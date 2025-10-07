# SafeSLM

**SafeSLM** is a Python library designed to make **small language models (SLMs)** safer for deployment by fine-tuning them on safety datasets using LoRA adapters. It provides an easy-to-use class-based API and CLI for training, loading, and inference while keeping safety-related logic separate from reasoning or other tasks.

---

## Motivation

Small language models, because they contain far fewer parameters, tend to memorize less context. This makes them more **vulnerable to simple prompt-based jailbreaks**. Large language models, on the other hand, have more weights and capacity, which allows them to:

* Detect malicious prompt manipulations
* Resist unsafe instructions
* Maintain high accuracy on legitimate tasks

However, SLMs perform best when focused on a **single task**. Forcing an SLM to perform multiple tasks—such as safety enforcement and reasoning—can degrade its performance.

**SafeSLM’s approach**:

* Keep tasks separate by training small models specifically for **safety detection**.
* For a given task, the model considers **all related prompts safe** and others unsafe.
* LoRA adapters allow fine-tuning safety behavior **without modifying the base model**, preserving the original weights.

---

## Features

* Fine-tune small language models on safety datasets using **LoRA adapters**
* Simple class-based Python API for training and inference
* CLI for reproducible training and inference pipelines
* Supports multiple adapters for the same base model
* Keeps tasks separate to avoid degrading reasoning or other capabilities
* Flexible precision: full, 8-bit, or 4-bit
* Supports custom HuggingFace datasets
* Task-specific inference with a `task` argument

---

## Installation

```bash
# First install semantic-router for routing functionality
!pip install -qU "semantic-router[fastembed]==0.1.0"

# Install SafeSLM
pip install safeslm
```

> **Note:** If you are on Google Colab, restart your session after installation.

---

## Usage

### Python API

```python
from safeslm import SafeSLM

# Train a new LoRA adapter on safety data
model = SafeSLM("gpt2", precision="full", device="cuda")
model.train(
    output_dir="./adapter_out",
    dataset_name="your_dataset_name_here",  # optional, defaults to Anthropic/hh-rlhf
    num_train_epochs=5,
    per_device_train_batch_size=4
)

# Load the adapter for inference
safe_model = SafeSLM(
    "gpt2",
    precision="full",
    device="cuda",
    adapter_path="./adapter_out/lora_adapter"
)

# Run prompts with a task (currently supports:"default","coding","content_creation","education",)
output = safe_model("Is it safe to share my password online?", task="default")
print(output)
```

### CLI

```bash
# Train LoRA adapter
safeslm train --model gpt2 --out_dir ./adapter_out --dataset your_dataset_name_here --epochs 5 --batch_size 4 --precision full --device cuda

# Run inference
safeslm infer --model gpt2 --adapter ./adapter_out/lora_adapter --prompt "What are safe browsing practices?" --task default --precision full --device cuda
```

---

## Multi-Adapter Support

You can train multiple LoRA adapters on different safety datasets or domains and switch between them without reloading the base model:

```python
# Load adapter A
adapter_a = SafeSLM("gpt2", adapter_path="./adapters/safety_v1/lora_adapter")

# Load adapter B
adapter_b = SafeSLM("gpt2", adapter_path="./adapters/safety_v2/lora_adapter")

# Run inference on both
print(adapter_a("Some potentially unsafe prompt", task="safety"))
print(adapter_b("Some potentially unsafe prompt", task="safety"))
```

---

## Pipeline Overview

The SafeSLM pipeline consists of:

1. **Base Model Loading** – Load the HuggingFace model in desired precision.
2. **Optional LoRA Adapter** – Fine-tuned weights for safety, loaded separately.
3. **Router & Encoder** – Encodes prompts for safety classification or routing.
4. **Pipeline Execution** – Handles prompt routing, LoRA injection, and generation.

<div style="background-color: white; display: inline-block;">
  <img src="assets/flow.png" alt="Flowchart">
</div>

---

## Why SafeSLM?

* **Task separation** ensures small models remain accurate for their intended purpose.
* **LoRA adapters** allow multiple safety profiles on the same base model.
* **Easy integration** via class-based API or CLI.
* **Supports multiple precisions** for faster inference on limited hardware.
* **Supports custom datasets** for training on your own data.
* **Task-aware inference** using the `task` argument.

---

## Contributing

Contributions are welcome! Please submit issues or pull requests.
For major changes, open a discussion first.

---

## License

[MIT License](LICENSE)
