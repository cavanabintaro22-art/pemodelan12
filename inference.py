import os
from typing import Dict, Optional, Tuple

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
