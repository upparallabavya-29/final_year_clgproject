"""
data/transforms.py — Image augmentation pipelines for training and validation.
"""
from torchvision import transforms


def get_train_transforms(img_size: int = 224) -> transforms.Compose:
    """
    Aggressive augmentation for training — helps regularise and prevent overfitting
    on PlantVillage which is a clean lab-photo dataset.
    """
    return transforms.Compose([
        transforms.Resize((img_size + 32, img_size + 32)),  # slightly larger for random crop
        transforms.RandomCrop(img_size),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.RandomRotation(degrees=30),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
        transforms.RandomGrayscale(p=0.05),
        transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def get_val_transforms(img_size: int = 224) -> transforms.Compose:
    """Standard centre-crop for validation and test — no randomisation."""
    return transforms.Compose([
        transforms.Resize((img_size + 16, img_size + 16)),
        transforms.CenterCrop(img_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def get_inference_transforms(img_size: int = 224) -> transforms.Compose:
    """
    Transform for single-image inference in app.py — identical to val_transforms
    so inference is consistent with validation accuracy.
    Exported here as the single source of truth.
    """
    return get_val_transforms(img_size=img_size)
