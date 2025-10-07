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

    - base_model: huggingface model (e.g., AutoModelForCausalLM) already loaded
    - tokenizer: corresponding tokenizer
    - dataset_name: HF dataset id or local path; dataset must have "chosen" and "rejected"
    - This function trains ONLY the LoRA/adapter parameters (base weights remain unchanged)
    """
    print("[safeslm] trl version:", getattr(_trl, "__version__", "unknown"))
    # 1) attach LoRA (PEFT) to the base model
    lora_config = prepare_lora_config_for_model(base_model, lora_config)
    peft_model = attach_lora(base_model, lora_config=lora_config)

    # 2) load dataset
    print(f"[safeslm] Loading dataset {dataset_name} (split={dataset_split})")
    ds = load_dataset(dataset_name, split=dataset_split)
    print(f"[safeslm] Dataset loaded, num examples: {len(ds)}")

    # sanity check: ensure 'chosen' and 'rejected' exist
    if not ("chosen" in ds.column_names and "rejected" in ds.column_names):
        raise ValueError("Dataset must have 'chosen' and 'rejected' text columns for DPO.")

    # 3) Build DPOConfig (trl v0.23.0 uses DPOConfig)
    pad_val = getattr(tokenizer, "pad_token_id", None)
    if pad_val is None:
        # prefer eos_token as pad if pad_token missing
        pad_val = getattr(tokenizer, "eos_token_id", 0)
        print(f"[safeslm] tokenizer.pad_token_id is None, falling back to eos_token_id / 0 -> {pad_val}")

    from transformers.tokenization_utils_base import BatchEncoding
    from dataclasses import dataclass
    from typing import List



    # 5) prepare training arguments
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
        padding_value=pad_val,  # important for older/newer DPO API
        # you can add other DPOConfig-specific fields, e.g. loss_type, beta, etc.
    )
    training_args = DPOConfig(**dpoconf_kwargs)

    # 6) instantiate DPO trainer
    # TRL's DPOTrainer accepts similar args to other trainers: model, args, train_dataset, tokenizer, etc.
    trainer = DPOTrainer(
        model=peft_model,
        args=training_args,
        processing_class=tokenizer,   # <- important for v0.23.0 examples in docs
        train_dataset=ds,
        data_collator=None,
    )

    # 7) train
    print("[safeslm] Starting DPO LoRA training (training only adapter params)")
    trainer.train()

    # 8) save LoRA adapter weights (keeps base model intact)
    lora_out = os.path.join(output_dir, "lora_adapter")
    save_lora(peft_model, lora_out)
    print(f"[safeslm] LoRA adapter saved to: {lora_out}")

    # Optionally save final trainer checkpoint if desired (kept small by save_total_limit)
    try:
        trainer.save_model(os.path.join(output_dir, "checkpoint-final"))
        print(f"[safeslm] Full trainer checkpoint saved to: {os.path.join(output_dir, 'checkpoint-final')}")
    except Exception:
        # Not critical — we already saved adapter
        pass

    return peft_model
