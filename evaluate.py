"""
evaluate.py — Evaluate a trained model on the test split of the PlantVillage dataset.

Usage:
    python evaluate.py --model vit  --data_dir dataset
    python evaluate.py --model swin --data_dir dataset --checkpoint checkpoints/best_model_swin.pth
"""

import argparse
import os
import sys
import json

import torch
import torch.nn.functional as F
from tqdm import tqdm

from data.dataset import get_dataloaders
from models import get_vit_model, get_swin_model
from utils.metrics import calculate_metrics

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def evaluate_model(model, loader, device, class_names):
    model.eval()
    all_preds, all_targets = [], []
    all_probs = []

    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Evaluating"):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            probs   = F.softmax(outputs, dim=-1)
            all_preds.append(outputs.cpu())
            all_targets.append(labels.cpu())
            all_probs.append(probs.cpu())

    all_preds   = torch.cat(all_preds)
    all_targets = torch.cat(all_targets)
    all_probs   = torch.cat(all_probs)

    metrics = calculate_metrics(all_targets, all_preds)

    # Per-class accuracy
    pred_labels = all_preds.argmax(dim=1)
    per_class   = {}
    for cls_idx, cls_name in enumerate(class_names):
        mask = (all_targets == cls_idx)
        if mask.sum() == 0:
            per_class[cls_name] = None
        else:
            per_class[cls_name] = float((pred_labels[mask] == cls_idx).float().mean())

    return metrics, per_class


def main():
    parser = argparse.ArgumentParser(description="CropGuard AI — Evaluation")
    parser.add_argument("--data_dir",    type=str, default="dataset",   help="Path to PlantVillage dataset")
    parser.add_argument("--model",       type=str, choices=["vit", "swin"], default="vit")
    parser.add_argument("--checkpoint",  type=str, default=None,        help="Path to .pth weights (auto-detected if not set)")
    parser.add_argument("--batch_size",  type=int, default=32)
    parser.add_argument("--img_size",    type=int, default=224)
    parser.add_argument("--num_workers", type=int, default=2)
    parser.add_argument("--out_dir",     type=str, default="eval_results")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # ── Data ──
    print("Loading dataset …")
    _, _, test_loader, class_names = get_dataloaders(
        args.data_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        img_size=args.img_size,
    )
    num_classes = len(class_names)
    print(f"Evaluating on {len(test_loader.dataset):,} test images | {num_classes} classes")

    # ── Model ──
    if args.model == "vit":
        model = get_vit_model(num_classes=num_classes)
    else:
        model = get_swin_model(num_classes=num_classes)

    if model is None:
        print("ERROR: Could not initialise model.")
        sys.exit(1)

    # Resolve checkpoint path
    ckpt_path = args.checkpoint or os.path.join("checkpoints", f"best_model_{args.model}.pth")
    if not os.path.isfile(ckpt_path):
        print(f"ERROR: Checkpoint not found: {ckpt_path}")
        print("Train first: python train.py --model vit --data_dir dataset")
        sys.exit(1)

    print(f"Loading weights: {ckpt_path}")
    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    model = model.to(device)

    # ── Evaluate ──
    metrics, per_class = evaluate_model(model, test_loader, device, class_names)

    print(f"\n{'='*50}")
    print(f"  Model       : {args.model.upper()}")
    print(f"  Accuracy    : {metrics['accuracy']*100:.2f}%")
    print(f"  F1-score    : {metrics['f1']:.4f}")
    print(f"{'='*50}")

    # Per-class breakdown (top-5 worst)
    valid_pc = {k: v for k, v in per_class.items() if v is not None}
    worst5   = sorted(valid_pc, key=lambda k: valid_pc[k])[:5]
    print("\nBottom-5 classes by accuracy:")
    for cls in worst5:
        print(f"  {cls:<55} {valid_pc[cls]*100:.1f}%")

    # Save results
    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(args.out_dir, f"eval_{args.model}.json")
    result = {
        "model":      args.model,
        "checkpoint": ckpt_path,
        "dataset":    args.data_dir,
        "metrics":    {k: float(v) for k, v in metrics.items()},
        "per_class":  {k: (float(v) if v is not None else None) for k, v in per_class.items()},
    }
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nFull results saved → {out_path}")


if __name__ == "__main__":
    main()
