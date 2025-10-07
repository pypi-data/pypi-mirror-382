from typing import Optional
import torch
from transformers import GenerationConfig

from safeslm.routing import make_default_router

BLOCK_MESSAGE = "⚠️ Content blocked due to safety concerns."

def generate_text(model, tokenizer, prompt: str, max_new_tokens: int = 128, generation_kwargs=None, device: str = "cpu"):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    # Move to model device
    device_torch = torch.device(device)
    inputs = {k: v.to(device_torch) for k, v in inputs.items()}
    model = model.to(device_torch)

    gen_conf = GenerationConfig()
    kwargs = {"max_new_tokens": max_new_tokens}
    if generation_kwargs:
        kwargs.update(generation_kwargs)

    outputs = model.generate(**inputs, **kwargs)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text

class SafeSLMPipeline:
    def __init__(self, base_model, tokenizer, router=None, lora_model=None, device: str = "cpu", task: str = "default"):
        self.base_model = base_model.to(device)
        self.lora_model = lora_model.to(device) if lora_model else None
        self.tokenizer = tokenizer
        self.router = router or make_default_router()
        self.device = device
        self.task = task  # store default task


    def run(self, prompt: str, max_new_tokens: int = 128,task: Optional[str] = None, generation_kwargs=None) -> str:
        # First routing: classify prompt

        effective_task = task or self.task
        route = self.router(prompt)
        route_name = route.name if route else "safe"

        if route_name == "safe":
            # use base model
            response = generate_text(self.base_model, self.tokenizer, prompt, max_new_tokens, generation_kwargs, self.device)
        else:
            print("[safeslm] Warning: Unsafe Prompt - Using LoRA Adapters")
            # use LoRA-adapted model (if not present, attach and warn)
            if self.lora_model is None:
                # fall back to base model if no adapter present (or raise)
                print("[safeslm] Warning: no LoRA adapter loaded - using base model")
                response = generate_text(self.base_model, self.tokenizer, prompt, max_new_tokens, generation_kwargs, self.device)
            else:
                response = generate_text(self.lora_model, self.tokenizer, prompt, max_new_tokens, generation_kwargs, self.device)

        return response
            
