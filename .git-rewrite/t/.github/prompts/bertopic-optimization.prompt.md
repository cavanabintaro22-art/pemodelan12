---
description: "Check if BERTopic optimization has been performed in the DTM project"
name: "Check BERTopic Optimization Status"
argument-hint: "Provide any specific aspects to check or context"
agent: "agent"
tools: [read_file, grep_search, semantic_search]
---

# Check BERTopic Optimization Status

This prompt addresses the query "apakah kamu sudah lakukan Optimasi BERTopic?" (Have you already done BERTopic optimization?) by reviewing the project to determine if optimization has been performed.

## Steps to Check:

1. **Review Logs and Documentation**:
   - Check DEVELOPMENT_LOG.md for mentions of optimization
   - Look at CHANGELOG.md for recent changes related to BERTopic
   - Examine EVALUATION_DOCUMENTATION.md and VERIFICATION_RECORD.md

2. **Examine Code**:
   - Review model_evaluation.py and evaluate.py for optimization code
   - Look for parameter tuning, hyperparameter searches, or evaluation metrics

3. **Check Results**:
   - See BAB_6_RESULTS.md for any optimization results
   - Look at sample outputs or validation reports

4. **Summarize Findings**:
   - Report what optimizations have been done
   - Note any pending optimizations
   - Suggest next steps if needed

Provide any additional context or specific files to focus on.