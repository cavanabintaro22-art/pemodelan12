# Bab 4: Metodologi Penelitian

## 4.1 Pendahuluan

Bab ini menjelaskan metodologi penelitian yang digunakan dalam pengembangan sistem Document Topic Modeling (DTM) untuk analisis teks media sosial Indonesia. Penelitian ini mengadopsi pendekatan kuantitatif dengan integrasi teknik pemrosesan bahasa alami (NLP) dan pembelajaran mesin untuk mengidentifikasi topik dan analisis stance dalam data teks.

## 4.2 Metode Pengumpulan Data

### 4.2.1 Sumber Data
Data dikumpulkan dari platform media sosial Indonesia seperti Twitter dan Facebook, dengan fokus pada diskusi politik dan diplomasi internasional. Data mentah berupa postingan dan komentar pengguna dalam bahasa Indonesia.

### 4.2.2 Kriteria Pengumpulan
- Periode waktu: 2020-2024
- Bahasa: Indonesia
- Topik: Isu-isu diplomasi dan politik luar negeri
- Volume: Minimum 10.000 postingan untuk representasi yang memadai

### 4.2.3 Format Data
Data disimpan dalam format CSV dengan kolom:
- `text`: Konten teks postingan
- `timestamp`: Waktu posting
- `source`: Platform sumber
- `engagement`: Metrik engagement (likes, shares, comments)

## 4.3 Preprocessing Data Teks

### 4.3.1 Tahapan Preprocessing
Sistem menerapkan pipeline preprocessing 8-tahap yang komprehensif untuk teks bahasa Indonesia:

1. **Konversi ke String & Lowercase**: Memastikan input string dan standardisasi case
2. **Hapus URL**: Menghapus http://, https://, www. patterns
3. **Hapus Mention**: Menghapus @username untuk fokus pada content
4. **Hapus Hashtag (Keep Kata)**: Menghapus simbol # tetapi menyimpan kata
5. **Hapus Emoji & Unicode Special**: Menggunakan encode/decode ASCII
6. **Hapus Angka**: Menghapus digit 0-9
7. **Hapus Punctuation & Special Characters**: Membersihkan karakter non-alfabet
8. **Hapus Extra Whitespace**: Normalisasi spasi berlebih

### 4.3.2 Implementasi Teknis
```python
def preprocess_text(text):
    # Pipeline preprocessing lengkap
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#(\w+)', r'\1', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    return text
```

### 4.3.3 Optimisasi Preprocessing
- **Batch Processing**: Pengolahan data dalam batch untuk efisiensi memori
- **Error Handling**: Try-except blocks untuk robust preprocessing
- **Logging**: Tracking preprocessing steps dengan logging.info

## 4.4 Model Topic Modeling

### 4.4.1 Algoritma BERTopic
Menggunakan library BERTopic yang mengintegrasikan:
- **Sentence Transformers**: Untuk embedding teks (model: all-MiniLM-L6-v2)
- **UMAP**: Untuk dimensionality reduction
- **HDBSCAN**: Untuk clustering topik
- **TF-IDF**: Untuk representasi topik

### 4.4.2 Parameter Model
- `min_topic_size`: Default BERTopic (disesuaikan otomatis)
- `nr_topics`: "auto" (penentuan jumlah topik otomatis)
- `language`: "multilingual" (dukungan multi-bahasa)
- `embedding_model`: SentenceTransformer("all-MiniLM-L6-v2")

### 4.4.3 Optimisasi Model
- **Caching**: Model loading menggunakan @st.cache_resource
- **Batch Processing**: Analisis dalam batch untuk efisiensi
- **Error Handling**: Fallback untuk topics_over_time jika nr_bins terlalu besar

### 4.4.4 Evaluasi Topik
- **Topic Count**: Jumlah topik terdeteksi secara otomatis
- **Document Distribution**: Distribusi dokumen per topik
- **Temporal Analysis**: Topics over time dengan sliding window

## 4.5 Analisis Stance

### 4.5.1 Model Stance Detection
Menggunakan model pre-trained dari HuggingFace:
- **Model**: cardiffnlp/twitter-roberta-base-sentiment-latest
- **Framework**: Transformers library
- **Klasifikasi**: Positive, Negative, Neutral

### 4.5.2 Pipeline Analisis
1. Input teks preprocessing
2. Embedding dengan RoBERTa
3. Klasifikasi sentimen
4. Mapping ke stance: Pro, Kontra, Netral

### 4.5.3 Ground Truth Development
- **Expert Validation Framework**: Sistem validasi oleh 5 ahli diplomasi
- **Inter-rater Agreement**: Menggunakan Cohen's Kappa
- **Ground Truth Dataset**: 2.000 sampel terannotasi manual

## 4.6 Validasi dan Evaluasi Model

### 4.6.1 Metrik Evaluasi
- **F1-Score**: Harmonic mean precision dan recall
- **Confusion Matrix**: Analisis klasifikasi error
- **Precision & Recall**: Akurasi prediksi positif
- **Accuracy**: Tingkat kebenaran keseluruhan

### 4.6.2 Cross-Validation
- **K-Fold CV**: k=5 untuk validasi robust
- **Stratified Sampling**: Memastikan distribusi kelas seimbang

### 4.6.3 Expert Validation
- **Domain Expert Review**: Validasi hasil oleh ahli diplomasi
- **Qualitative Assessment**: Analisis konteks dan nuansa
- **Iterative Refinement**: Perbaikan model berdasarkan feedback

## 4.7 Analisis Data dan Statistik

### 4.7.1 Statistik Deskriptif
- Distribusi panjang teks
- Frekuensi kata kunci
- Tren temporal postingan
- Metrik engagement

### 4.7.2 Visualisasi Data
- Word clouds untuk topik dominan
- Time series analisis
- Heatmap korelasi antar variabel
- Scatter plots untuk clustering

## 4.8 Etika Penelitian dan Privasi

### 4.8.1 Perlindungan Data
- Anonimisasi data pengguna
- Compliance dengan GDPR dan regulasi Indonesia
- Informed consent untuk data sensitif

### 4.8.2 Bias Mitigation
- Balanced sampling across demographics
- Regular bias audits
- Transparency dalam algoritma

## 4.9 Kesimpulan Metodologi

Metodologi ini mengintegrasikan teknik NLP terkini dengan domain knowledge diplomasi untuk menghasilkan sistem DTM yang akurat dan dapat diandalkan. Pendekatan hybrid antara automated modeling dan expert validation memastikan validitas hasil analisis.