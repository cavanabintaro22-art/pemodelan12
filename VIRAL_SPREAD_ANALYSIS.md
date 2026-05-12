# 🔥 Viral Spread Analysis - Dokumentasi Lengkap

## Overview
Fitur baru untuk menganalisis bagaimana posts diplomasi/kebijakan luar negeri menyebar secara viral di media sosial (Twitter/X). Fitur ini memanfaatkan duplicate posts (retweets) untuk memahami pola penyebaran pesan.

---

## 📊 Data Insights dari Dataset Awal

### Statistik Duplikat Posts
```
Total Posts: 13,023 records
Posts Unik: 6,082 unique texts
Duplicate Instances: 3,399 (53.3% dari dataset)
Viral Posts: 54 unique posts dengan reposts >1x
```

### Top 5 Paling Viral
| Rank | Text | Reposts | Unique Users | Spread Rate |
|------|------|---------|--------------|-------------|
| 1 | "Saya heran membaca pernyataan @Kemlu_RI re Venezuela..." | 709x | 10 | 48.16/hr |
| 2 | "Anggota dewan Malaysia marah bantuan dari negaranya..." | 290x | 223 | 19.66/hr |
| 3 | "@NataliusPigai2 Pak Dino sedang mengkritik inkompetensi..." | 279x | 272 | 18.93/hr |
| 4 | "Selamat Tahun Baru 2026. Semoga di tahun yang baru..." | 250x | 244 | 16.98/hr |
| 5 | "Bukannya dia udah di tempat yang seharusnya bisa..." | 229x | 226 | 15.54/hr |

---

## 🔍 Apa itu Duplicate Posts (Retweets)?

### Karakteristik
- **Text Content**: ✅ 100% SAMA (viral message)
- **Tweet ID**: ❌ BERBEDA (setiap retweet adalah tweet baru)
- **Username**: ❌ BERBEDA (orang berbeda yang mereposts)
- **User ID**: ❌ BERBEDA (user ID berbeda)
- **Timestamp**: ❌ BERBEDA (waktu posting berbeda)

### Contoh
```
Original Post oleh @diplomat_a:
"Kebijakan luar negeri harus konsisten..."
- Tweet ID: 2000100001
- Posted: 2026-01-05 10:00:00

Retweet by @user_b:
"Kebijakan luar negeri harus konsisten..."  ← SAMA
- Tweet ID: 2000100002 ← BEDA
- User: user_b ← BEDA
- Posted: 2026-01-05 10:05:00 ← BEDA

Retweet by @user_c:
"Kebijakan luar negeri harus konsisten..."  ← SAMA
- Tweet ID: 2000100003 ← BEDA
- User: user_c ← BEDA
- Posted: 2026-01-05 11:30:00 ← BEDA
```

---

## 📈 Fitur Dashboard

### Location di App
**Tab**: "🔥 Analisis Penyebaran Viral Posts"
**Posisi**: Setelah Stance Analysis Results

### 4 Tab Visualisasi

#### Tab 1: 📊 Statistik Top Posts
Menampilkan data top 10 most viral posts

**Visualisasi 1 - Bar Chart**:
- X-axis: Post text (first 80 chars)
- Y-axis: Number of reposts
- Berguna untuk: Identifikasi posts paling viral

**Visualisasi 2 - Scatter Plot**:
- X-axis: Unique Users (reach)
- Y-axis: Total Reposts (virality)
- Bubble Size: Spread Rate (posts/hora)
- Color: Intensity (Viridis scale)
- Berguna untuk: Korelasi reach vs virality

#### Tab 2: ⏱️ Timeline Penyebaran
Menampilkan timeline top 5 most viral posts

**Visualisasi - Line Chart**:
- X-axis: Timestamp (per jam)
- Y-axis: Jumlah repost baru dalam jam tersebut
- Multiple lines: Setiap line = 1 viral post
- Berguna untuk: Lihat pola penyebaran temporalnya

