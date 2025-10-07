import os
from typing import Tuple, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, PeftModel, PeftConfig, prepare_model_for_kbit_training, PeftModelForCausalLM
import json
try:
    # depending on your PEFT version, import the right loader
    from peft import PeftModel, PeftModelForCausalLM
    _has_peft = True
except Exception:
    _has_peft = False
from safeslm.config import DEFAULT_LORA_CONFIG

def load_base_model(model_name: str, precision: str = "full", device: str = "cpu"):
    """
    Load a HF causal model with desired precision.
    precision: "full", "8bit", "4bit"
    Returns (model, tokenizer).
    """
    precision = precision.lower()
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    # Ensure tokenizer has pad token
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "[PAD]"})
    device_map = "auto" if device != "cpu" else {"": "cpu"}
    load_kwargs = {"device_map": device_map}

    if precision == "4bit":
        print("[safeslm] Loading model in 4-bit (requires bitsandbytes)")
        model = AutoModelForCausalLM.from_pretrained(model_name, load_in_4bit=True, **load_kwargs)
        prepare_model_for_kbit_training(model)
    elif precision == "8bit":
        print("[safeslm] Loading model in 8-bit (requires bitsandbytes)")
        model = AutoModelForCausalLM.from_pretrained(model_name, load_in_8bit=True, **load_kwargs)
        prepare_model_for_kbit_training(model)
    else:
        print("[safeslm] Loading model in full precision (fp16 if GPU available)")
        model = AutoModelForCausalLM.from_pretrained(model_name, **load_kwargs)
        if device != "cpu":
            model = model.to(device)

    return model, tokenizer

def attach_lora(model, lora_config: Optional[dict] = None):
    """
    Wrap a model with a LoRA adapter (PEFT) and return the wrapped model.
    lora_config: dict matching keys in DEFAULT_LORA_CONFIG
    """
    cfg = DEFAULT_LORA_CONFIG.copy()
    if lora_config:
        cfg.update(lora_config)

    lora = LoraConfig(
        r=cfg["r"],
        lora_alpha=cfg["lora_alpha"],
        target_modules=cfg["target_modules"],
        lora_dropout=cfg["lora_dropout"],
        bias=cfg["bias"],
        task_type=cfg["task_type"]
    )
    peft_model = get_peft_model(model, lora)
    return peft_model

def save_lora(peft_model: PeftModel, out_dir: str):
    """
    Save LoRA adapter weights to out_dir (PEFT-friendly).
    """
    os.makedirs(out_dir, exist_ok=True)
    peft_model.save_pretrained(out_dir)
    print(f"[safeslm] LoRA adapter saved to {out_dir}")

# def load_lora(base_model, adapter_dir: str):
#     """
#     Load LoRA adapter onto base_model (returns a PeftModel wrapper).
#     """
#     if not os.path.isdir(adapter_dir):
#         raise FileNotFoundError(f"Adapter dir not found: {adapter_dir}")
#     peft_model = PeftModel.from_pretrained(base_model, adapter_dir, device_map="auto")
#     print(f"[safeslm] LoRA adapter loaded from {adapter_dir}")
#     return peft_model

def load_lora(base_model: str, lora_adapter_dir: str, device: str = "cpu", low_cpu_mem_usage: bool = False):
    """
    Loads tokenizer (from lora_adapter_dir), resizes base model embeddings if needed,
    then loads the PEFT/LoRA adapter onto the base model.

    Returns: (peft_model, tokenizer)
    """
    if not os.path.isdir(lora_adapter_dir):
        raise FileNotFoundError(f"{lora_adapter_dir} does not exist")

    # 1) load tokenizer from the adapter folder (fall back to base tokenizer if missing)
    try:
        tokenizer = AutoTokenizer.from_pretrained(lora_adapter_dir, use_fast=True)
        print(f"[safeslm] Loaded tokenizer from {lora_adapter_dir}")
    except Exception:
        print(f"[safeslm] Warning: tokenizer not found in {lora_adapter_dir};")

    tok_len = len(tokenizer)
    # 2) load base model
    # base = AutoModelForCausalLM.from_pretrained(base_model_name_or_path, low_cpu_mem_usage=low_cpu_mem_usage)
    base=base_model
    model_vocab_size = getattr(base.config, "vocab_size", None)
    print(f"[safeslm] base model vocab_size={model_vocab_size}, tokenizer length={tok_len}")

    # 3) if vocab size mismatch, resize embeddings BEFORE loading adapter
    if model_vocab_size is None or tok_len != model_vocab_size:
        print(f"[safeslm] Resizing base model embeddings {model_vocab_size} -> {tok_len}")
        base.resize_token_embeddings(tok_len)
    # 4) load the PEFT adapter onto base model
    if not _has_peft:
        raise RuntimeError("peft not installed; please pip install peft")

    # Use PeftModel.from_pretrained or PeftModelForCausalLM depending on your version
    try:
        peft_model = PeftModel.from_pretrained(base, lora_adapter_dir, is_trainable=False)
    except Exception:
        # fallback: some PEFT versions have PeftModelForCausalLM
        try:
            peft_model = PeftModelForCausalLM.from_pretrained(base, lora_adapter_dir, is_trainable=False)
        except Exception as e:
            raise RuntimeError(f"Failed to load PEFT model from {lora_adapter_dir}: {e}")

    peft_model.to(device)
    peft_model.eval()
    print("[safeslm] Loaded PEFT model and moved to device:", device)
    return peft_model, tokenizer