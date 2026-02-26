"""
train.py — Train ViT or Swin Transformer on the PlantVillage dataset.

Usage:
    # Download dataset first (one-time):
    python download_data.py

    # Then train:
    python train.py --model vit   --data_dir dataset --epochs 30
    python train.py --model swin  --data_dir dataset --epochs 30 --batch_size 16

    # Quick smoke-test (1 batch per epoch):
    python train.py --model vit --data_dir dataset --dry_run
"""

import argparse
import os
import sys
import time
import json

import torch
import torch.nn as nn
import torch.optim as optim
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


# ── Training helpers ──────────────────────────────────────────────────────────

def train_epoch(model, loader, criterion, optimizer, device, scaler=None):
    model.train()
    running_loss = 0.0
    all_preds, all_targets = [], []

    pbar = tqdm(loader, desc="Training", leave=False)
    for images, labels in pbar:
        images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)

        optimizer.zero_grad()

        if scaler:  # AMP (mixed precision)
            with torch.cuda.amp.autocast():
                outputs = model(images)
                loss    = criterion(outputs, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss    = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

        running_loss += loss.item() * images.size(0)
        all_preds.append(outputs.detach().cpu())
        all_targets.append(labels.detach().cpu())
        pbar.set_postfix({"loss": f"{loss.item():.4f}"})

    epoch_loss = running_loss / len(loader.dataset)
    metrics = calculate_metrics(torch.cat(all_targets), torch.cat(all_preds))
    metrics["loss"] = epoch_loss
    return metrics


def validate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds, all_targets = [], []

    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Validation", leave=False):
            images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
            outputs = model(images)
            loss    = criterion(outputs, labels)
            running_loss += loss.item() * images.size(0)
            all_preds.append(outputs.cpu())
            all_targets.append(labels.cpu())

    epoch_loss = running_loss / len(loader.dataset)
    metrics = calculate_metrics(torch.cat(all_targets), torch.cat(all_preds))
    metrics["loss"] = epoch_loss
    return metrics


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CropGuard AI — Training")
    parser.add_argument("--data_dir",      type=str, default="dataset",  help="Path to PlantVillage dataset")
    parser.add_argument("--model",         type=str, choices=["vit", "swin"], default="vit")
    parser.add_argument("--epochs",        type=int, default=30)
    parser.add_argument("--batch_size",    type=int, default=32)
    parser.add_argument("--lr",            type=float, default=1e-4)
    parser.add_argument("--img_size",      type=int, default=224)
    parser.add_argument("--num_workers",   type=int, default=2)
    parser.add_argument("--checkpoint_dir",type=str, default="checkpoints")
    parser.add_argument("--resume",        type=str, default=None, help="Path to checkpoint to resume from")
    parser.add_argument("--amp",           action="store_true", help="Use Automatic Mixed Precision (GPU only)")
    parser.add_argument("--dry_run",       action="store_true", help="Single-batch smoke test")
    parser.add_argument("--download",      action="store_true", help="Download dataset before training")
    args = parser.parse_args()

    # ── Optional auto-download ──
    if args.download:
        from download_data import download_plantvillage
        download_plantvillage(out_dir=args.data_dir)

    # ── Device ──
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if args.amp and not torch.cuda.is_available():
        print("Warning: --amp requested but no CUDA. Disabling AMP.")
        args.amp = False

    # ── Data ──
    print("Loading data …")
    train_loader, val_loader, test_loader, class_names = get_dataloaders(
        args.data_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        img_size=args.img_size,
    )
    num_classes = len(class_names)
    print(f"Classes detected: {num_classes}  ({class_names[:5]} …)")

    # Persist class list alongside checkpoint
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    class_index_path = os.path.join(args.checkpoint_dir, "class_names.json")
    with open(class_index_path, "w") as f:
        json.dump(class_names, f, indent=2)
    print(f"Class names saved → {class_index_path}")

    # ── Model ──
    print(f"Initialising {args.model.upper()} model ({num_classes} classes) …")
    if args.model == "vit":
        model = get_vit_model(num_classes=num_classes)
    else:
        model = get_swin_model(num_classes=num_classes)

    if model is None:
        print("ERROR: Failed to initialise model. Exiting.")
        sys.exit(1)

    if args.resume and os.path.isfile(args.resume):
        print(f"Resuming from checkpoint: {args.resume}")
        model.load_state_dict(torch.load(args.resume, map_location="cpu"))

    model = model.to(device)
    if torch.cuda.device_count() > 1:
        model = nn.DataParallel(model)

    # ── Optimiser & scheduler ──
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler    = torch.cuda.amp.GradScaler() if args.amp else None

    # ── Training loop ──
    best_acc  = 0.0
    n_epochs  = 1 if args.dry_run else args.epochs
    history   = []

    for epoch in range(n_epochs):
        t0 = time.time()
        print(f"\nEpoch {epoch+1}/{n_epochs}  (lr={scheduler.get_last_lr()[0]:.2e})")

        train_m = train_epoch(model, train_loader, criterion, optimizer, device, scaler)
        val_m   = validate(model, val_loader, criterion, device)
        scheduler.step()

        elapsed = time.time() - t0
        print(f"  Train  loss={train_m['loss']:.4f}  acc={train_m['accuracy']:.4f}")
        print(f"  Val    loss={val_m['loss']:.4f}  acc={val_m['accuracy']:.4f}  "
              f"f1={val_m['f1']:.4f}  [{elapsed:.0f}s]")

        history.append({"epoch": epoch + 1, "train": train_m, "val": val_m})

        if val_m["accuracy"] > best_acc:
            best_acc  = val_m["accuracy"]
            save_path = os.path.join(args.checkpoint_dir, f"best_model_{args.model}.pth")
            state     = model.module.state_dict() if isinstance(model, nn.DataParallel) else model.state_dict()
            torch.save(state, save_path)
            print(f"  ✅ New best model saved → {save_path}  (acc={best_acc:.4f})")

        if args.dry_run:
            print("Dry run complete.")
            break

    # ── Save training history ──
    hist_path = os.path.join(args.checkpoint_dir, f"history_{args.model}.json")
    with open(hist_path, "w") as f:
        json.dump(history, f, indent=2, default=float)
    print(f"\nTraining history saved → {hist_path}")
    print(f"Best validation accuracy: {best_acc:.4f}")


if __name__ == "__main__":
    main()
