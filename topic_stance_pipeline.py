import argparse
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd
from bertopic import BERTopic

from dataset import clean_indonesian_text
from inference import StancePairClassifier
from topic_modeling import build_topic_model

DEFAULT_TOPIC_MODEL_DIR = "topic_model"
DEFAULT_STANCE_MODEL_DIR = "model_output/best_model"


class TopicStancePipeline:
    """Pipeline for combining topic modeling on posts with pairwise comment stance."""

    def __init__(
        self,
        stance_model_dir: Optional[str] = None,
        topic_model_dir: Optional[str] = None,
        topic_embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
    ):
        self.stance_model_dir = stance_model_dir or DEFAULT_STANCE_MODEL_DIR
        self.topic_model_dir = topic_model_dir or DEFAULT_TOPIC_MODEL_DIR
        self.topic_embedding_model_name = topic_embedding_model_name
        self.stance_classifier: Optional[StancePairClassifier] = None
        self.topic_model: Optional[BERTopic] = None

    def load_stance_classifier(self) -> StancePairClassifier:
        if self.stance_classifier is None:
            self.stance_classifier = StancePairClassifier(model_dir=self.stance_model_dir)
        return self.stance_classifier

    def load_topic_model(self) -> Optional[BERTopic]:
        if self.topic_model is not None:
            return self.topic_model
        model_path = Path(self.topic_model_dir)
        if model_path.exists():
            try:
                self.topic_model = BERTopic.load(str(model_path))
                return self.topic_model
            except Exception:
                return None
        return None

    def fit_topic_model(self, posts: pd.Series) -> pd.DataFrame:
        if posts.empty:
            raise ValueError("No post text available for topic modeling.")

        cleaned_posts = posts.fillna("").astype(str).map(clean_indonesian_text)
        output, topic_model, _ = build_topic_model(
            posts_df=pd.DataFrame({"clean_text": cleaned_posts}),
            text_column="clean_text",
            embedding_model_name=self.topic_embedding_model_name,
        )
        self.topic_model = topic_model
        os.makedirs(self.topic_model_dir, exist_ok=True)
        topic_model.save(self.topic_model_dir)
        return output

    def assign_topics(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["post_text"] = df["full_text"].fillna("").astype(str).map(clean_indonesian_text)
        df["comment_text"] = df["full_text_comments"].fillna("").astype(str).map(clean_indonesian_text)

        topic_model = self.load_topic_model()
        if topic_model is None:
            topic_output = self.fit_topic_model(df["post_text"])
        else:
            topic_output, _ = topic_model.transform(df["post_text"], return_probability=True)
            df["topic_id"] = topic_output
            topic_info = topic_model.get_topic_info()
            topic_names = {int(topic): ", ".join([word for word, _ in topic_model.get_topic(int(topic))[:5]]) for topic in topic_info[topic_info.Topic != -1].Topic}
            topic_names[-1] = "Outlier"
            df["topic_name"] = [topic_names.get(int(topic), "Outlier") for topic in topic_output]
            probabilities = topic_model.transform(df["post_text"], return_probability=True)[1]
            df["topic_probability"] = [float(probs[0]) if isinstance(probs, (list, tuple)) and len(probs) else 0.0 for probs in probabilities]
            return df

        df = df.merge(
            topic_output[["topic_id", "topic_name", "topic_probability"]],
            left_index=True,
            right_index=True,
        )
        return df

    def predict_stance(self, df: pd.DataFrame, batch_size: int = 16) -> pd.DataFrame:
        df = df.copy()
        classifier = self.load_stance_classifier()
        label_ids, probabilities = classifier.predict_batch(
            posts=df["post_text"].tolist(),
            comments=df["comment_text"].tolist(),
            batch_size=batch_size,
        )
        labels = [classifier.model.config.id2label[label_id] if hasattr(classifier.model.config, "id2label") else None for label_id in label_ids]
        df["stance_label_id"] = label_ids
        df["stance"] = [clean_label(label) for label in labels]
        df["stance_confidence"] = [max(prob.values()) for prob in probabilities]
        return df

    @staticmethod
    def aggregate_distribution(df: pd.DataFrame) -> pd.DataFrame:
        dist = (
            df.groupby(["topic_id", "topic_name", "stance"])
            .size()
            .reset_index(name="count")
        )
        dist["percentage"] = dist.groupby(["topic_id"])["count"].transform(lambda x: x / x.sum() * 100)
        return dist.sort_values(["topic_id", "stance"], ascending=[True, True])

    def run(
        self,
        input_csv: str,
        output_prefix: str,
        batch_size: int = 16,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = pd.read_csv(input_csv, dtype=str, keep_default_na=False)
        df = df[["full_text", "full_text_comments"]].copy()
        df = df.dropna(subset=["full_text", "full_text_comments"])  # ensure both sides
        df["full_text"] = df["full_text"].astype(str)
        df["full_text_comments"] = df["full_text_comments"].astype(str)

        df = self.assign_topics(df)
        df = self.predict_stance(df, batch_size=batch_size)
        distribution = self.aggregate_distribution(df)

        os.makedirs(Path(output_prefix).parent, exist_ok=True)
        df.to_csv(f"{output_prefix}_comment_topic_stance.csv", index=False)
        distribution.to_csv(f"{output_prefix}_topic_stance_distribution.csv", index=False)

        return df, distribution


def clean_label(label: Optional[str]) -> str:
    if label is None:
        return "neutral"
    normalized = str(label).strip().lower()
    if normalized.startswith("label_"):
        normalized = normalized.replace("label_", "")
        if normalized.isdigit():
            numeric = int(normalized)
            return {0: "against", 1: "neutral", 2: "support"}.get(numeric, "neutral")
    if normalized in {"support", "positive", "pos", "pro"}:
        return "support"
    if normalized in {"against", "negative", "neg", "kontra"}:
        return "against"
    return "neutral"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run topic + pairwise stance pipeline.")
    parser.add_argument("--input-csv", required=True, help="Input CSV with full_text and full_text_comments")
    parser.add_argument("--output-prefix", required=True, help="Prefix for output CSV files")
    parser.add_argument("--stance-model-dir", default=DEFAULT_STANCE_MODEL_DIR, help="Directory of saved pairwise stance model")
    parser.add_argument("--topic-model-dir", default=DEFAULT_TOPIC_MODEL_DIR, help="Directory to save or load BERTopic model")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size for stance inference")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = TopicStancePipeline(
        stance_model_dir=args.stance_model_dir,
        topic_model_dir=args.topic_model_dir,
    )
    comments_df, distribution_df = pipeline.run(
        input_csv=args.input_csv,
        output_prefix=args.output_prefix,
        batch_size=args.batch_size,
    )
    print(f"Saved comment-level output: {args.output_prefix}_comment_topic_stance.csv")
    print(f"Saved distribution output: {args.output_prefix}_topic_stance_distribution.csv")
    print(distribution_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
