# -*- coding: utf-8 -*-
"""
Streamlit app untuk Dynamic Topic Modeling & Stance Analysis
Versi optimized untuk data komentar media sosial Bahasa Indonesia
"""

import streamlit as st
import pandas as pd
from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP
from hdbscan import HDBSCAN
import logging

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Dynamic Topic Modeling & Stance", layout="wide")
st.title("📊 Dynamic Topic Modeling & Stance Analysis")
st.write("Aplikasi untuk analisis topik dinamis dan stance berbahasa Indonesia")

# Upload dataset
uploaded_file = st.file_uploader("Upload dataset CSV", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Dataset loaded: {len(df)} rows")
        
        # Preview
        with st.expander("Preview Data"):
            st.dataframe(df.head())
        
        # Simple preprocessing
        def preprocess(text):
            if pd.isna(text):
                return ""
            text = str(text).lower()
            import re
            text = re.sub(r"\s+", " ", text).strip()
            return text
        
        def calculate_coherence(topic_model, docs):
            from gensim.models import CoherenceModel
            from gensim.corpora import Dictionary
            tokenized_docs = [doc.split() for doc in docs if doc.strip()]
            if not tokenized_docs:
                raise ValueError("Tidak ada dokumen valid untuk menghitung coherence")
            dictionary = Dictionary(tokenized_docs)
            dictionary.filter_extremes(no_below=5, no_above=0.5)
            corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]
            if len(dictionary) == 0 or len(corpus) == 0:
                raise ValueError("Dictionary atau corpus kosong untuk coherence")
            topic_words = []
            for topic_id in sorted(topic_model.get_topics().keys()):
                if topic_id == -1:
                    continue
                words = [w for w, _ in topic_model.get_topic(topic_id)[:10]]
                if words:
                    topic_words.append(words)
            if not topic_words:
                raise ValueError("Tidak ada topik valid untuk menghitung coherence")
            coherence_model = CoherenceModel(
                topics=topic_words,
                texts=tokenized_docs,
                corpus=corpus,
                dictionary=dictionary,
                coherence='c_v'
            )
            return coherence_model.get_coherence()
        
        def run_analysis():
            try:
                if "full_text" not in df.columns:
                    st.error("Dataset harus memiliki kolom 'full_text'")
                    return
                docs = df["full_text"].dropna().astype(str).apply(preprocess).tolist()
                docs = [d for d in docs if d.strip()]
                if not docs:
                    st.error("Dataset tidak memiliki teks valid di kolom 'full_text'")
                    return
                
                # Initialize models
                embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
                vectorizer = CountVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9)
                umap_model = UMAP(
                    n_neighbors=15,
                    n_components=5,
                    min_dist=0.0,
                    metric='cosine',
                    random_state=42
                )
                hdbscan_model = HDBSCAN(
                    min_cluster_size=20,
                    metric='euclidean',
                    cluster_selection_method='eom',
                    prediction_data=True
                )
                representation_model = MaximalMarginalRelevance(diversity=0.3)
                
                topic_model = BERTopic(
                    embedding_model=embedding_model,
                    umap_model=umap_model,
                    hdbscan_model=hdbscan_model,
                    vectorizer_model=vectorizer,
                    representation_model=representation_model,
                    nr_topics="auto",
                    min_topic_size=20,
                    calculate_probabilities=True,
                )
                
                st.info("🔄 Processing dataset and fitting BERTopic model...")
                topics, probs = topic_model.fit_transform(docs)
                st.success("✅ Model fitted!")
                
                # Show results
                st.subheader("📌 Topics")
                topics_info = topic_model.get_topic_info()
                st.dataframe(topics_info)
                
                st.subheader("📊 Topic Distribution")
                topic_dist = pd.Series(topics).value_counts().sort_index()
                st.bar_chart(topic_dist)
                
                # Coherence
                try:
                    coherence = calculate_coherence(topic_model, docs)
                    st.subheader("🎯 Topic Coherence")
                    st.metric("Overall Coherence (C_V)", f"{coherence:.4f}")
                except Exception as e:
                    st.warning(f"⚠️ Could not calculate coherence: {e}")
                
                st.success("✅ Analysis complete!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logging.error(f"Analysis error: {e}", exc_info=True)
        
        run_analysis()
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
