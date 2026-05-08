# Pemodelan Topik Dinamis

Pemodelan Topik Dinamis terhadap unggahan media sosial X dan stance analysist terhadap komentar pada kebijakan luar negeri

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pemodelan-topik-dinamis.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

## ✨ Features

### Core Analysis
- **Dynamic Topic Modeling**: BERTopic untuk pemodelan topik dinamis pada unggahan media sosial
- **Stance Analysis**: Analisis sikap (Pro/Netral/Kontra) pada komentar menggunakan IndoBERT
- **Topics Over Time**: Visualisasi evolusi topik seiring waktu
- **Model Evaluation**: Metrik evaluasi komprehensif termasuk topic coherence dan diversity metrics

### 🎨 Interactive UI/UX Features
- **📊 Data Filters**: Sidebar interaktif untuk filter berdasarkan topik, stance, dan confidence score
- **☁️ Word Clouds**: Visualisasi word cloud per topik untuk memahami kata kunci representatif
- **📝 Sample Comments**: Klik untuk lihat sampel komentar acak dan verifikasi klasifikasi model
- **📈 Real-time Filtering**: Semua visualisasi update secara real-time berdasarkan filter yang dipilih
- **🎯 Evaluation Dashboard**: Metrik coherence, diversity, dan distribusi topik dengan interpretasi
- **📝 Sample Comments**: Klik bar chart untuk melihat sampel komentar acak dan verifikasi klasifikasi model
- **📈 Real-time Filtering**: Semua visualisasi update secara real-time berdasarkan filter yang dipilih

### Data Processing
- **Preprocessing Pipeline**: Pembersihan teks komprehensif untuk bahasa Indonesia
- **Progress Tracking**: Progress bar informatif untuk setiap tahap analisis
- **Caching**: Optimisasi performa dengan caching untuk model dan hasil analisis

### Export & Download
- **Multiple Formats**: Download hasil dalam format CSV, HTML, dan TXT
- **Comprehensive Reports**: Laporan lengkap dengan statistik dan metrik evaluasi

## 📊 Sample Output

### Topics Over Time Visualization
![Topics Over Time](https://via.placeholder.com/600x300/4ECDC4/FFFFFF?text=Topics+Over+Time+Visualization)

### Sentiment Distribution with Interactive Filters
![Sentiment Analysis](https://via.placeholder.com/600x300/45B7D1/FFFFFF?text=Sentiment+Distribution+Chart)

### Word Cloud per Topic
![Word Cloud](https://via.placeholder.com/600x300/FF6B6B/FFFFFF?text=Word+Cloud+Visualization)
