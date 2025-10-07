#!/usr/bin/env python3
import argparse
from safeslm import SafeSLM

def main():
    parser = argparse.ArgumentParser(prog="safeslm", description="SafesLM CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    train_p = sub.add_parser("train", help="Fine-tune LoRA on safety dataset")
    train_p.add_argument("--model", required=True, help="HuggingFace model id")
    train_p.add_argument("--out_dir", required=True, help="Directory to save adapter")
    train_p.add_argument("--epochs", type=int, default=1)
    train_p.add_argument("--batch_size", type=int, default=8)
    train_p.add_argument("--precision", default="full", choices=["full","8bit","4bit"])
    train_p.add_argument("--device", default=None)
    train_p.add_argument("--dataset_name", help="Name of the dataset for training")


    infer_p = sub.add_parser("infer", help="Run prompt through safeslm pipeline")
    infer_p.add_argument("--model", required=True, help="HuggingFace model id")
    infer_p.add_argument("--prompt", required=True, help="Prompt for the model")
    infer_p.add_argument("--adapter", default=None, help="Path to LoRA adapter (optional)")
    infer_p.add_argument("--max_new_tokens", type=int, default=128)
    infer_p.add_argument("--precision", default="full", choices=["full","8bit","4bit"])
    infer_p.add_argument("--device", default=None)
    infer_p.add_argument("--task", default="default", help="High-level task label")

    args = parser.parse_args()

    if args.cmd == "train":
        client = SafeSLM(args.model, precision=args.precision, device=args.device)
        client.train(output_dir=args.out_dir,dataset_name=args.dataset_name, num_train_epochs=args.epochs, per_device_train_batch_size=args.batch_size)

    elif args.cmd == "infer":
        client = SafeSLM(args.model, precision=args.precision, device=args.device, adapter_path=args.adapter)
        out = client.prompt(args.prompt, max_new_tokens=args.max_new_tokens,task=args.task)
        print("=== OUTPUT ===")
        print(out)

if __name__ == "__main__":
    main()
