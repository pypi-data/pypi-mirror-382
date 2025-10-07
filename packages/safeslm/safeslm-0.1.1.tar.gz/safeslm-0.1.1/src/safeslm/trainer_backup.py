import os
from typing import Optional, Dict
import re
import torch
from datasets import load_dataset
from transformers import TrainingArguments
from transformers.data.data_collator import DataCollatorForLanguageModeling

# keep your safeslm helpers
from safeslm.modeling import attach_lora, save_lora
from safeslm.config import HF_DEFAULT_DATASET
from safeslm.utils import infer_lora_target_modules, debug_list_model_param_names

from trl import DPOTrainer, DPOConfig
import trl as _trl  # for version print

def _get_tokenizer_vocab_size(tokenizer):
    # robustly determine tokenizer vocab size
    try:
        return len(tokenizer)
    except Exception:
        vs = getattr(tokenizer, "vocab_size", None)
        if vs is not None:
            return vs
        # fallback: try get_vocab()
        try:
            return len(tokenizer.get_vocab())
        except Exception:
            return None

def _sample_and_check_dataset_token_ids(ds, tokenizer, model_vocab_size, chosen_col="chosen", rejected_col="rejected", n_sample=200):
    """
    Tokenize first n_sample rows with tokenizer (without padding/truncation)
    and check min/max token id ranges. Returns list of bad rows found.
    Works with datasets.Dataset where ds[i] returns a dict.
    """
    bad = []
    sample_n = min(n_sample, len(ds))
    for i in range(sample_n):
        row = ds[i]  # row is a dict-like object
        # prefer the requested column if present, else fallback to "chosen"/"rejected"
        chosen_text_or_ids = row.get(chosen_col) if chosen_col in row else row.get("chosen")
        rejected_text_or_ids = row.get(rejected_col) if rejected_col in row else row.get("rejected")

        # Normalize chosen -> list of token ids (if it's a raw string, tokenize it)
        if isinstance(chosen_text_or_ids, str):
            ids_ch = tokenizer(chosen_text_or_ids, truncation=False, padding=False)["input_ids"]
        elif isinstance(chosen_text_or_ids, (list, tuple)):
            # assume already token ids
            ids_ch = list(chosen_text_or_ids)
        else:
            ids_ch = []

        # Normalize rejected -> list of token ids
        if isinstance(rejected_text_or_ids, str):
            ids_re = tokenizer(rejected_text_or_ids, truncation=False, padding=False)["input_ids"]
        elif isinstance(rejected_text_or_ids, (list, tuple)):
            ids_re = list(rejected_text_or_ids)
        else:
            ids_re = []

        # Also check common pre-tokenized fields if present
        # (some datasets include input_ids/input_ids_chosen/input_ids_rejected)
        if not ids_ch:
            for key in ("input_ids_chosen", "input_ids", "input_ids_chosen"):
                if key in row and isinstance(row[key], (list, tuple)):
                    ids_ch = list(row[key]); break
        if not ids_re:
            for key in ("input_ids_rejected", "input_ids", "input_ids_rejected"):
                if key in row and isinstance(row[key], (list, tuple)):
                    ids_re = list(row[key]); break

        # Inspect ids
        for which, ids in (("chosen", ids_ch), ("rejected", ids_re)):
            if not ids:
                continue
            mn = min(ids)
            mx = max(ids)
            if mn < 0 or (model_vocab_size is not None and mx >= model_vocab_size):
                bad.append({"row": i, "which": which, "min": mn, "max": mx, "sample_ids": ids[:10]})
    return bad

def prepare_lora_config_for_model(model, base_lora_config: dict) -> dict:
    lora_cfg = dict(base_lora_config) if base_lora_config is not None else {}
    user_targets = lora_cfg.get("target_modules", None)

    # If user passed targets and they exist in model, keep them
    if user_targets:
        # quick check if any of the requested substrings appear in model state_dict keys
        sd = " ".join(list(model.state_dict().keys())[:2000])
        found_any = any(re.search(r"(^|[\._])" + re.escape(t) + r"($|[\._])", sd) for t in user_targets)
        if found_any:
            return lora_cfg
        else:
            print("[safeslm] WARNING: requested LoRA target_modules {} not found in model; inferring automatically.".format(user_targets))

    # infer
    inferred = infer_lora_target_modules(model)
    if not inferred:
        print("[safeslm] ERROR: could not infer LoRA target modules automatically.")
        debug_list_model_param_names(model, max_lines=80)
        raise RuntimeError(
            "No candidate attention projection module names found. "
            "Please inspect model parameter names and pass `target_modules` in lora_config manually."
        )

    # set inferred targets (you can also merge with user list)
    lora_cfg["target_modules"] = inferred
    print(f"[safeslm] Using inferred LoRA target_modules: {inferred}")
    return lora_cfg


