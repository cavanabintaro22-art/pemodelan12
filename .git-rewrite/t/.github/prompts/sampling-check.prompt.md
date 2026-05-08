---
description: "Check if data sampling for testing has been performed in the DTM project"
name: "Check Sampling Status"
argument-hint: "Provide any specific aspects to check or context about sampling"
agent: "agent"
tools: [read_file, grep_search, semantic_search]
---

# Check Sampling Status

This prompt addresses the query "kamu sudah lakukan Sampling dulu (buat testing)?" (Have you already done sampling first for testing?) by reviewing the project to determine if data sampling has been performed.

## Steps to Check:

1. **Review Preprocessing Documentation**:
   - Check PREPROCESSING_DOCUMENTATION.md for mentions of sampling
   - Look at DEVELOPMENT_LOG.md for sampling activities

2. **Examine Code and Data**:
   - Review app.py, evaluate.py, or model_evaluation.py for sampling code
   - Check sample_data.csv and sample_posts_comments.csv for sampled data

3. **Check Methodology and Implementation**:
   - See BAB_4_METHODOLOGY.md and BAB_5_IMPLEMENTATION.md for sampling details
   - Look at GROUND_TRUTH_SAMPLES.md for any sampling validation

4. **Summarize Findings**:
   - Report what sampling has been done
   - Note any testing data preparation
   - Suggest next steps if sampling is incomplete

Provide any additional context or specific files to focus on.