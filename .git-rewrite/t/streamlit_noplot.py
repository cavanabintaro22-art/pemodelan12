import streamlit as st
import pandas as pd
import re

st.title("📊 Topic Modeling (No Plot)")

uploaded = st.file_uploader("Upload CSV", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)
    st.success(f"✅ Loaded {len(df)} rows")
    
    if st.button("Analyze"):
        try:
            from bertopic import BERTopic
            from sentence_transformers import SentenceTransformer
            from sklearn.feature_extraction.text import CountVectorizer
            from umap import UMAP
            from hdbscan import HDBSCAN
            
            st.info("Loading models...")
            
            # Get text column
            if "full_text" in df.columns:
                text_col = "full_text"
            elif "text" in df.columns:
                text_col = "text"
            else:
                st.error("No text column found")
                st.stop()
            
            docs = df[text_col].dropna().astype(str).tolist()
            docs = [re.sub(r'\s+', ' ', d.lower()).strip()[:500] for d in docs if d.strip()]
            docs = docs[:500]  # Limit for testing
            
            st.write(f"Processing {len(docs)} documents...")
            
            # Models
            embedding = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            vectorizer = CountVectorizer(ngram_range=(1,2), min_df=2, max_df=0.9)
            umap = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
            hdbscan = HDBSCAN(min_cluster_size=20, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
            
            model = BERTopic(
                embedding_model=embedding,
                umap_model=umap,
                hdbscan_model=hdbscan,
                vectorizer_model=vectorizer,
                nr_topics="auto",
                min_topic_size=20,
                calculate_probabilities=True
            )
            
            st.info("Fitting model (this may take time)...")
            topics, probs = model.fit_transform(docs)
            
            st.success("✅ Done!")
            
            # Results
            info = model.get_topic_info()
            st.write(f"Topics found: {len(info) - 1}")  # -1 for outlier
            st.dataframe(info[info['Topic'] != -1])
            
            # Topic distribution
            topic_dist = pd.Series(topics).value_counts()
            st.write("Topic distribution:")
            st.write(topic_dist)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            st.write(traceback.format_exc())
