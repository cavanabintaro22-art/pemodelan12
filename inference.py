import os
from typing import Dict, List, Optional, Tuple

import torch
from torch.nn.functional import softmax
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from dataset import ID2LABEL, LABEL2ID, clean_indonesian_text

MODEL_NAME = "indobenchmark/indobert-base-p1"


class StancePairClassifier:
    """Wrapper for pairwise IndoBERT stance inference."""

    def __init__(self, model_dir: Optional[str] = None, device: Optional[str] = None):
        self.model_dir = model_dir or MODEL_NAME
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, post: str, comment: str) -> Dict[str, object]:
        post_text = clean_indonesian_text(post)
        comment_text = clean_indonesian_text(comment)
        encoding = self.tokenizer(
            text=post_text,
            text_pair=comment_text,
            truncation=True,
            padding="max_length",
            max_length=256,
            return_tensors="pt",
        )
        encoding = {k: v.to(self.device) for k, v in encoding.items()}

        with torch.no_grad():
            outputs = self.model(**encoding)
            logits = outputs.logits
            probs = softmax(logits, dim=-1)[0].cpu().numpy().tolist()
            label_id = int(torch.argmax(logits, dim=-1).cpu().item())

        return {
            "label_id": label_id,
            "label": ID2LABEL[label_id],
            "probabilities": {ID2LABEL[i]: float(probs[i]) for i in range(len(probs))},
        }

    def predict_batch(
        self,
        posts: List[str],
        comments: List[str],
        batch_size: int = 16,
    ) -> Tuple[List[int], List[Dict[str, float]]]:
        assert len(posts) == len(comments), "Posts and comments lists must have the same length."
        label_ids: List[int] = []
        probabilities: List[Dict[str, float]] = []

        for start_idx in range(0, len(posts), batch_size):
            batch_posts = [clean_indonesian_text(text) for text in posts[start_idx : start_idx + batch_size]]
            batch_comments = [clean_indonesian_text(text) for text in comments[start_idx : start_idx + batch_size]]
            encoding = self.tokenizer(
                text=batch_posts,
                text_pair=batch_comments,
                truncation=True,
                padding="max_length",
                max_length=256,
                return_tensors="pt",
            )
            encoding = {k: v.to(self.device) for k, v in encoding.items()}

            with torch.no_grad():
                outputs = self.model(**encoding)
                probs_batch = softmax(outputs.logits, dim=-1).cpu().numpy()
                preds = probs_batch.argmax(axis=-1).tolist()

            for label_id, prob_scores in zip(preds, probs_batch):
                label_ids.append(int(label_id))
                probabilities.append({ID2LABEL[i]: float(prob_scores[i]) for i in range(len(prob_scores))})

        return label_ids, probabilities


def predict_stance(post: str, comment: str, model_dir: Optional[str] = None) -> Dict[str, object]:
    """Predict stance given a post and a comment pair."""
    classifier = StancePairClassifier(model_dir=model_dir)
    return classifier.predict(post, comment)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Infer pairwise stance with IndoBERT.")
    parser.add_argument("--model-dir", default=None, help="Directory of saved model or pretrained name")
    parser.add_argument("--post", required=True, help="Post text")
    parser.add_argument("--comment", required=True, help="Comment text")
    args = parser.parse_args()

    classifier = StancePairClassifier(model_dir=args.model_dir)
    result = classifier.predict(args.post, args.comment)
    print("Prediction:")
    print(f"  label_id: {result['label_id']}")
    print(f"  label: {result['label']}")
    print("  probabilities:")
    for label, score in result["probabilities"].items():
        print(f"    {label}: {score:.4f}")
