# 📊 Ground Truth Sample Dataset & Validation Examples

Dokumen ini berisi contoh konkret dari ground truth dataset yang akan dihasilkan dari proses validasi experts.

---

## 1. Sample Ground Truth - Topics

File: `ground_truth_topics.csv`

```csv
topic_id,model_top_words,expert_interpretation,relevance_score,coherence_score,distinctiveness_score,interpretability_score,completeness_score,avg_rating,status,expert_label,expert_notes
0,"kebijakan,diplomasi,bilateral,kerjasama,negara,hubungan,perjanjian,negosiasi,internasional,persetujuan",Topic ini menggambarkan kerjasama dan diplomasi bilateral antara Indonesia dengan negara lain.,5,5,4,5,4,4.6,VALID,Kerjasama Diplomasi Bilateral,"Topik ini sangat relevan dengan kebijakan luar negeri. Words yang dipilih model cukup representatif. Bisa lebih spesifik ke jenis kerjasama (perdagangan, keamanan, dll)"
1,"perdagangan,ekspor,impor,ekonomi,barang,tarif,industri,produk,pasar,komersial",Fokus pada aspek perdagangan dan ekonomi dalam hubungan internasional.,5,4,5,5,4,4.6,VALID,Perdagangan & Ekonomi Internasional,"Coherence agak berkurang karena 'barang' dan 'produk' cukup general. Namun distinctiveness bagus berbeda dari topic lain."
2,"krisis,konflik,zona,maritim,perbatasan,ketegangan,pertahanan,keamanan,pertanyaan,masa",Membahas isu-isu keamanan, khususnya terkait zona maritim dan perbatasan Indonesia.,4,5,5,4,5,4.6,VALID,Isu Keamanan Maritim & Perbatasan,"Very relevant untuk Indonesia. Model mengcapture isu strategis dengan baik. Label bisa lebih spesifik: 'Keamanan Maritim & Zona Eksklusif'"
3,"iklim,energi,lingkungan,karbon,perubahan,emisi,keberlanjutan,panel,tenaga,ramah",Membahas isu lingkungan dan energi dalam konteks kebijakan luar negeri.,4,4,4,4,3,3.8,NEEDS_REVISION,"Isu Lingkungan & Transisi Energi","Model bagus menangkap topik, tapi 'panel' dan 'tenaga' kurang clear. Saran: lebih fokus pada climate change dan renewable energy."
4,"pemerintah,presiden,menteri,luar,negeri,keputusan,pernyataan,resmi,kantor,departemen",Berisi informasi tentang struktur pemerintah dan institusi yang berhubungan dengan kebijakan LN.,2,2,2,3,2,2.2,INVALID,"Metadata Institution (Bukan Topic Substansi)","Ini lebih banyak metadata/noise daripada topik substansial. Preprocessing perlu ditingkatkan untuk menghilangkan words institutional ini."
```

---

## 2. Sample Ground Truth - Stance

File: `ground_truth_stance.csv`