**Insights**:
- Garis yang curam = penyebaran cepat
- Garis yang flat = penyebaran lambat
- Peak = waktu paling banyak repost dalam jam tersebut

#### Tab 3: 🔥 Heatmap Aktivitas
Menampilkan distribusi posts per hari & jam

**Visualisasi - Heatmap**:
- X-axis: Jam (0-23, 24-hour format)
- Y-axis: Hari (Monday-Sunday)
- Color Intensity: Jumlah posts (warna merah = banyak)
- Berguna untuk: Identifikasi peak activity time

**Insights**:
- Jam berapa paling banyak posts?
- Hari apa paling aktif?
- Kapan sebaiknya posting untuk viral?

#### Tab 4: 📋 Tabel Lengkap
Tabel semua viral posts dengan metrics

**Kolom**:
| Kolom | Deskripsi |
|-------|-----------|
| Post Text | Konten post (first 80 chars) |
| Reposts | Total berapa kali post di-retweet |
| Users | Berapa unique user yang mereposts |
| Hours Span | Berapa jam dari post pertama ke terakhir |
| Rate/Hr | Kecepatan penyebaran (posts/jam) |

**Action**:
- Sort: Klik header kolom untuk sort
- Search: Gunakan browser search (Ctrl+F)
- Export: Download sebagai CSV untuk analisis lebih lanjut

---

## 📊 Metrics & Interpretasi

### Metrics yang Ditampilkan

#### 🔥 Posts Viral
**Definisi**: Jumlah unique posts yang muncul >1 kali
**Contoh**: 54 unique posts

**Interpretasi**:
- Tinggi (>100) = Banyak pesan viral di dataset
- Rendah (<10) = Sedikit pesan yang berhasil viral

#### 🔄 Total Repost
**Definisi**: Total instances dari semua viral posts
**Contoh**: 3,399 total reposts

**Interpretasi**:
- Tinggi = Dataset penuh dengan retweets (beryakin pesan dikurasi)
- Rendah = Dataset lebih original content

#### 👥 Rata-rata Users
**Definisi**: Rata-rata unique users per viral post
**Contoh**: ~163 users per post

**Interpretasi**:
- Tinggi (100+) = Post menjangkau banyak orang berbeda
- Rendah (<10) = Post hanya di-retweet oleh sedikit group

#### ⚡ Max Spread Rate
**Definisi**: Kecepatan penyebaran tertinggi (reposts per jam)
**Contoh**: 48.16 posts/jam

**Interpretasi**:
- 100+ = SANGAT VIRAL (spreading exponentially)
- 10-100 = VIRAL (spreading quickly)
- <10 = MODERATE (spreading slowly)

---

## 🎯 Use Cases

### 1. Identifikasi Political Messages yang Viral
```
Pertanyaan: Pesan diplomatik mana yang paling resonates?
Jawaban: Lihat Tab 1 Bar Chart - Post dengan repost terbanyak
Action: Analisis isi/tone post yang viral
```

### 2. Lihat Kapan Posts Paling Aktif
```
Pertanyaan: Jam/hari berapa yang sebaiknya post untuk viral?
Jawaban: Lihat Tab 3 Heatmap - Red areas paling aktif
Action: Schedule posts saat prime time
```

### 3. Analisis Reach & Influence
```
Pertanyaan: Post mana yang paling mempengaruhi banyak orang?
Jawaban: Lihat Tab 2 Scatter - Bubble besar = reach luas
Action: Identifikasi influential political messages
```

### 4. Korelasi Topik dengan Viral Pattern
```
Pertanyaan: Topik mana yang lebih viral?
Jawaban: Export Tab 4 data + join dengan topic data
Action: Analisis topic_id yang paling banyak viral
```

### 5. Timeline Analisis Crisis/Event
```
Pertanyaan: Kapan tension/crisis terjadi di Twitter?
Jawaban: Lihat Tab 2 Timeline - Spike = peak crisis time
Action: Cross-reference dengan real-world events
```

---

## 💾 Export & Download

