import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import math


@dataclass
class EvaluationResults:
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    precision_weighted: float
    recall_weighted: float
    f1_weighted: float
    classification_report: str
    confusion_matrix: np.ndarray
    labels: List[str]

    def to_dict(self) -> Dict:
        return {
            "accuracy": self.accuracy,
            "precision_macro": self.precision_macro,
            "recall_macro": self.recall_macro,
            "f1_macro": self.f1_macro,
            "precision_weighted": self.precision_weighted,
            "recall_weighted": self.recall_weighted,
            "f1_weighted": self.f1_weighted,
            "classification_report": self.classification_report,
            "confusion_matrix": self.confusion_matrix.tolist(),
            "labels": self.labels,
        }


def evaluate_classification(
    y_true: List[str],
    y_pred: List[str],
    labels: Optional[List[str]] = None,
) -> EvaluationResults:
    """Evaluate classification results using standard metrics."""
    if labels is None:
        labels = sorted(list(set(y_true) | set(y_pred)))

    accuracy = accuracy_score(y_true, y_pred)
    precision_macro = precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    recall_macro = recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    f1_macro = f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    precision_weighted = precision_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)
    recall_weighted = recall_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)
    report = classification_report(y_true, y_pred, labels=labels, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    return EvaluationResults(
        accuracy=accuracy,
        precision_macro=precision_macro,
        recall_macro=recall_macro,
        f1_macro=f1_macro,
        precision_weighted=precision_weighted,
        recall_weighted=recall_weighted,
        f1_weighted=f1_weighted,
        classification_report=report,
        confusion_matrix=cm,
        labels=labels,
    )


def load_ground_truth_stance(path: str) -> pd.DataFrame:
    """Load a ground truth stance file from CSV."""
    df = pd.read_csv(path)
    required_cols = [
        "comment_id",
        "model_prediction",
        "expert_stance",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in ground truth stance file: {missing}")
    return df


def evaluate_stance_ground_truth(
    path: str,
    prediction_col: str = "model_prediction",
    label_col: str = "expert_stance",
    label_order: Optional[List[str]] = None,
) -> EvaluationResults:
    """Evaluate stance classification using a ground truth CSV file."""
    df = load_ground_truth_stance(path)
    y_true = df[label_col].astype(str).tolist()
    y_pred = df[prediction_col].astype(str).tolist()

    labels = label_order if label_order is not None else sorted(list(set(y_true) | set(y_pred)))
    return evaluate_classification(y_true, y_pred, labels=labels)


def save_evaluation_results(results: EvaluationResults, path: str) -> None:
    """Save evaluation results to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results.to_dict(), f, indent=2, ensure_ascii=False)


def format_confusion_matrix(results: EvaluationResults) -> str:
    """Return a printable confusion matrix table."""
    labels = results.labels
    cm = results.confusion_matrix.tolist()
    header = [" "] + [f"Pred:{label}" for label in labels]
    rows = [header]
    for label, row in zip(labels, cm):
        rows.append([f"True:{label}"] + [str(int(x)) for x in row])

    col_widths = [max(len(cell) for cell in column) for column in zip(*rows)]
    lines = []
    for row in rows:
        padded = [cell.ljust(width) for cell, width in zip(row, col_widths)]
        lines.append(" | ".join(padded))
    return "\n".join(lines)


def summary_text(results: EvaluationResults) -> str:
    """Return a plain text summary of evaluation metrics."""
    return (
        f"Accuracy: {results.accuracy:.4f}\n"
        f"Precision (macro): {results.precision_macro:.4f}\n"
        f"Recall (macro): {results.recall_macro:.4f}\n"
        f"F1 Score (macro): {results.f1_macro:.4f}\n"
        f"Precision (weighted): {results.precision_weighted:.4f}\n"
        f"Recall (weighted): {results.recall_weighted:.4f}\n"
        f"F1 Score (weighted): {results.f1_weighted:.4f}\n"
    )


@dataclass
class TopicEvaluationResults:
    coherence_score: float
    topic_diversity: float
    intra_topic_similarity: float
    topic_size_variance: float
    expert_agreement_score: Optional[float] = None
    topic_quality_scores: Dict[int, float] = None

    def to_dict(self) -> Dict:
        return asdict(self)


def calculate_coherence_score(topics: List[List[str]], documents: List[str], coherence_type: str = 'c_v') -> float:
    """
    Calculate topic coherence score.

    Args:
        topics: List of topic word lists
        documents: List of preprocessed documents
        coherence_type: Type of coherence ('c_v', 'u_mass', 'c_npmi')

    Returns:
        Coherence score
    """
    try:
        from gensim.models import CoherenceModel
        from gensim.corpora import Dictionary

        # Create dictionary and corpus
        dictionary = Dictionary(documents)
        corpus = [dictionary.doc2bow(doc.split()) for doc in documents]

        # Calculate coherence
        coherence_model = CoherenceModel(
            topics=topics,
            texts=[doc.split() for doc in documents],
            corpus=corpus,
            dictionary=dictionary,
            coherence=coherence_type
        )

        return coherence_model.get_coherence()

    except ImportError:
        # Fallback implementation without gensim
        return _calculate_coherence_fallback(topics, documents)


def _calculate_coherence_fallback(topics: List[List[str]], documents: List[str]) -> float:
    """Fallback coherence calculation using word co-occurrence."""
    # Simple implementation based on word pair frequencies
    word_docs = {}
    for doc in documents:
        words = set(doc.split())
        for word in words:
            if word not in word_docs:
                word_docs[word] = 0
            word_docs[word] += 1

    total_coherence = 0
    total_pairs = 0

    for topic_words in topics:
        if len(topic_words) < 2:
            continue

        topic_coherence = 0
        pair_count = 0

        for i in range(len(topic_words)):
            for j in range(i+1, len(topic_words)):
                word1, word2 = topic_words[i], topic_words[j]

                # Calculate co-occurrence score
                if word1 in word_docs and word2 in word_docs:
                    co_occur = sum(1 for doc in documents
                                 if word1 in doc and word2 in doc)
                    score = math.log((co_occur + 1) / (word_docs[word1] * word_docs[word2] + 1))
                    topic_coherence += score
                    pair_count += 1

        if pair_count > 0:
            total_coherence += topic_coherence / pair_count
            total_pairs += 1

    return total_coherence / total_pairs if total_pairs > 0 else 0.0


def calculate_topic_diversity(topics: List[List[str]]) -> float:
    """
    Calculate topic diversity (1 - redundancy).
    Measures how unique the words are across topics.
    """
    all_words = []
    for topic in topics:
        all_words.extend(topic)

    total_words = len(all_words)
    unique_words = len(set(all_words))

    return unique_words / total_words if total_words > 0 else 0.0


def calculate_intra_topic_similarity(topics: List[List[str]], embeddings: Optional[np.ndarray] = None) -> float:
    """
    Calculate average intra-topic similarity.
    Measures how similar words are within each topic.
    """
    if embeddings is None:
        # Simple word overlap based similarity
        similarities = []
        for topic_words in topics:
            if len(topic_words) < 2:
                continue

            total_sim = 0
            count = 0
            for i in range(len(topic_words)):
                for j in range(i+1, len(topic_words)):
                    # Simple Jaccard similarity
                    set1 = set(topic_words[i])
                    set2 = set(topic_words[j])
                    intersection = len(set1.intersection(set2))
                    union = len(set1.union(set2))
                    sim = intersection / union if union > 0 else 0
                    total_sim += sim
                    count += 1

            if count > 0:
                similarities.append(total_sim / count)

        return np.mean(similarities) if similarities else 0.0

    else:
        # Cosine similarity based
        similarities = []
        for topic_words in topics:
            if len(topic_words) < 2:
                continue

            topic_embeddings = embeddings[[i for i, word in enumerate(embeddings) if word in topic_words]]
            if len(topic_embeddings) > 1:
                sim_matrix = cosine_similarity(topic_embeddings)
                # Average similarity between all pairs
                avg_sim = (np.sum(sim_matrix) - len(topic_embeddings)) / (len(topic_embeddings) * (len(topic_embeddings) - 1))
                similarities.append(avg_sim)

        return np.mean(similarities) if similarities else 0.0


def calculate_topic_size_variance(topic_sizes: List[int]) -> float:
    """Calculate variance in topic sizes."""
    return np.var(topic_sizes) if topic_sizes else 0.0


def evaluate_expert_agreement(expert_ratings: List[Dict[int, float]]) -> float:
    """
    Calculate expert agreement on topic quality.
    Uses average standard deviation across topics.
    """
    if not expert_ratings:
        return 0.0

    topic_scores = {}
    for rating in expert_ratings:
        for topic_id, score in rating.items():
            if topic_id not in topic_scores:
                topic_scores[topic_id] = []
            topic_scores[topic_id].append(score)

    if not topic_scores:
        return 0.0

    # Calculate agreement as 1 - average coefficient of variation
    variations = []
    for scores in topic_scores.values():
        if len(scores) > 1:
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            cv = std_score / mean_score if mean_score > 0 else 0
            variations.append(cv)

    avg_variation = np.mean(variations) if variations else 0.0
    return 1.0 - avg_variation  # Higher agreement = lower variation


def evaluate_topic_model(
    topics: Dict[int, List[str]],
    documents: List[str],
    topic_sizes: Optional[List[int]] = None,
    expert_ratings: Optional[List[Dict[int, float]]] = None,
    embeddings: Optional[np.ndarray] = None
) -> TopicEvaluationResults:
    """
    Comprehensive evaluation of topic model.

    Args:
        topics: Dictionary mapping topic ID to list of top words
        documents: List of preprocessed documents
        topic_sizes: List of document counts per topic
        expert_ratings: List of expert rating dictionaries
        embeddings: Word embeddings for similarity calculation

    Returns:
        TopicEvaluationResults with all metrics
    """
    topic_word_lists = list(topics.values())

    # Calculate coherence
    coherence = calculate_coherence_score(topic_word_lists, documents)

    # Calculate diversity
    diversity = calculate_topic_diversity(topic_word_lists)

    # Calculate intra-topic similarity
    intra_similarity = calculate_intra_topic_similarity(topic_word_lists, embeddings)

    # Calculate topic size variance
    size_variance = calculate_topic_size_variance(topic_sizes) if topic_sizes else 0.0

    # Calculate expert agreement
    expert_agreement = evaluate_expert_agreement(expert_ratings) if expert_ratings else None

    # Calculate individual topic quality scores
    topic_quality = {}
    for topic_id, words in topics.items():
        # Simple quality score based on word diversity and coherence contribution
        word_diversity = len(set(words)) / len(words) if words else 0
        topic_quality[topic_id] = (coherence + word_diversity) / 2

    return TopicEvaluationResults(
        coherence_score=coherence,
        topic_diversity=diversity,
        intra_topic_similarity=intra_similarity,
        topic_size_variance=size_variance,
        expert_agreement_score=expert_agreement,
        topic_quality_scores=topic_quality
    )


def print_topic_evaluation(results: TopicEvaluationResults) -> str:
    """Return formatted string of topic evaluation results."""
    output = []
    output.append("=== Topic Model Evaluation Results ===")
    output.append(f"Coherence Score: {results.coherence_score:.4f}")
    output.append(f"Topic Diversity: {results.topic_diversity:.4f}")
    output.append(f"Intra-topic Similarity: {results.intra_topic_similarity:.4f}")
    output.append(f"Topic Size Variance: {results.topic_size_variance:.4f}")

    if results.expert_agreement_score is not None:
        output.append(f"Expert Agreement Score: {results.expert_agreement_score:.4f}")

    if results.topic_quality_scores:
        output.append("\nTopic Quality Scores:")
        for topic_id, score in results.topic_quality_scores.items():
            output.append(f"  Topic {topic_id}: {score:.4f}")

    return "\n".join(output)