```csv
comment_id,original_text,preprocessed_text,model_prediction,model_confidence,expert_stance,expert_confidence,agreement,error_type,expert_notes
c001,"Setuju 100% dengan kebijakan ini! Ini keputusan yang bijak untuk Indonesia 🇮🇩 👍👍","setuju dengan kebijakan ini ini keputusan yang bijak untuk indonesia",POSITIVE,0.95,POSITIVE,Very Confident,TRUE,NONE,"Clear positive stance. Model correctly identified."
c002,"Sangat tidak setuju! Ini akan merugikan negara kita. Kebijakan bodoh!","sangat tidak setuju ini akan merugikan negara kita kebijakan bodoh",NEGATIVE,0.92,NEGATIVE,Very Confident,TRUE,NONE,"Clear negative stance with strong language. Model handled negation well."
c003,"Hmm, sebagian setuju sebagian tidak. Ada pro dan kontra yang perlu dipertimbangkan.","hmm sebagian setuju sebagian tidak ada pro dan kontra yang perlu dipertimbangkan",NEUTRAL,0.68,NEUTRAL,Confident,TRUE,NONE,"Balanced perspective. Model correctly identified ambiguity."
c004,"Kebijakan ini akan menyelamatkan negara kita dari krisis. Sangat bagus!","kebijakan ini akan menyelamatkan negara kita dari krisis sangat bagus",NEGATIVE,0.72,POSITIVE,Very Confident,FALSE,Negation_Handling,"Model predicted NEGATIVE but clearly positive sentiment. Issue with 'menyelamatkan' (save/rescue). Needs negation context understanding."
c005,"Presiden membuat keputusan ini setelah konsultasi menyeluruh. Implementasi dimulai bulan depan.","presiden membuat keputusan ini setelah konsultasi menyeluruh implementasi dimulai bulan depan",NEUTRAL,0.85,NEUTRAL,Confident,TRUE,NONE,"Factual, informative. No clear stance expressed. Model correct."
c006,"Ini adalah langkah maju yang dibutuhkan untuk hubungan bilateral kita dengan negara tetangga.","ini adalah langkah maju yang dibutuhkan untuk hubungan bilateral kita dengan negara tetangga",POSITIVE,0.88,POSITIVE,Confident,TRUE,NONE,"Positive framing with 'langkah maju'. Model interpreted correctly."
c007,"Kebijakan ini sama saja seperti yang dilakukan pemerintah sebelumnya. Tidak ada inovasi.","kebijakan ini sama saja seperti yang dilakukan pemerintah sebelumnya tidak ada inovasi",NEGATIVE,0.76,NEGATIVE,Very Confident,TRUE,NONE,"Negative tone due to criticism about lack of innovation. Model got it right."
c008,"Saya tidak yakin apakah ini keputusan yang tepat atau tidak. Perlu waktu untuk lihat hasilnya.","saya tidak yakin apakah ini keputusan yang tepat atau tidak perlu waktu untuk lihat hasilnya",NEUTRAL,0.62,NEUTRAL,Very Confident,TRUE,NONE,"Uncertain/wait-and-see approach. Neutral classification appropriate."
c009,"Kebijakan ini TIDAK akan berhasil! Ini kesalahan besar!","kebijakan ini akan berhasil ini kesalahan besar",POSITIVE,0.65,NEGATIVE,Very Confident,FALSE,Negation_Handling,"Model missed strong negation 'TIDAK'. Text shows clear disapproval despite how preprocessing removed 'TIDAK'. Critical error."
c010,"Dukungan penuh untuk kebijakan internasional Indonesia yang forward-thinking seperti ini!","dukungan penuh untuk kebijakan internasional indonesia yang forwardthinking seperti ini",POSITIVE,0.91,POSITIVE,Very Confident,TRUE,NONE,"Explicit positive with 'dukungan penuh'. Model handled well."
```

---

## 3. Validation Statistics

### Metrics Summary:

```
TOPIC VALIDATION RESULTS:
========================
Total Topics Validated: 25
Valid Topics: 20 (80%)
Needs Revision: 3 (12%)
Invalid Topics: 2 (8%)

Average Ratings:
- Relevance: 4.32/5.0
- Coherence: 4.28/5.0
- Distinctiveness: 4.40/5.0
- Interpretability: 4.36/5.0
- Completeness: 4.12/5.0
- Overall: 4.30/5.0

Status: PASSED (>4.0 average)


STANCE VALIDATION RESULTS:
==========================
Total Comments Validated: 100
Correct Classifications: 87
Incorrect: 13
Accuracy: 87%

Per-Class Performance:
- POSITIVE: 92% accuracy (34/37 correct)
- NEGATIVE: 90% accuracy (27/30 correct)
- NEUTRAL: 76% accuracy (26/33 correct)

Error Analysis:
- Negation Handling: 8 errors (61.5%)
- Sarcasm Detection: 2 errors (15.4%)
- Conditional Statements: 2 errors (15.4%)
- Other: 1 error (7.7%)

Inter-rater Reliability:
- Cohen's Kappa: 0.83 (Almost Perfect Agreement)
- Agreement Rate: 87%
- Confidence Average: 0.88

Status: PASSED (>80% accuracy)
```

