import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from torch import nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.utils.data import DataLoader, WeightedRandomSampler
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

from dataset import ID2LABEL, LABEL2ID, create_dataset_from_dataframe, prepare_stance_dataframe

MODEL_NAME = "indobenchmark/indobert-base-p1"


def load_dataframe(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError(f"File '{csv_path}' contains no rows.")
    return df


def build_dataloaders(
    df: pd.DataFrame,
    tokenizer: AutoTokenizer,
    train_batch_size: int,
    eval_batch_size: int,
    max_length: int,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> Tuple[DataLoader, DataLoader, np.ndarray, pd.DataFrame]:
    df = prepare_stance_dataframe(df)
    if df.empty:
        raise ValueError("No valid rows for training after preprocessing.")

    train_df, val_df = train_test_split(
        df,
        test_size=val_ratio,
        stratify=df["label_id"],
        random_state=seed,
    )

    train_dataset = create_dataset_from_dataframe(tokenizer, train_df, max_length=max_length)
    val_dataset = create_dataset_from_dataframe(tokenizer, val_df, max_length=max_length)

    class_counts = train_df["label_id"].value_counts().reindex(range(len(LABEL2ID)), fill_value=0).values
    sample_weights = np.zeros(len(train_df), dtype=np.float32)
    for label, count in enumerate(class_counts):
        if count > 0:
            sample_weights[train_df["label_id"] == label] = 1.0 / float(count)
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

    train_loader = DataLoader(
        train_dataset,
        batch_size=train_batch_size,
        sampler=sampler,
        drop_last=False,
        num_workers=0,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=eval_batch_size,
        shuffle=False,
        num_workers=0,
    )

    return train_loader, val_loader, class_counts, val_df


def compute_class_weights(class_counts: np.ndarray) -> torch.Tensor:
    total = float(class_counts.sum())
    weights = [total / count if count > 0 else 0.0 for count in class_counts]
    normalized = np.array(weights, dtype=np.float32)
    normalized /= normalized.sum() / len(class_counts)
    return torch.tensor(normalized, dtype=torch.float32)


def format_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
    }


class FocalLoss(nn.Module):
    def __init__(self, alpha: Optional[torch.Tensor] = None, gamma: float = 2.0, reduction: str = "mean"):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        log_probs = F.log_softmax(inputs, dim=-1)
        probs = torch.exp(log_probs)
        targets = targets.view(-1, 1)
        pt = probs.gather(1, targets).squeeze(1)
        log_pt = log_probs.gather(1, targets).squeeze(1)
        focal_term = (1 - pt) ** self.gamma
        loss = -focal_term * log_pt
        if self.alpha is not None:
            alpha_factor = self.alpha[targets.squeeze(1)].to(inputs.device)
            loss = alpha_factor * loss
        if self.reduction == "mean":
            return loss.mean()
        if self.reduction == "sum":
            return loss.sum()
        return loss


def _apply_neutral_threshold(probs: np.ndarray, threshold: float) -> np.ndarray:
    predictions = []
    for prob in probs:
        if prob[1] >= threshold:
            predictions.append(1)
        else:
            non_neutral = np.array([prob[0], prob[2]])
            label = int(np.argmax(non_neutral) * 2)
            predictions.append(label)
    return np.array(predictions, dtype=int)


def threshold_analysis(probs: np.ndarray, labels: np.ndarray, thresholds: np.ndarray) -> Tuple[float, float, np.ndarray]:
    best_threshold = 0.0
    best_macro_f1 = -1.0
    best_predictions = np.array([], dtype=int)
    for threshold in thresholds:
        preds = _apply_neutral_threshold(probs, threshold)
        score = f1_score(labels, preds, average="macro", zero_division=0)
        print(f"Threshold {threshold:.2f} -> macro F1: {score:.4f}")
        if score > best_macro_f1:
            best_macro_f1 = score
            best_threshold = threshold
            best_predictions = preds
    return best_threshold, best_macro_f1, best_predictions


def collect_probs_and_labels(
    model: AutoModelForSequenceClassification,
    dataloader: DataLoader,
    device: torch.device,
) -> Tuple[np.ndarray, np.ndarray]:
    model.eval()
    all_probs: List[np.ndarray] = []
    all_labels: List[int] = []
    with torch.no_grad():
        for batch in dataloader:
            inputs = {
                "input_ids": batch["input_ids"].to(device),
                "attention_mask": batch["attention_mask"].to(device),
                "token_type_ids": batch["token_type_ids"].to(device),
            }
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            all_probs.append(probs.cpu().numpy())
            all_labels.extend(batch["labels"].cpu().numpy().tolist())
    return np.concatenate(all_probs, axis=0), np.array(all_labels, dtype=int)


def train_one_epoch(
    model: AutoModelForSequenceClassification,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler._LRScheduler,
    loss_fn: nn.Module,
    device: torch.device,
) -> float:
    model.train()
    running_loss = 0.0
    for batch in dataloader:
        inputs = {
            "input_ids": batch["input_ids"].to(device),
            "attention_mask": batch["attention_mask"].to(device),
            "token_type_ids": batch["token_type_ids"].to(device),
            "labels": batch["labels"].to(device),
        }
        optimizer.zero_grad()
        outputs = model(**inputs)
        loss = loss_fn(outputs.logits, inputs["labels"])
        loss.backward()
        optimizer.step()
        scheduler.step()
        running_loss += loss.item() * inputs["labels"].size(0)

    return running_loss / len(dataloader.dataset)


def evaluate(
    model: AutoModelForSequenceClassification,
    dataloader: DataLoader,
    loss_fn: nn.Module,
    device: torch.device,
) -> Tuple[float, Dict[str, float], np.ndarray, np.ndarray]:
    model.eval()
    running_loss = 0.0
    all_predictions: List[int] = []
    all_labels: List[int] = []

    with torch.no_grad():
        for batch in dataloader:
            inputs = {
                "input_ids": batch["input_ids"].to(device),
                "attention_mask": batch["attention_mask"].to(device),
                "token_type_ids": batch["token_type_ids"].to(device),
                "labels": batch["labels"].to(device),
            }
            outputs = model(**inputs)
            loss = loss_fn(outputs.logits, inputs["labels"])
            running_loss += loss.item() * inputs["labels"].size(0)
            predictions = torch.argmax(outputs.logits, dim=-1)
            all_predictions.extend(predictions.cpu().numpy().tolist())
            all_labels.extend(inputs["labels"].cpu().numpy().tolist())

    avg_loss = running_loss / len(dataloader.dataset)
    metrics = format_metrics(np.array(all_labels), np.array(all_predictions))
    return avg_loss, metrics, np.array(all_labels), np.array(all_predictions)


def print_report(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    print("\n=== Evaluation Report ===")
    print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
    print(f"Macro F1: {f1_score(y_true, y_pred, average='macro', zero_division=0):.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=[ID2LABEL[i] for i in range(len(ID2LABEL))], zero_division=0))


def save_model(model: AutoModelForSequenceClassification, tokenizer: AutoTokenizer, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)


def _display_example_predictions(
    model: AutoModelForSequenceClassification,
    tokenizer: AutoTokenizer,
    df: pd.DataFrame,
    device: torch.device,
    n_samples: int = 3,
) -> None:
    if df.empty:
        return

    print("\n=== Example Validation Predictions ===")
    samples = df.sample(min(n_samples, len(df)), random_state=42).reset_index(drop=True)
    for idx, row in samples.iterrows():
        inputs = tokenizer(
            text=row["post_text"],
            text_pair=row["comment_text"],
            truncation=True,
            padding="max_length",
            max_length=256,
            return_tensors="pt",
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0].cpu().numpy().tolist()
            pred_label = int(torch.argmax(logits, dim=-1).cpu().item())

        print(f"\nSample {idx + 1}:")
        print(f"Post: {row['post_text']}")
        print(f"Comment: {row['comment_text']}")
        print(f"True label: {row['label_id']} ({[k for k,v in LABEL2ID.items() if v==row['label_id']][0]})")
        print(f"Predicted: {pred_label} ({[k for k,v in LABEL2ID.items() if v==pred_label][0]})")
        print("Probabilities:")
        for label_id, prob in enumerate(probs):
            print(f"  {label_id} ({[k for k,v in LABEL2ID.items() if v==label_id][0]}): {prob:.4f}")


def train(
    data_path: str,
    output_dir: str,
    epochs: int = 6,
    train_batch_size: int = 16,
    eval_batch_size: int = 32,
    learning_rate: float = 3e-5,
    max_length: int = 256,
    val_ratio: float = 0.15,
    patience: int = 2,
    seed: int = 42,
    use_focal_loss: bool = False,
    focal_gamma: float = 2.0,
) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    df = load_dataframe(data_path)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(LABEL2ID))
    model.to(device)

    train_loader, val_loader, class_counts, val_df = build_dataloaders(
        df,
        tokenizer,
        train_batch_size=train_batch_size,
        eval_batch_size=eval_batch_size,
        max_length=max_length,
        val_ratio=val_ratio,
        seed=seed,
    )

    class_weights = compute_class_weights(class_counts).to(device)
    if use_focal_loss:
        loss_fn = FocalLoss(alpha=class_weights, gamma=focal_gamma)
    else:
        loss_fn = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)

    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, int(total_steps * 0.1)),
        num_training_steps=total_steps,
    )

    best_macro_f1 = 0.0
    patience_counter = 0
    best_model_path = Path(output_dir) / "best_model"

    for epoch in range(1, epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, scheduler, loss_fn, device)
        val_loss, val_metrics, y_true, y_pred = evaluate(model, val_loader, loss_fn, device)

        print(f"\nEpoch {epoch}/{epochs}")
        print(f"Train loss: {train_loss:.4f}")
        print(f"Val loss:   {val_loss:.4f}")
        print(f"Val acc:    {val_metrics['accuracy']:.4f}")
        print(f"Val macro F1: {val_metrics['macro_f1']:.4f}")

        if val_metrics["macro_f1"] > best_macro_f1 + 1e-4:
            best_macro_f1 = val_metrics["macro_f1"]
            patience_counter = 0
            save_model(model, tokenizer, str(best_model_path))
            print(f"Saved best model to {best_model_path}")
        else:
            patience_counter += 1
            print(f"No improvement, patience {patience_counter}/{patience}")
            if patience_counter >= patience:
                print("Early stopping triggered.")
                break

    probs, labels = collect_probs_and_labels(model, val_loader, device)
    thresholds = np.arange(0.50, 0.96, 0.05)
    print("\n=== Threshold analysis for neutral decision ===")
    best_threshold, best_threshold_f1, threshold_preds = threshold_analysis(probs, labels, thresholds)
    print(f"Best neutral threshold: {best_threshold:.2f} with macro F1 = {best_threshold_f1:.4f}")

    with open(Path(output_dir) / "training_metadata.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "model_name": MODEL_NAME,
                "best_macro_f1": best_macro_f1,
                "best_threshold_macro_f1": best_threshold_f1,
                "best_neutral_threshold": best_threshold,
                "class_counts": class_counts.tolist(),
                "label_map": LABEL2ID,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print_report(y_true, y_pred)
    _display_example_predictions(model, tokenizer, val_df, device)
    print(f"Training complete. Best validation macro F1: {best_macro_f1:.4f}")
    print(f"Best model directory: {best_model_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train IndoBERT pairwise stance classifier.")
    parser.add_argument("--data-path", required=True, help="CSV dataset path with full_text, full_text_comments, stance")
    parser.add_argument("--output-dir", required=True, help="Directory to save best model and metadata")
    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument("--train-batch-size", type=int, default=16)
    parser.add_argument("--eval-batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=3e-5)
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--patience", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--use-focal-loss", action="store_true", help="Use focal loss to reduce majority neutral bias")
    parser.add_argument("--focal-gamma", type=float, default=2.0, help="Focal loss gamma parameter")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train(
        data_path=args.data_path,
        output_dir=args.output_dir,
        epochs=args.epochs,
        train_batch_size=args.train_batch_size,
        eval_batch_size=args.eval_batch_size,
        learning_rate=args.learning_rate,
        max_length=args.max_length,
        val_ratio=args.val_ratio,
        patience=args.patience,
        seed=args.seed,
        use_focal_loss=args.use_focal_loss,
        focal_gamma=args.focal_gamma,
    )
