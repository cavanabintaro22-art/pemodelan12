#!/usr/bin/env python3
"""
Test script to verify topic coherence improvements
"""

import pandas as pd
from streamlit_app import preprocess_text, calculate_topic_coherence
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer

def test_coherence():
    # Load sample data
    df = pd.read_csv('/workspaces/pemodelan6/sample_posts_comments.csv')
    docs = df['full_text'].apply(preprocess_text).tolist()
    docs = [doc for doc in docs if doc.strip()]

    print(f"Loaded {len(docs)} documents")
    print("Sample preprocessed docs:")
    for i, doc in enumerate(docs[:3]):
        print(f"{i+1}: {doc}")

    # Initialize BERTopic with updated parameters
    embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    vectorizer_model = CountVectorizer(ngram_range=(1, 2), min_df=5, max_df=0.8)

    topic_model = BERTopic(
        embedding_model=embedding_model,
        vectorizer_model=vectorizer_model,
        nr_topics="auto",
        min_topic_size=50,  # Will be adjusted for small dataset
        calculate_probabilities=False,
    )

    # Fit model
    topics, probabilities = topic_model.fit_transform(docs)

    print(f"\nTopics found: {len(set(topics)) - 1}")  # -1 for -1 outlier topic

    # Calculate coherence
    coherence_results = calculate_topic_coherence(topic_model, docs, coherence_type='c_v')

    print(f"\nCoherence Results:")
    print(f"Overall coherence: {coherence_results.get('overall_coherence', 'N/A')}")
    print(f"Topic coherences: {coherence_results.get('topic_coherences', [])}")

    return coherence_results

if __name__ == "__main__":
    test_coherence()