---

## 4. Error Analysis Report

### Top Error Patterns:

```
1. NEGATION HANDLING (8 occurrences - 61.5%)
   ==================================================
   Issue: Model fails to recognize negation in context
   
   Examples:
   - "TIDAK akan berhasil" → Model: POSITIVE, Expert: NEGATIVE
   - "bukan keputusan yang baik" → Model: POSITIVE, Expert: NEGATIVE
   
   Root Cause: Preprocessing removes some negation markers or 
               embedding model doesn't capture full negation context
   
   Recommended Fix:
   - Better negation handling in preprocessing
   - Consider syntax-aware preprocessing
   - Fine-tune with negation-heavy examples
   
   Impact: Medium (affects interpretation of disapproval)
   Priority: HIGH

2. SARCASM DETECTION (2 occurrences - 15.4%)
   ==================================================
   Issue: Sarcastic comments misclassified
   
   Examples:
   - "Oh yes, sangat genius policynya" [sarcastic] 
     → Model: POSITIVE, Expert: NEGATIVE
   
   Root Cause: Model treats literal meaning, not contextual intent
   
   Recommended Fix:
   - Add sarcasm examples to fine-tuning dataset
   - Consider linguistic markers of sarcasm
   - Increase training data size for edge cases
   
   Impact: Low (sarcasm relatively rare in dataset)
   Priority: MEDIUM

3. CONDITIONAL STATEMENTS (2 occurrences - 15.4%)
   ==================================================
   Issue: Conditional/hypothetical statements mishandled
   
   Examples:
   - "Jika ini diimplementasikan dengan baik, akan bagus"
     → Model: NEGATIVE, Expert: POSITIVE
   
   Root Cause: Model focuses on word frequency, not logical structure
   
   Recommended Fix:
   - Better contextual understanding through fine-tuning
   - Use larger model or more context
   
   Impact: Low (conditional statements less common)
   Priority: LOW
```

---

## 5. Expert Feedback Summary

### By Expert:

```
Expert 1: Dr. Budi Santoso (Diplomat, Kemenlu)
=========================================
Topics Validated: 12
Stance Validated: 35

Overall Assessment: "Model has good grasp of main topics. 
Preprocessing very helpful. Stance analysis needs work on negation."

Key Feedback:
- Topics are relevant and well-differentiated
- Some vocabulary could be more domain-specific
- Stance model struggles with complex sentences
- Consider fine-tuning with diplomatic language corpus

Rating: 4/5


Expert 2: Prof. Rina Wijaya (Political Analyst)
==============================================
Topics Validated: 13
Stance Validated: 32

Overall Assessment: "Strong performance overall. Topics align 
with actual discourse. Stance model is conservative with confidence."

Key Feedback:
- Topic labels are accurate
- Model could use more training data on minority classes
- Good at distinguishing neutral from positive/negative
- Consider domain adaptation for political terminology

Rating: 4.2/5


Expert 3: Dr. Hendra Kusuma (Linguist)
================================
Topics Validated: 10
Stance Validated: 33

Overall Assessment: "Preprocessing quality is excellent. 
Language understanding is good but could improve with linguistic features."

Key Feedback:
- Preprocessing effectively removes noise
- Missing some linguistic nuances
- Consider POS tagging for better context
- Indonesian-specific stopwords handling needed

Rating: 3.8/5
```

---

## 6. Recommended Improvements

### Prioritized Action Items:

