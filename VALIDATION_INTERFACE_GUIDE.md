# 📋 Expert Validation Interface - Implementation Guide

## Overview

File ini menjelaskan implementasi UI untuk expert validation dalam Streamlit app, termasuk fitur interaktif terbaru untuk presentasi dan evaluasi.

---

## 🎨 New Interactive UI Features (April 2026)

### 1. Interactive Data Filters
**Location:** Sidebar (muncul setelah analisis selesai)

**Implementation:**
```python
# Sidebar filters untuk real-time filtering
if st.session_state.get('analysis_done', False):
    st.sidebar.header("📊 Data Filters")
    
    # Topic filter
    available_topics = sorted([t for t in posts_df['Topik'].unique() if t != -1])
    selected_topics = st.sidebar.multiselect("Filter by Topics", available_topics, default=available_topics)
    
    # Stance filter  
    available_stances = sorted(comments_df['sentiment'].unique())
    selected_stances = st.sidebar.multiselect("Filter by Stance", available_stances, default=available_stances)
    
    # Confidence threshold
    min_confidence = st.sidebar.slider("Minimum Confidence Score", 0.0, 1.0, 0.0, 0.05)
    
    # Apply filters
    if st.sidebar.button("🔄 Apply Filters"):
        st.session_state['filters_applied'] = True
```

**Usage for Validation:**
- Filter data untuk fokus pada topik tertentu
- Exclude low-confidence predictions
- Compare results across different stance categories

### 2. Word Clouds per Topic
**Location:** Main content area, setelah Topics Over Time

**Implementation:**
```python
st.subheader("☁️ Word Clouds per Topic")
topic_model = st.session_state.get('topic_model')

if topic_model:
    available_topics = [t for t in topic_model.get_topics().keys() if t != -1]
    selected_topic_wc = st.selectbox("Select Topic for Word Cloud", available_topics)
    
    if selected_topic_wc:
        topic_words = topic_model.get_topic(selected_topic_wc)
        word_freq = {word: weight for word, weight in topic_words}
        
        wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate_from_frequencies(word_freq)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
```

**Usage for Validation:**
- Visual assessment of topic coherence
- Identify representative keywords
- Compare topic quality across different topics

### 3. Sample Comments Display
**Location:** Main content area, dalam Sentiment Analysis section

**Implementation:**
```python
st.subheader("📝 Sample Comments by Sentiment")

# Interactive sentiment selector
selected_sentiment = st.selectbox("Select sentiment to view sample comments:", sentiment_counts.index)

if selected_sentiment:
    sentiment_comments = filtered_comments_df[filtered_comments_df['sentiment'] == selected_sentiment]['full_text_comments']
    sample_comments = sentiment_comments.sample(min(5, len(sentiment_comments)), random_state=42)
    
    for idx, comment in enumerate(sample_comments, 1):
        with st.expander(f"💬 Sample {idx}"):
            st.write(comment)
            preprocessed = filtered_comments_df[filtered_comments_df['full_text_comments'] == comment]['full_text_comments_preprocessed'].iloc[0]
            st.markdown(f"**Preprocessed:** {preprocessed}")
```

**Usage for Validation:**
- Manual verification of stance classification accuracy
- Quality assessment of preprocessing pipeline
- Identify edge cases and misclassifications

---

## 1. Struktur Implementasi

### File yang Diperlukan:

```
validation_interface.py - UI untuk expert validation
├── Topic Validation Interface
├── Stance Validation Interface
├── Results Export
└── Metrics Dashboard
```

---

## 2. Topic Validation Interface

### Implementation Code:

```python
import streamlit as st
import pandas as pd
from datetime import datetime

def topic_validation_interface(topic_model, sample_topics=[0, 1, 2, 3, 4]):
    """
    Interface untuk expert validasi topics
    """
    st.sidebar.header("👤 Expert Information")
    expert_name = st.sidebar.text_input("Nama Expert:", key="expert_name")
    expert_org = st.sidebar.text_input("Institusi/Organisasi:", key="expert_org")
    
    st.header("🎯 Topic Validation Interface")
    
    # Inisialisasi session state untuk tracking
    if 'validation_data' not in st.session_state:
        st.session_state.validation_data = {}
    
    # Pilih topic untuk divalidasi
    selected_topic = st.selectbox(
        "Pilih Topic ID untuk divalidasi:",
        sample_topics,
        key="topic_selection"
    )
    
    # Tampilkan topic information
    topic_info = topic_model.get_topic(selected_topic)
    top_words = [word for word, _ in topic_info]
    
    st.subheader(f"📌 Topic {selected_topic}")
    st.write(f"**Top 10 Words:** {', '.join(top_words)}")
    
    # Tampilkan sample documents
    st.subheader("📄 Sample Documents")
    topic_docs = get_documents_for_topic(selected_topic)  # Custom function
    
    for idx, doc in enumerate(topic_docs[:5], 1):
        with st.expander(f"Document {idx}"):
            st.write(doc[:200] + "..." if len(doc) > 200 else doc)
    
    # Validation Form
    st.subheader("📋 Validation Rating")
    
    col1, col2 = st.columns(2)
    
    with col1:
        relevance = st.slider(
            "1. Relevance terhadap Kebijakan LN:",
            1, 5, 3,
            help="Seberapa relevan topik dengan kebijakan luar negeri?"
        )
        coherence = st.slider(
            "2. Coherence (Kohesi):",
            1, 5, 3,
            help="Seberapa koheren kata-kata membentuk konsep?"
        )
        distinctiveness = st.slider(
            "3. Distinctiveness (Keunikan):",
            1, 5, 3,
            help="Seberapa distinct dari topik lain?"
        )
    
    with col2:
        interpretability = st.slider(
            "4. Interpretability (Kemudahan Interpretasi):",
            1, 5, 3,
            help="Seberapa mudah memahami topik?"
        )
        completeness = st.slider(
            "5. Completeness (Kelengkapan):",
            1, 5, 3,
            help="Apakah aspek penting ada semua?"
        )
    
    # Overall Rating
    avg_rating = (relevance + coherence + distinctiveness + interpretability + completeness) / 5
    st.info(f"📊 Rata-rata Rating: {avg_rating:.2f}/5.0")
    
    # Status
    st.subheader("✅ Assessment Status")
    status = st.radio(
        "Status Validasi:",
        ["VALID", "NEEDS REVISION", "INVALID"],
        horizontal=True
    )
    
    # Expert Label
    st.subheader("🏷️ Suggested Label/Interpretation")
    expert_label = st.text_input(
        "Interpretasi topik ini (contoh: 'Kebijakan Bilateral Perdagangan'):",
        key="topic_label"
    )
    
    # Comments
    st.subheader("💬 Expert Comments")
    comments = st.text_area(
        "Berikan feedback & saran:",
        height=150,
        placeholder="Contoh: 'Topik ini mencerminkan... Saran perbaikan: ...'"
    )
    
    # Save Validation
    if st.button("💾 Simpan Validasi", key="save_topic_validation"):
        validation_record = {
            'timestamp': datetime.now(),
            'expert_name': expert_name,
            'expert_org': expert_org,
            'topic_id': selected_topic,
            'top_words': ', '.join(top_words),
            'relevance': relevance,
            'coherence': coherence,
            'distinctiveness': distinctiveness,
            'interpretability': interpretability,
            'completeness': completeness,
            'avg_rating': avg_rating,
            'status': status,
            'expert_label': expert_label,
            'comments': comments
        }
        
        st.session_state.validation_data[selected_topic] = validation_record
        st.success(f"✅ Validasi Topic {selected_topic} berhasil disimpan!")
        
        # Option to export
        if st.button("📥 Export Validasi", key="export_topic"):
            export_validation_to_csv(st.session_state.validation_data)
```

---

## 3. Stance Validation Interface

### Implementation Code:

```python
def stance_validation_interface(comments_df, sample_size=50):
    """
    Interface untuk expert validasi stance
    """
    st.sidebar.header("👤 Expert Information")
    expert_name = st.sidebar.text_input("Nama Expert:", key="expert_stance_name")
    expert_org = st.sidebar.text_input("Institusi/Organisasi:", key="expert_stance_org")
    
    st.header("🗣️ Stance Analysis Validation Interface")
    
    # Random sample comments
    if 'stance_validation_data' not in st.session_state:
        st.session_state.stance_validation_data = []
    
    # Progress bar
    progress = st.progress(0)
    
    for idx, (comment_id, row) in enumerate(comments_df.iterrows()):
        if idx >= sample_size:
            break
        
        # Update progress
        progress.progress((idx + 1) / sample_size)
        
        st.subheader(f"💬 Comment {idx + 1}/{sample_size}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**ORIGINAL TEXT:**")
            st.text_area(
                "Original:",
                row['full_text_comments'],
                height=80,
                disabled=True,
                key=f"original_{idx}"
            )
        
        with col2:
            st.markdown("**PREPROCESSED TEXT:**")
            st.text_area(
                "Preprocessed:",
                row['full_text_comments_preprocessed'],
                height=80,
                disabled=True,
                key=f"preprocessed_{idx}"
            )
        
        # Model Prediction
        with st.expander("🤖 Model Prediction"):
            model_stance = row.get('sentiment', 'N/A')
            model_conf = row.get('confidence', 0)
            st.info(f"**Model Prediksi:** {model_stance} (Confidence: {model_conf:.2%})")
        
        # Expert Judgment
        st.markdown("**👨‍💼 Expert Judgment:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            expert_stance = st.radio(
                "Stance terhadap kebijakan:",
                ["POSITIVE (Mendukung)", "NEGATIVE (Menolak)", "NEUTRAL (Netral)"],
                horizontal=False,
                key=f"stance_{idx}"
            )
            
            confidence = st.radio(
                "Confidence Level:",
                ["Very Confident", "Confident", "Somewhat", "Low", "Ambiguous"],
                key=f"confidence_{idx}"
            )
        
        with col2:
            agreement = st.checkbox(
                "✓ Setuju dengan model prediction",
                key=f"agreement_{idx}"
            )
            
            if not agreement:
                disagreement_reason = st.text_area(
                    "Jelaskan perbedaan dengan model:",
                    height=100,
                    key=f"disagreement_{idx}"
                )
            else:
                disagreement_reason = ""
        
        # Additional Feedback
        feedback = st.text_area(
            "Feedback tambahan:",
            height=80,
            placeholder="Nuansa apa yang tidak tertangkap model?",
            key=f"feedback_{idx}"
        )
        
        # Save this stance validation
        if st.button(f"💾 Simpan Validasi Comment {idx + 1}", key=f"save_stance_{idx}"):
            stance_record = {
                'timestamp': datetime.now(),
                'expert_name': expert_name,
                'comment_id': comment_id,
                'original_text': row['full_text_comments'],
                'preprocessed_text': row['full_text_comments_preprocessed'],
                'model_stance': model_stance,
                'model_confidence': model_conf,
                'expert_stance': expert_stance.split()[0],  # Extract POSITIVE/NEGATIVE/NEUTRAL
                'expert_confidence': confidence,
                'agreement': agreement,
                'disagreement_reason': disagreement_reason,
                'feedback': feedback
            }
            
            st.session_state.stance_validation_data.append(stance_record)
            st.success(f"✅ Validasi Comment {idx + 1} disimpan!")
        
        st.divider()
    
    # Export Results
    if st.button("📥 Export Semua Validasi Stance"):
        export_stance_validation_to_csv(st.session_state.stance_validation_data)
```

---

## 4. Metrics & Performance Dashboard

### Implementation Code:

```python
def validation_metrics_dashboard():
    """
    Dashboard untuk menampilkan metrics validasi
    """
    st.header("📊 Validation Metrics Dashboard")
    
    # Load validation results
    if os.path.exists('validation_results/'):
        topics_val = pd.read_csv('validation_results/topics_validation.csv')
        stance_val = pd.read_csv('validation_results/stance_validation.csv')
        
        # Tabs for different metrics
        tab1, tab2, tab3, tab4 = st.tabs([
            "📌 Topic Metrics",
            "🗣️ Stance Metrics",
            "👥 Expert Agreement",
            "🎯 Performance Summary"
        ])
        
        with tab1:
            st.subheader("Topic Validation Metrics")
            
            # Average Ratings
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                avg_relevance = topics_val['relevance'].mean()
                st.metric("Avg Relevance", f"{avg_relevance:.2f}/5")
            with col2:
                avg_coherence = topics_val['coherence'].mean()
                st.metric("Avg Coherence", f"{avg_coherence:.2f}/5")
            with col3:
                avg_distinct = topics_val['distinctiveness'].mean()
                st.metric("Avg Distinctiveness", f"{avg_distinct:.2f}/5")
            with col4:
                avg_interp = topics_val['interpretability'].mean()
                st.metric("Avg Interpretability", f"{avg_interp:.2f}/5")
            with col5:
                avg_complete = topics_val['completeness'].mean()
                st.metric("Avg Completeness", f"{avg_complete:.2f}/5")
            
            # Status Distribution
            status_counts = topics_val['status'].value_counts()
            st.bar_chart(status_counts)
        
        with tab2:
            st.subheader("Stance Validation Metrics")
            
            # Accuracy
            correct = (stance_val['agreement'] == True).sum()
            total = len(stance_val)
            accuracy = correct / total * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Accuracy", f"{accuracy:.1f}%")
            with col2:
                st.metric("Total Validated", total)
            with col3:
                st.metric("Agreement Rate", f"{correct}/{total}")
            
            # Per-class metrics
            st.subheader("Per-Class Performance")
            
            positive_acc = (stance_val[(stance_val['expert_stance'] == 'POSITIVE') & 
                                       (stance_val['agreement'] == True)].shape[0] / 
                           stance_val[stance_val['expert_stance'] == 'POSITIVE'].shape[0] * 100)
            negative_acc = (stance_val[(stance_val['expert_stance'] == 'NEGATIVE') & 
                                       (stance_val['agreement'] == True)].shape[0] / 
                           stance_val[stance_val['expert_stance'] == 'NEGATIVE'].shape[0] * 100)
            neutral_acc = (stance_val[(stance_val['expert_stance'] == 'NEUTRAL') & 
                                      (stance_val['agreement'] == True)].shape[0] / 
                          stance_val[stance_val['expert_stance'] == 'NEUTRAL'].shape[0] * 100)
            
            metrics_df = pd.DataFrame({
                'Stance': ['POSITIVE', 'NEGATIVE', 'NEUTRAL'],
                'Accuracy': [positive_acc, negative_acc, neutral_acc]
            })
            
            st.bar_chart(metrics_df.set_index('Stance'))
        
        with tab3:
            st.subheader("Inter-rater Reliability")
            
            # Cohen's Kappa calculation
            from sklearn.metrics import cohen_kappa_score
            
            # Example: comparing different experts
            # kappa = cohen_kappa_score(expert1_labels, expert2_labels)
            
            st.info("""
            **Inter-rater Reliability Metrics:**
            - Cohen's Kappa: Mengukur agreement antara rater
            - Target: κ ≥ 0.70 (Substantial Agreement)
            - κ > 0.81: Almost Perfect Agreement
            - κ 0.61-0.80: Substantial Agreement
            - κ 0.41-0.60: Moderate Agreement
            """)
        
        with tab4:
            st.subheader("Performance Summary")
            
            summary_col1, summary_col2 = st.columns(2)
            
            with summary_col1:
                st.markdown("### ✅ Validation Status")
                valid_topics = (topics_val['status'] == 'VALID').sum()
                revision_topics = (topics_val['status'] == 'NEEDS REVISION').sum()
                invalid_topics = (topics_val['status'] == 'INVALID').sum()
                
                st.write(f"✅ Valid Topics: {valid_topics}")
                st.write(f"🔄 Needs Revision: {revision_topics}")
                st.write(f"❌ Invalid: {invalid_topics}")
            
            with summary_col2:
                st.markdown("### 📊 Data Quality")
                st.write(f"Total Topics Validated: {len(topics_val)}")
                st.write(f"Total Stances Validated: {len(stance_val)}")
                st.write(f"Average Topic Quality: {topics_val['avg_rating'].mean():.2f}/5.0")
                st.write(f"Stance Accuracy: {accuracy:.1f}%")
```

---

## 5. Export Functions

### CSV Export:

```python
def export_validation_to_csv(validation_data):
    """Export topic validations ke CSV"""
    df = pd.DataFrame(validation_data).T
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download Topic Validations (CSV)",
        data=csv,
        file_name=f"topic_validations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def export_stance_validation_to_csv(validation_data):
    """Export stance validations ke CSV"""
    df = pd.DataFrame(validation_data)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download Stance Validations (CSV)",
        data=csv,
        file_name=f"stance_validations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
```

---

## 6. Integration dalam Main App

### Tambahkan di `streamlit_app.py`:

```python
# Di dalam else block (setelah display_data_statistics)

# Menu untuk Expert Validation
st.divider()

expert_mode = st.checkbox("🔐 Expert Validation Mode", help="Aktifkan untuk validasi hasil")

if expert_mode:
    st.warning("⚠️ Mode Validasi Expert - Hanya untuk expert yang authorized")
    
    validation_type = st.radio(
        "Pilih tipe validasi:",
        ["Topic Validation", "Stance Validation", "Metrics Dashboard"]
    )
    
    if validation_type == "Topic Validation":
        topic_validation_interface(topic_model if 'topic_model' in locals() else None)
    
    elif validation_type == "Stance Validation":
        stance_validation_interface(comments_df)
    
    else:
        validation_metrics_dashboard()
```

---

## 7. Deployment Setup

### Requirements tambahan:

```
scikit-learn>=0.24.0  # Untuk Cohen's Kappa
xlsxwriter>=3.0.0    # Untuk Excel export (optional)
```

---

## 8. Usage Flow

```
Expert Login
    ↓
Pilih Validation Type (Topic/Stance)
    ↓
Review Data & Expert Judgment
    ↓
Rate & Provide Feedback
    ↓
Save Validation
    ↓
View Metrics Dashboard
    ↓
Export Results (CSV/Excel)
```

---

**Status:** ✅ Implementation Guide Ready