def fine_tune_dpo_lora(
    base_model,
    tokenizer,
    output_dir: str,
    dataset_name: str = HF_DEFAULT_DATASET,
    dataset_split: str = "train",
    num_train_epochs: int = 1,
    per_device_train_batch_size: int = 4,
    max_length: int = 512,
    learning_rate: float = 2e-5,
    lora_config: Optional[Dict] = None,
    logging_steps: int = 50,
    save_total_limit: int = 2,
    push_to_hub: bool = False,
):
    """
    Fine-tune a LoRA adapter using TRL's DPOTrainer on a dataset containing
    'chosen' and 'rejected' fields.
    """
    print("[safeslm] trl version:", getattr(_trl, "__version__", "unknown"))

    # Ensure pad token exists
    if getattr(tokenizer, "pad_token_id", None) is None:
        if getattr(tokenizer, "eos_token_id", None) is not None:
            tokenizer.pad_token = tokenizer.eos_token
            print(f"[safeslm] tokenizer.pad_token was None — set pad_token to eos_token (id={tokenizer.pad_token_id})")
        else:
            tokenizer.add_special_tokens({"pad_token": "<|pad|>"})
            print("[safeslm] tokenizer.pad_token was None and no eos_token; added a pad token <|pad|>")

    # Determine tokenizer vocab size
    tok_vocab_size = _get_tokenizer_vocab_size(tokenizer)
    model_vocab_size = getattr(base_model.config, "vocab_size", None)
    print(f"[safeslm] tokenizer vocab size (est): {tok_vocab_size}, model.config.vocab_size: {model_vocab_size}")

    # If tokenizer has bigger vocab than model embeddings — resize first (before attaching LoRA)
    if tok_vocab_size is not None and model_vocab_size is not None and tok_vocab_size > model_vocab_size:
        print(f"[safeslm] Resizing model embeddings: {model_vocab_size} -> {tok_vocab_size}")
        base_model.resize_token_embeddings(tok_vocab_size)
        model_vocab_size = getattr(base_model.config, "vocab_size", tok_vocab_size)

    # Load dataset for sanity check
    print(f"[safeslm] Loading dataset {dataset_name} (split={dataset_split}) for quick sanity check")
    ds = load_dataset(dataset_name, split=dataset_split)
    print(f"[safeslm] Dataset loaded, num examples: {len(ds)}. Columns: {ds.column_names}")


    # Take only 5% of the dataset
    frac = 0.02
    subset_len = max(1, int(len(ds) * frac))
    ds = ds.select(range(subset_len))
    print(f"[safeslm] Using only 5% of dataset, num examples: {len(ds)}")



    # Basic check for chosen/rejected columns
    if not ("chosen" in ds.column_names and "rejected" in ds.column_names):
        raise ValueError("Dataset must have 'chosen' and 'rejected' text columns for DPO.")

    # Run sampling check (uses the fixed helper above)
    bad_rows = _sample_and_check_dataset_token_ids(ds, tokenizer, model_vocab_size, n_sample=200)
    if bad_rows:
        print("[safeslm] ERROR: Found token ids outside model vocab range or negative in sample rows:")
        for b in bad_rows[:20]:
            print("  -", b)
        raise RuntimeError(
            "Token ids in dataset are outside the model's embedding range. "
            "Possible causes:\n"
            " - You tokenized with a different tokenizer than the model expects.\n"
            " - The dataset contains pre-tokenized ids from another vocab.\n"
            "Fixes:\n"
            " - Ensure you use tokenizer.from_pretrained(the same model name) for tokenization.\n"
            " - Or call model.resize_token_embeddings(len(tokenizer)) before training.\n"
        )

    # Attach LoRA (after any resize)
    lora_config = prepare_lora_config_for_model(base_model, lora_config)
    peft_model = attach_lora(base_model, lora_config=lora_config)

    # Build DPOConfig and trainer (trl v0.23.0 pattern)
    pad_val = getattr(tokenizer, "pad_token_id", None) or getattr(tokenizer, "eos_token_id", 0)
    dpoconf_kwargs = dict(
        output_dir=output_dir,
        per_device_train_batch_size=per_device_train_batch_size,
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
        fp16=torch.cuda.is_available(),
        save_total_limit=save_total_limit,
        logging_steps=logging_steps,
        remove_unused_columns=False,
        push_to_hub=push_to_hub,
        padding_value=pad_val,
    )
    training_args = DPOConfig(**dpoconf_kwargs)

    trainer = DPOTrainer(
        model=peft_model,
        args=training_args,
        processing_class=tokenizer,
        train_dataset=ds,
        data_collator=None,
    )

    print("[safeslm] Starting DPO LoRA training (training only adapter params)")
    trainer.train()

    # Save LoRA adapter
    lora_out = os.path.join(output_dir, "lora_adapter")
    save_lora(peft_model, lora_out)
    print(f"[safeslm] LoRA adapter saved to: {lora_out}")

    try:
        trainer.save_model(os.path.join(output_dir, "checkpoint-final"))
    except Exception:
        pass

    return peft_model