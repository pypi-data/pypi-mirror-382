"""
SafeSLM high-level class.

Usage:
    from safeslm import SafeSLM
    model = SafeSLM("gpt2", task="safety", precision="8bit", device="cuda")
    out = model.prompt("Hello world", max_new_tokens=64)
"""

from typing import Optional, Any
import torch
import os

# your internal helpers - adjust imports to your package structure
from safeslm.modeling import load_base_model, load_lora
from safeslm.routing import make_default_router
from semantic_router.encoders import FastEmbedEncoder
from safeslm.pipeline import SafeSLMPipeline
from safeslm.trainer import fine_tune_dpo_lora
from safeslm.config import HF_DEFAULT_DATASET

class SafeSLM:
    def __init__(
        self,
        model_name: str,
        task: str = "default",
        precision: str = "full",  # "full", "8bit", "4bit"
        device: Optional[str] = None,  # "cpu" or "cuda"
        adapter_path: Optional[str] = None,
        router: Optional[Any] = None,
        encoder_name: str = "BAAI/bge-small-en-v1.5",
        **kwargs,
    ):
        """
        High-level wrapper for model + tokenizer, optional LoRA adapter, and pipeline.

        Args:
            model_name: HuggingFace model id (or path).
            task: high-level task label (informational).
            precision: 'full' | '8bit' | '4bit'
            device: 'cpu' | 'cuda' | None (auto-detect)
            adapter_path: path to a saved LoRA adapter (optional)
            router: optional router instance (if you already have one)
            encoder_name: encoder name for default router if router not given
            kwargs: passed onto lower-level loader if needed
        """
        # resolve device
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.model_name = model_name
        self.task = task
        self.precision = precision
        self.adapter_path = adapter_path

        # load base model + tokenizer using your implementation
        self.base_model, self.tokenizer = load_base_model(model_name, precision, device=self.device, **kwargs)

        # attempt to load LoRA if given
        self.lora_model = None
        if adapter_path:
            try:
                self.lora_model, self.tokenizer = load_lora(self.base_model, adapter_path, device=self.device)
            except Exception as e:
                # don't crash; warn
                print(f"[safeslm] warning: could not load adapter from {adapter_path}: {e}")

        # router: allow injection for testing; otherwise create default
        if router is None:
            encoder = FastEmbedEncoder(name=encoder_name)
            router = make_default_router(encoder,self.task)
        self.router = router

        # pipeline wraps model/tokenizer/router and can take lora model
        self.pipeline = SafeSLMPipeline(
            base_model=self.base_model,
            tokenizer=self.tokenizer,
            router=self.router,
            lora_model=self.lora_model,
            device=self.device,
            task=self.task
        )

    def prompt(self, text: str, max_new_tokens: int = 128,task: Optional[str] = None, **generate_kwargs) -> str:
        """Run a single prompt through the pipeline and return text."""

        effective_task = task or self.task
        out = self.pipeline.run(prompt=text,task= effective_task, max_new_tokens=max_new_tokens, **generate_kwargs)
        return out

    # make instance callable: model("my prompt")
    __call__ = prompt

    # training helper that uses existing trainer helper
    def train(
        self,
        output_dir: str,
        dataset_name: Optional[str] = HF_DEFAULT_DATASET,
        num_train_epochs: int = 1,
        per_device_train_batch_size: int = 8,
        **trainer_kwargs,
    ):
        """Fine-tune a LoRA adapter using your trainer utility.

        Saves adapter to output_dir (expected behavior from trainer).
        """
        fine_tune_dpo_lora(
            base_model=self.base_model,
            tokenizer=self.tokenizer,
            output_dir=output_dir,
            dataset_name=dataset_name,
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=per_device_train_batch_size,
            device=self.device,
            **trainer_kwargs,
        )
        # try to reload adapter into this instance
        adapter_path = os.path.join(output_dir, "lora_adapter")
        if os.path.isdir(adapter_path):
            try:
                self.lora_model, self.tokenizer = load_lora(self.base_model, adapter_path, device=self.device)
                self.pipeline.lora_model = self.lora_model
                print(f"[safeslm] loaded trained adapter from {adapter_path}")
            except Exception as e:
                print(f"[safeslm] training finished but failed to load adapter: {e}")

    def save(self, dirpath: str):
        """Optional helper to save any metadata you want (tokenizer, adapter pointer, config)."""
        os.makedirs(dirpath, exist_ok=True)
        # Example: save a tiny metadata file
        metadata = {
            "model_name": self.model_name,
            "task": self.task,
            "precision": self.precision,
            "adapter": bool(self.lora_model),
        }
        import json
        with open(os.path.join(dirpath, "safeslm_meta.json"), "w") as f:
            json.dump(metadata, f, indent=2)

    @classmethod
    def from_config(cls, config: dict):
        """Optional convenience constructor from config dict."""
        return cls(**config)
