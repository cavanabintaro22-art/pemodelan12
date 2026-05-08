# Bab 5: Implementasi Sistem

## 5.1 Pendahuluan

Bab ini menjelaskan implementasi teknis dari sistem Document Topic Modeling (DTM) untuk analisis teks media sosial Indonesia. Sistem dikembangkan menggunakan bahasa pemrograman Python dengan framework Streamlit untuk interface web interaktif.

## 5.2 Arsitektur Sistem

### 5.2.1 Komponen Utama
Sistem terdiri dari empat komponen utama:
1. **Data Ingestion Module**: Modul untuk memuat dan validasi data
2. **Preprocessing Pipeline**: Pipeline pemrosesan teks 8-tahap
3. **Modeling Engine**: Mesin untuk topic modeling dan stance analysis
4. **Visualization & Export**: Interface untuk visualisasi dan ekspor hasil

### 5.2.2 Alur Kerja Sistem
```
Data Input → Preprocessing → Topic Modeling → Stance Analysis → Visualization → Export
```

### 5.2.3 Struktur File
```
/workspaces/DTM/
├── streamlit_app.py          # Aplikasi utama Streamlit
├── app.py                     # Implementasi alternatif
├── model_evaluation.py        # Modul evaluasi model
├── evaluate.py                # Script CLI evaluasi
├── requirements.txt           # Dependencies Python
├── sample_data.csv           # Data sampel
└── sample_posts_comments.csv # Data komentar sampel
```

## 5.3 Teknologi dan Library

### 5.3.1 Framework Utama
- **Streamlit 1.28+**: Framework web untuk aplikasi data science
- **Python 3.8+**: Bahasa pemrograman utama
- **Pandas 1.5+**: Manipulasi dan analisis data
- **NumPy 1.21+**: Komputasi numerik

### 5.3.2 Library NLP dan ML
- **BERTopic 0.15+**: Topic modeling dengan BERT
- **Transformers 4.21+**: Model pre-trained dari HuggingFace
- **Sentence-Transformers**: Embedding teks multilingual
- **Scikit-learn 1.2+**: Algoritma machine learning

### 5.3.3 Library Pendukung
- **Plotly 5.10+**: Visualisasi interaktif
- **Matplotlib/Seaborn**: Plotting statis
- **Regex**: Pattern matching
- **Sastrawi**: Stemming bahasa Indonesia

## 5.4 Implementasi Preprocessing Pipeline

### 5.4.1 Fungsi `preprocess_text()`
```python
def preprocess_text(text):
    # 1. Pembersihan HTML dan URL
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # 2. Normalisasi teks
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    
    # 3. Tokenisasi
    tokens = word_tokenize(text)
    
    # 4. Penghapusan stopwords
    stop_words = set(stopwords.words('indonesian'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # 5. Stemming
    stemmer = StemmerFactory().create_stemmer()
    tokens = [stemmer.stem(word) for word in tokens]
    
    # 6. Filter panjang kata
    tokens = [word for word in tokens if len(word) > 2]
    
    return ' '.join(tokens)
```

### 5.4.2 Optimisasi Performa
- **Batch Processing**: Pemrosesan teks dalam batch untuk efisiensi memori
- **Caching**: Cache hasil preprocessing untuk data berulang
- **Logging**: Comprehensive logging untuk debugging dan monitoring
- **Error Handling**: Try-except blocks untuk robust operation

## 5.5 Implementasi Topic Modeling

### 5.5.1 Setup Model dengan Caching
```python
import streamlit as st
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

@st.cache_resource
def load_embedding_model():
    """Cache model embedding untuk performa optimal"""
    logging.info("Starting load_embedding_model")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    logging.info("Completed load_embedding_model")
    return model

# Setup BERTopic
embedding_model = load_embedding_model()
topic_model = BERTopic(embedding_model=embedding_model)
    min_topic_size=10,
    nr_topics="auto",
    language="multilingual"
)
```

