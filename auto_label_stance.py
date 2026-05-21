import argparse
import csv
import os
import re
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util

from dataset import clean_indonesian_text

SUPPORT_KEYWORDS = {
    "setuju", "dukung", "mendukung", "support", "bagus", "baik", "oke", "ok", "ya",
    "betul", "benar", "apresiasi", "mantap", "positif", "bagus sekali", "boleh",
}
AGAINST_KEYWORDS = {
    "tolak", "menentang", "kontra", "benci", "buruk", "salah", "tidak setuju", "gak setuju",
    "ga setuju", "nggak setuju", "bohong", "bohong banget", "kritis", "serang", "menyerang", "kabur",
}
NEGATION_TERMS = {"tidak", "gak", "ga", "bukan", "belum", "jangan", "tak"}
QUESTION_TERMS = {"kenapa", "mengapa", "apakah", "kapan", "siapa", "bagaimana", "apa", "kenapa"}
POSITIVE_LEXICON = {
    "bagus", "baik", "setuju", "mendukung", "support", "positif", "keren", "oke", "mantap",
}
NEGATIVE_LEXICON = {
    "tolak", "menentang", "kontra", "buruk", "salah", "benci", "bohong", "jelek", "parah",
}

SUPPORT_TEMPLATES = [
    "Saya mendukung pendapat ini.",
    "Saya setuju dengan isi postingan.",
    "Argumen ini layak didukung.",
    "Komentar ini positif terhadap tulisan.",
]
AGAINST_TEMPLATES = [
    "Saya tidak setuju dengan postingan ini.",
    "Komentar ini menolak argumen dalam postingan.",
    "Pendapat ini salah.",
    "Ini kritik terhadap isi postingan.",
]

SEMANTIC_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def load_dataframe(input_path: str) -> pd.DataFrame:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    expected_columns = {"full_text", "full_text_comments"}
    missing = expected_columns - set(df.columns)
    if missing:
        raise ValueError(f"CSV harus berisi kolom: {sorted(missing)}")
    return df[["full_text", "full_text_comments"]].copy()


def is_question(text: str) -> bool:
    return any(term in text for term in QUESTION_TERMS)


def count_keyword_matches(text: str, keywords: set) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def has_negation(text: str) -> bool:
    return any(term in text for term in NEGATION_TERMS)


def normalize_text(text: str) -> str:
    text = str(text).strip().lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[@#]\w+", " ", text)
    text = re.sub(r"[^\w\s'’\"]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def sentiment_orientation(text: str) -> int:
    """Return orientation score: positive=1, negative=-1, neutral=0."""
    positive_score = count_keyword_matches(text, POSITIVE_LEXICON)
    negative_score = count_keyword_matches(text, NEGATIVE_LEXICON)
    if positive_score > negative_score:
        return 1
    if negative_score > positive_score:
        return -1
    return 0


def semantic_support_against_scores(
    post_text: str,
    comment_text: str,
    embedder: SentenceTransformer,
    support_embeddings: torch.Tensor,
    against_embeddings: torch.Tensor,
) -> Tuple[float, float, float]:
    post_text = normalize_text(post_text)
    comment_text = normalize_text(comment_text)
    encoded = embedder.encode([post_text, comment_text], convert_to_tensor=True, show_progress_bar=False)
    post_emb, comment_emb = encoded[0], encoded[1]
    support_score = float(util.cos_sim(comment_emb, support_embeddings).max())
    against_score = float(util.cos_sim(comment_emb, against_embeddings).max())
    post_comment_similarity = float(util.cos_sim(post_emb, comment_emb).item())
    return support_score, against_score, post_comment_similarity


def choose_stance_from_signals(
    post: str,
    comment: str,
    semantic_scores: Tuple[float, float, float],
) -> str:
    comment_text = normalize_text(comment)
    support_count = count_keyword_matches(comment_text, SUPPORT_KEYWORDS)
    against_count = count_keyword_matches(comment_text, AGAINST_KEYWORDS)
    negation = has_negation(comment_text)
    orientation = sentiment_orientation(comment_text)
    support_score, against_score, _ = semantic_scores
    score = 0.0

    if support_count > against_count:
        score += 2.0
    if against_count > support_count:
        score -= 2.0
    if support_count >= 1 and against_count == 0:
        score += 1.0
    if against_count >= 1 and support_count == 0:
        score -= 1.0
    if orientation > 0:
        score += 0.8
    if orientation < 0:
        score -= 0.8
    score += support_score - against_score

    if negation and support_count > 0 and against_score >= support_score:
        score -= 2.5
    if negation and against_count > 0 and support_score >= against_score:
        score += 0.5

    if support_score - against_score >= 0.25:
        score += 1.0
    if against_score - support_score >= 0.25:
        score -= 1.0

    if is_question(comment_text) and abs(score) < 1.0:
        return "neutral"
    if score >= 1.5:
        return "support"
    if score <= -1.5:
        return "against"
    if support_count >= 1 and against_count == 0 and orientation >= 0:
        return "support"
    if against_count >= 1 and support_count == 0 and orientation <= 0:
        return "against"
    return "neutral"


def label_comment(
    post: str,
    comment: str,
    embedder: SentenceTransformer,
    support_embeddings: torch.Tensor,
    against_embeddings: torch.Tensor,
) -> Dict[str, object]:
    post_text = clean_indonesian_text(post)
    comment_text = clean_indonesian_text(comment)
    semantic_scores = semantic_support_against_scores(
        post_text, comment_text, embedder, support_embeddings, against_embeddings
    )
    stance = choose_stance_from_signals(post_text, comment_text, semantic_scores)
    return {
        "full_text": post_text,
        "full_text_comments": comment_text,
        "stance": stance,
        "support_score": semantic_scores[0],
        "against_score": semantic_scores[1],
        "post_comment_similarity": semantic_scores[2],
    }


def build_label_dataframe(input_df: pd.DataFrame, embedder: SentenceTransformer) -> pd.DataFrame:
    support_embeddings = embedder.encode(SUPPORT_TEMPLATES, convert_to_tensor=True, show_progress_bar=False)
    against_embeddings = embedder.encode(AGAINST_TEMPLATES, convert_to_tensor=True, show_progress_bar=False)
    rows: List[Dict[str, object]] = []
    for _, row in input_df.iterrows():
        labeled = label_comment(
            post=row["full_text"],
            comment=row["full_text_comments"],
            embedder=embedder,
            support_embeddings=support_embeddings,
            against_embeddings=against_embeddings,
        )
        rows.append({
            "full_text": labeled["full_text"],
            "full_text_comments": labeled["full_text_comments"],
            "stance": labeled["stance"],
        })
    return pd.DataFrame(rows, columns=["full_text", "full_text_comments", "stance"])


def save_csv(df: pd.DataFrame, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auto-label stance for post-comment pairs.")
    parser.add_argument("--input-csv", required=True, help="Input CSV file containing full_text and full_text_comments columns")
    parser.add_argument("--output-csv", required=True, help="Output CSV path for labeled stance data")
    parser.add_argument("--model-name", default=SEMANTIC_MODEL_NAME, help="SentenceTransformer model for semantic similarity")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_dataframe(args.input_csv)
    print(f"Loaded {len(df)} rows from {args.input_csv}")
    embedder = SentenceTransformer(args.model_name)
    labeled_df = build_label_dataframe(df, embedder)
    save_csv(labeled_df, args.output_csv)
    print(f"Saved labeled dataset to {args.output_csv}")
    print(labeled_df["stance"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
