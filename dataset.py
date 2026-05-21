import re
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import PreTrainedTokenizerBase

LABEL2ID: Dict[str, int] = {
    "against": 0,
    "neutral": 1,
    "support": 2,
}
ID2LABEL: Dict[int, str] = {value: key for key, value in LABEL2ID.items()}

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
MENTION_PATTERN = re.compile(r"@\w+")
HASHTAG_PATTERN = re.compile(r"#(\w+)")
MULTI_SPACE_PATTERN = re.compile(r"\s+")
REPEATED_CHAR_PATTERN = re.compile(r"(.)\1{2,}")


def clean_indonesian_text(text: str) -> str:
    """Lightweight Indonesian text preprocessing for transformer input."""
    if not isinstance(text, str):
        return ""

    text = text.strip()
    text = URL_PATTERN.sub(" ", text)
    text = MENTION_PATTERN.sub(" ", text)
    text = HASHTAG_PATTERN.sub(r"\1", text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = REPEATED_CHAR_PATTERN.sub(r"\1\1", text)
    text = MULTI_SPACE_PATTERN.sub(" ", text)
    text = text.lower()
    return text.strip()


def normalize_stance_label(label: str) -> Optional[int]:
    """Convert text labels into numeric IDs with a fixed Indonesian mapping."""
    if not isinstance(label, str):
        return None

    label = label.strip().lower()
    if label in {"against", "menentang", "kontra", "tolak", "negative", "neg"}:
        return LABEL2ID["against"]
    if label in {"support", "mendukung", "setuju", "pro", "positive", "pos"}:
        return LABEL2ID["support"]
    if label in {"neutral", "netral", "net", "n"}:
        return LABEL2ID["neutral"]
    return None


def prepare_stance_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize dataframe and return only usable rows for pairwise stance training."""
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None.")

    columns = ["full_text", "full_text_comments", "stance"]
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"DataFrame must contain columns: {missing}")

    df = df.copy()
    df["post_text"] = df["full_text"].fillna("").astype(str).map(clean_indonesian_text)
    df["comment_text"] = df["full_text_comments"].fillna("").astype(str).map(clean_indonesian_text)
    df["label_id"] = df["stance"].map(normalize_stance_label)
    df = df.dropna(subset=["label_id"])
    df["label_id"] = df["label_id"].astype(int)
    df = df[df["post_text"].str.len() > 0]
    df = df[df["comment_text"].str.len() > 0]
    df = df.reset_index(drop=True)
    return df[["post_text", "comment_text", "label_id"]]


class StancePairDataset(Dataset):
    """PyTorch dataset for IndoBERT pairwise stance classification."""

    def __init__(
        self,
        tokenizer: PreTrainedTokenizerBase,
        posts: List[str],
        comments: List[str],
        labels: Optional[List[int]] = None,
        max_length: int = 256,
    ):
        self.tokenizer = tokenizer
        self.posts = posts
        self.comments = comments
        self.labels = labels
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.posts)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        encoding = self.tokenizer(
            text=self.posts[idx],
            text_pair=self.comments[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_attention_mask=True,
            return_token_type_ids=True,
        )
        batch = {
            "input_ids": torch.tensor(encoding["input_ids"], dtype=torch.long),
            "attention_mask": torch.tensor(encoding["attention_mask"], dtype=torch.long),
            "token_type_ids": torch.tensor(encoding["token_type_ids"], dtype=torch.long),
        }
        if self.labels is not None:
            batch["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return batch


def create_dataset_from_dataframe(
    tokenizer: PreTrainedTokenizerBase,
    df: pd.DataFrame,
    max_length: int = 256,
) -> StancePairDataset:
    """Build a pairwise dataset from a prepared DataFrame."""
    return StancePairDataset(
        tokenizer=tokenizer,
        posts=df["post_text"].tolist(),
        comments=df["comment_text"].tolist(),
        labels=df["label_id"].tolist(),
        max_length=max_length,
    )