### Download Viral Analysis
- **Format**: CSV
- **Lokasi**: Tab 4 (Tabel Lengkap) - tombol "💾 Download"
- **Konten**: Semua viral posts dengan metrics
- **Use**: Untuk post-processing di Excel/R/Python

### Kolom CSV
```
Post Text
Reposts
Users
Hours Span
Rate/Hr
```

---

## 🔧 Technical Details

### Functions dalam Code

#### 1. `analyze_viral_spread(df)`
```python
- Input: DataFrame dengan kolom 'full_text' dan 'created_at'
- Output: DataFrame dengan viral posts dan metrics
- Proses:
  1. Group by full_text (identify duplicates)
  2. Hitung unique users per post
  3. Hitung time span (first - last timestamp)
  4. Hitung spread rate (reposts / hours)
```

#### 2. `visualize_viral_timeline(df, viral_posts_info)`
```python
- Input: DataFrame + viral_posts_info dari analyze_viral_spread
- Output: Plotly line chart
- Visualisasi: Top 5 viral posts + hourly distribution
```

#### 3. `visualize_viral_heatmap(df)`
```python
- Input: DataFrame dengan 'created_at'
- Output: Plotly heatmap
- Visualisasi: Day x Hour matrix
```

#### 4. `visualize_viral_statistics(viral_posts_info)`
```python
- Input: viral_posts_info DataFrame
- Output: 2 Plotly figures (bar chart + scatter)
- Visualisasi: Top posts + users vs reposts correlation
```

---

## ⚠️ Limitations & Considerations

### 1. Data Quality
- **Timestamps**: Format mixed (ISO 8601 + Twitter format) - diparsing dengan best-effort
- **Username**: Beberapa missing values (NaN)
- **Assumption**: Duplicate text = pasti retweet (bisa ada false matches)

### 2. Tidak Tercakup
- ❌ Retweet dengan comment/quote (text berbeda)
- ❌ Deleted posts (tidak dalam dataset)
- ❌ Quote tweets (counted as unique)
- ❌ Mentions (tidak dihitung sebagai retweet)

### 3. Performance
- Dataset <100K posts: ⚡ Instant (~1 detik)
- Dataset 100K-1M posts: ⏱️ Fast (~5-10 detik)
- Dataset >1M posts: 🐌 Slow (~30 detik+)

---

## 🚀 Future Enhancements

### Possible Additions
1. **Network Graph**: Social network dari retweets
2. **Sentiment Over Time**: Bagaimana sentiment berubah seiring penyebaran
3. **Topic + Viral**: Heatmap topik popularity + viral intensity
4. **Influencer Detection**: Siapa yang mulai menyebarkan post
5. **Correlation Analysis**: Real-world events vs viral spikes
6. **Anomaly Detection**: Unusual viral patterns (bot behavior?)

---

## 📖 References

- **Viral Coefficient**: Posts/hour * Hours Active
- **Reach**: Unique users who engaged with post
- **Virality**: Total spread / unique users
- **Spread Rate**: Posts per unit time (hour/day)
- **Influence**: Number of unique users affected

---

## 🤝 Integration dengan Feature Lain

### Dengan Topic Modeling
```
Topic ID + Viral Analysis =
Tahu topik mana yang paling viral
```

### Dengan Stance Analysis
```
Sentiment + Viral Analysis =
Tahu apakah posts pro/con lebih viral
```

### Dengan Time Analysis
```
Timeline + Viral Analysis =
Temporal pattern dari political discourse
```

---

## 📞 Support & Questions

**Untuk debugging:**
1. Check apakah column 'full_text' dan 'created_at' exist
2. Verify timestamp format valid
3. Check untuk missing values (NaN)

**Common Issues:**
- Heatmap kosong? → Kemungkinan timestamp sangat compressed
- Timeline error? → Timestamps tidak properly formatted
- Scatter plot weird? → Ada outliers dalam data

---

Dokumentasi v1.0 | Created: May 12, 2026