### 5.5.2 Pipeline Topic Modeling
1. **Embedding**: Konversi teks ke vektor embedding
2. **Dimensionality Reduction**: UMAP untuk reduksi dimensi
3. **Clustering**: HDBSCAN untuk pengelompokan topik
4. **Topic Representation**: TF-IDF untuk kata-kata representatif

### 5.5.3 Caching untuk Analysis Results
```python
@st.cache_data
def cached_fit_transform(_topic_model, _docs):
    """Cached wrapper untuk BERTopic fit_transform"""
    logging.info(f"Starting cached fit_transform on {len(_docs)} documents")
    topics, probs = _topic_model.fit_transform(_docs)
    logging.info(f"Completed cached fit_transform: {len(set(topics))} topics found")
    return topics, probs

@st.cache_data
def cached_topics_over_time(_topic_model, _docs, _timestamps, _nr_bins=20):
    """Cached wrapper untuk topics over time calculation"""
    logging.info("Calculating cached topics over time")
    try:
        result = _topic_model.topics_over_time(_docs, _timestamps, nr_bins=_nr_bins)
    except ValueError as e:
        logging.warning(f"Error dengan nr_bins={_nr_bins}: {e}. Menggunakan nr_bins=10.")
        result = _topic_model.topics_over_time(_docs, _timestamps, nr_bins=10)
    logging.info("Completed cached topics over time calculation")
    return result
```

### 5.5.4 Logging Implementation
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Logging pada setiap step analysis
logging.info("Starting load_embedding_model")
logging.info("Completed cached fit_transform")
```

## 5.6 Implementasi Stance Analysis

### 5.6.1 Setup Model Stance dengan Caching
```python
from transformers import pipeline

@st.cache_resource
def load_sentiment_model():
    """Cache model sentiment untuk performa optimal"""
    logging.info("Starting load_sentiment_model")
    model = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    logging.info("Completed load_sentiment_model")
    return model

stance_model = load_sentiment_model()
```

### 5.6.2 Cached Stance Analysis
```python
@st.cache_data
def cached_stance_analysis(_sentiment_model, _comments_list, _batch_size=20):
    """Cached wrapper untuk stance analysis pada komentar"""
    logging.info(f"Starting cached stance analysis on {len(_comments_list)} comments")
    sentiments = []
    confidences = []
    
    total_batches = (len(_comments_list) + _batch_size - 1) // _batch_size
    
    for batch_idx in range(total_batches):
        start_idx = batch_idx * _batch_size
        end_idx = min((batch_idx + 1) * _batch_size, len(_comments_list))
        batch = _comments_list[start_idx:end_idx]
        
        batch_sentiments = _sentiment_model(batch)
        for sentiment in batch_sentiments:
            sentiments.append(sentiment['label'])
            confidences.append(sentiment['score'])
    
    logging.info("Completed cached stance analysis")
    return sentiments, confidences
```

### 5.6.3 Mapping Sentimen ke Stance
```python
def map_sentiment_to_stance(sentiment_label):
    mapping = {
        'LABEL_2': 'Pro',      # Positive
        'LABEL_0': 'Kontra',   # Negative  
        'LABEL_1': 'Netral'    # Neutral
    }
    return mapping.get(sentiment_label, 'Netral')
```

## 5.7 Interface Pengguna dengan Streamlit

### 5.7.1 Struktur Aplikasi
```python
def main():
    st.title("Document Topic Modeling - Analisis Media Sosial Indonesia")
    
    # Sidebar untuk konfigurasi
    with st.sidebar:
        st.header("Konfigurasi")
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        
    # Main content
    if uploaded_file:
        display_data_statistics(data)
        run_topic_modeling(data)
        run_stance_analysis(data)