```
PRIORITY 1 - CRITICAL (Implement immediately):
================================================
1. Negation Handling Enhancement
   - Implement negation-aware preprocessing
   - Add negation examples to fine-tuning data
   - Expected Impact: +8-10% accuracy improvement

2. Data Quality Improvement
   - Review preprocessing rules
   - Add linguistic-aware processing
   - Expected Impact: +5% quality improvement


PRIORITY 2 - HIGH (Implement soon):
===================================
1. Fine-tune Model with Ground Truth
   - Use 87 validated stance examples
   - Use 20 validated topics
   - Expected Impact: +5-8% accuracy gain

2. Domain-specific Language Handling
   - Add diplomatic vocabulary context
   - Improve political terminology understanding
   - Expected Impact: +3-5% relevance improvement

3. Confidence Calibration
   - Better confidence scoring
   - Uncertainty quantification
   - Expected Impact: Better reliability indication


PRIORITY 3 - MEDIUM (Enhance capabilities):
============================================
1. Sarcasm Detection
   - Build sarcasm detection model
   - Add sarcasm examples
   - Expected Impact: +2-3% accuracy for sarcastic comments

2. Contextual Understanding
   - Improve sentence-level context
   - Better multi-sentence document understanding
   - Expected Impact: +3-4% completeness

3. Multi-label Support
   - Some comments/topics have multiple aspects
   - Consider multi-label classification
   - Expected Impact: Better representation of complex opinions
```

---

## 7. Fine-tuning Data Preparation

### Convert to Fine-tuning Format:

```python
# Fine-tune Stance Model
from datasets import Dataset
import json

fine_tune_data = {
    "texts": [
        "setuju dengan kebijakan ini ini keputusan yang bijak untuk indonesia",
        "sangat tidak setuju ini akan merugikan negara kita kebijakan bodoh",
        "hmm sebagian setuju sebagian tidak ada pro dan kontra yang perlu dipertimbangkan",
        # ... more validated examples
    ],
    "labels": [
        1,  # POSITIVE
        0,  # NEGATIVE
        2,  # NEUTRAL
        # ... corresponding labels
    ]
}

# Create Dataset
dataset = Dataset.from_dict(fine_tune_data)

# Split train/eval
train_test_split = dataset.train_test_split(test_size=0.2, seed=42)

# Fine-tune model with this validated dataset
```

---

## 8. Baseline vs Fine-tuned Performance

### Comparison Table:

```
Metric                  Baseline    Fine-tuned    Improvement
===========================================================
Overall Accuracy        78%         87%           +9%
POSITIVE Accuracy       85%         92%           +7%
NEGATIVE Accuracy       82%         90%           +8%
NEUTRAL Accuracy        68%         76%           +8%
Negation Handling       45%         75%           +30%
Precision (avg)         0.79        0.88          +0.09
Recall (avg)            0.78        0.87          +0.09
F1-Score (avg)          0.78        0.87          +0.09

Topic Coherence         3.8/5       4.3/5         +0.5
Topic Relevance         4.0/5       4.6/5         +0.6
```

---

## 9. Implementation Checklist

```
PRE-VALIDATION:
[ ] Expert panel recruited (4-5 experts)
[ ] Training session completed
[ ] Rubric finalized
[ ] Sample data prepared

VALIDATION PHASE:
[ ] Topic validation completed (25 topics)
[ ] Stance validation completed (100 comments)
[ ] Inter-rater reliability ≥ 0.70
[ ] Consensus reached on conflicts

POST-VALIDATION:
[ ] Ground truth dataset compiled
[ ] Error analysis completed
[ ] Fine-tuning data prepared
[ ] Model fine-tuning executed
[ ] Performance validation done
[ ] Documentation completed

DEPLOYMENT:
[ ] Fine-tuned model deployed
[ ] Performance monitoring setup
[ ] Feedback mechanism in place
[ ] Expert review process documented
```

---

## 10. Next Steps

1. **Compile all validation forms** from experts
2. **Create ground truth CSV files** with validated data
3. **Calculate metrics** (accuracy, kappa, etc.)
4. **Conduct error analysis**
5. **Prepare fine-tuning dataset**
6. **Fine-tune models** with validated examples
7. **Evaluate improvements**
8. **Deploy updated models**
9. **Monitor performance** in production

---

**Status:** 📊 Sample Data & Framework Complete
**Next Action:** Start Expert Validation Campaign
