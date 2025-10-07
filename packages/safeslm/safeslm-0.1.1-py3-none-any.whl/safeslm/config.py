DEFAULT_LORA_CONFIG = {
    "r": 8,
    "lora_alpha": 32,
    "lora_dropout": 0.1,
    "target_modules": ["q_proj", "v_proj"],  # good default for many causal models
    "bias": "none",
    "task_type": "CAUSAL_LM"
}

# Default dataset to fine-tune LoRA (you requested anthopic/hh-rlhf)
HF_DEFAULT_DATASET = "Anthropic/hh-rlhf"