```

### 5.7.2 Komponen UI Utama
- **File Uploader**: Upload data CSV dengan validasi format
- **Data Statistics Dashboard**: Tampilan statistik data real-time
- **Progress Bars**: Indikator kemajuan untuk setiap proses
- **Visualization Tabs**: Tab terpisah untuk hasil topic dan stance
- **Download Buttons**: Ekspor hasil dalam format CSV/JSON

### 5.7.3 State Management
Penggunaan `st.session_state` untuk menyimpan hasil analisis antar interaksi pengguna.

## 5.8 Sistem Evaluasi Model

### 5.8.1 Modul `model_evaluation.py`
```python
def evaluate_classification(y_true, y_pred):
    """Evaluasi klasifikasi dengan multiple metrics"""
    return {
        'f1_score': f1_score(y_true, y_pred, average='weighted'),
        'precision': precision_score(y_true, y_pred, average='weighted'),
        'recall': recall_score(y_true, y_pred, average='weighted'),
        'accuracy': accuracy_score(y_true, y_pred)
    }
```

### 5.8.2 Confusion Matrix Visualization
Implementasi heatmap confusion matrix menggunakan Plotly untuk analisis error klasifikasi.

### 5.8.3 Ground Truth Integration
Sistem untuk memuat dan membandingkan hasil model dengan ground truth dari expert validation.

## 5.9 Framework Validasi Expert

### 5.9.1 Interface Validasi
```python
def topic_validation_interface():
    """Interface untuk validasi topik oleh expert"""
    st.header("Validasi Topik oleh Expert")
    
    # Tampilkan topik untuk review
    for topic_id, topic_words in topics.items():
        with st.expander(f"Topik {topic_id}: {topic_words[:5]}"):
            rating = st.slider("Relevansi", 1, 5, key=f"topic_{topic_id}")
            comments = st.text_area("Komentar", key=f"comments_{topic_id}")
```

### 5.9.2 Penyimpanan Feedback
Penyimpanan feedback expert dalam format JSON untuk analisis iteratif dan perbaikan model.

## 5.10 Optimisasi Performa

### 5.10.1 Memory Management
- **Chunk Processing**: Pemrosesan data dalam chunk untuk menghindari out-of-memory
- **Garbage Collection**: Manual GC untuk cleanup memori
- **Efficient Data Structures**: Penggunaan pandas dengan dtypes optimal

### 5.10.2 Caching dan Persistence
- **Model Caching**: Cache model BERTopic untuk reuse
- **Result Persistence**: Simpan hasil analisis dalam session state
- **Disk Caching**: Cache embedding untuk dataset berulang

### 5.10.3 Error Handling
Comprehensive error handling dengan try-except blocks dan user-friendly error messages.

## 5.11 Testing dan Validation

### 5.11.1 Unit Testing
Test untuk setiap komponen:
- Preprocessing functions
- Model loading dan inference
- Data validation
- Export functionality

### 5.11.2 Integration Testing
End-to-end testing untuk workflow lengkap dari data input sampai hasil output.

### 5.11.3 Performance Benchmarking
Benchmarking untuk berbagai ukuran dataset dan konfigurasi model.

## 5.12 Deployment dan Maintenance

### 5.12.1 Environment Setup
- **Virtual Environment**: Isolasi dependencies dengan venv
- **Requirements.txt**: Pinning versi library untuk reproducibility
- **Docker Container**: Containerization untuk deployment konsisten

### 5.12.2 Monitoring dan Logging
- **Application Logging**: Log aktivitas aplikasi
- **Performance Monitoring**: Track waktu eksekusi dan resource usage
- **Error Reporting**: Sistem pelaporan error otomatis

## 5.13 Kesimpulan Implementasi

Implementasi sistem DTM ini menghasilkan aplikasi web yang robust dan user-friendly untuk analisis teks media sosial Indonesia. Integrasi antara teknik NLP terkini dengan interface yang intuitif memungkinkan pengguna non-teknis untuk melakukan analisis topik dan stance secara efektif.