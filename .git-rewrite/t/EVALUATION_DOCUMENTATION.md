# 📊 Evaluasi Model untuk DTM Project

Dokumen ini menjelaskan metrik evaluasi yang penting untuk model stance classification dan topik. Fokus utamanya adalah F1 score, confusion matrix, dan evaluasi lain yang relevan.

---

## 1. Metrik Evaluasi Utama

### 1.1 Accuracy
Persentase prediksi model yang benar.

**Formula:**
```
accuracy = (TP + TN) / total_predictions
```

### 1.2 Precision
Proporsi prediksi positif yang benar.

**Formula:**
```
precision = TP / (TP + FP)
```

### 1.3 Recall
Proporsi kasus positif yang berhasil diidentifikasi.

**Formula:**
```
recall = TP / (TP + FN)
```

### 1.4 F1 Score
Harmonic mean dari precision dan recall.

**Formula:**
```
F1 = 2 * (precision * recall) / (precision + recall)
```

Menggunakan F1 score penting untuk mengukur performa model pada dataset tidak seimbang, karena memperhitungkan trade-off antara precision dan recall.

---

## 2. Confusion Matrix

Confusion matrix menyajikan ringkasan jumlah prediksi benar dan salah per kelas.

| Actual \ Predicted | POSITIVE | NEGATIVE | NEUTRAL |
|--------------------|----------|----------|---------|
| POSITIVE           | TP       | FN       | FN      |
| NEGATIVE           | FP       | TN       | FN      |
| NEUTRAL            | FP       | FP       | TP      |

Interpretasi:
- Baris menunjukkan label sebenarnya
- Kolom menunjukkan prediksi model
- Diagonal adalah prediksi benar
- Off-diagonal adalah kesalahan model

---

## 3. Evaluasi Stance Classification

Untuk masalah stance analysis di DTM, metrik yang penting adalah:
- Accuracy
- Precision (macro & weighted)
- Recall (macro & weighted)
- F1 score (macro & weighted)
- Confusion matrix
- Classification report per kelas

### Mengapa macro dan weighted?
- **Macro:** Melakukan rata-rata per kelas tanpa memperhatikan proporsi kelas, sehingga berguna untuk melihat performa di kelas minoritas.
- **Weighted:** Menghitung rata-rata berdasarkan support setiap kelas, sehingga mencerminkan distribusi data nyata.

---

## 4. Evaluasi Topic Modeling

Topic modeling dievaluasi dengan metrik lain, misalnya:
- Coherence score
- Relevance score dari expert
- Expert agreement
- Distinctiveness dan interpretability

Metrik topik lebih subjektif, karena melibatkan penilaian manusia terhadap kualitas topic.

---

## 5. File Evaluasi yang Dibuat

### `model_evaluation.py`
- `evaluate_classification(y_true, y_pred, labels=None)`
- `evaluate_stance_ground_truth(path, prediction_col, label_col, label_order)`
- `format_confusion_matrix(results)`
- `save_evaluation_results(results, path)`

### `evaluate.py`
- Script CLI untuk menjalankan evaluasi stance dengan ground truth CSV
- Menyimpan hasil ke `evaluation_results.json`
- Menampilkan summary, confusion matrix, dan classification report

---

## 6. Cara Menjalankan Evaluasi

1. Pastikan Anda memiliki ground truth stance file, misalnya:
   - `ground_truth_stance.csv`
   - Kolom minimal: `comment_id`, `model_prediction`, `expert_stance`

2. Jalankan command:

```bash
python evaluate.py ground_truth_stance.csv --output evaluation_results.json
```

3. Hasil evaluasi akan ditampilkan di terminal dan disimpan di `evaluation_results.json`.

---

## 7. Struktur Ground Truth Stance yang Direkomendasikan

Contoh kolom:
- `comment_id`
- `text_original`
- `preprocessed_text`
- `model_prediction`
- `model_confidence`
- `expert_stance`
- `expert_confidence`
- `agreement`
- `error_type`
- `expert_notes`

---

## 8. Interpretasi Hasil

### Contoh hasil evaluasi
```
Accuracy: 0.87
Precision (macro): 0.88
Recall (macro): 0.85
F1 Score (macro): 0.86
Precision (weighted): 0.87
Recall (weighted): 0.87
F1 Score (weighted): 0.87
```

### Langkah lanjutan
- Jika F1 score rendah di kelas `NEUTRAL`, perlu perbaikan pada isu ambiguity dan contextual understanding.
- Jika precision lebih rendah daripada recall, model terlalu sering memberikan prediksi positif/negatif yang salah.
- Jika recall rendah, model melewatkan banyak label yang benar.

---

## 9. Evaluasi Lain yang Penting

Selain metrik klasifikasi dasar, berikut metrik lain yang bisa diterapkan:
- **Support** per kelas: jumlah sesungguhnya tiap kelas
- **Macro-average** vs **weighted-average**
- **Cohen's Kappa**: untuk mengukur agreement antara model dan expert
- **Error type analysis**: negation, sarcasm, conditional statements
- **Confidence calibration**: apakah confidence model mencerminkan akurasi

---

## 10. Rekomendasi untuk Thesis

Gunakan hasil evaluasi ini untuk:
- Menyajikan tabel F1, precision, recall, accuracy
- Menampilkan confusion matrix sebagai tabel atau heatmap
- Menjelaskan gap antara model dan expert
- Menyebutkan area perbaikan: misalnya negation handling dan irony/sarcasm

---

## 11. File yang Disimpan

- `model_evaluation.py`
- `evaluate.py`
- `EVALUATION_DOCUMENTATION.md`

**Status:** ✅ Evaluasi model sudah siap digunakan dan didokumentasikan.
