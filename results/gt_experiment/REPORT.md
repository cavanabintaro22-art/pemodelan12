# Evaluation Report

## Metrics
   label  precision  recall       f1  support
Positive   0.888889     1.0 0.941176        8
Negative   1.000000     0.8 0.888889       10
 Neutral   0.666667     0.8 0.727273        5

## Confusion Matrix
                 pred_Positive  pred_Negative  pred_Neutral
actual_Positive              8              0             0
actual_Negative              0              8             2
actual_Neutral               1              0             4

- Total matched examples: 23
- Total errors: 3

## Top 10 Error Examples
- Text: @P3gEl Maaf ya kak, Presiden, wapres dan pejabat di negeri ini memang gak punya ...
  - Expected: Negative | Predicted: Neutral (0.3)

- Text: #intinyadeh lebih dr 100 org Indonesia kabur dr Chrey Thum Kamboja. Mereka ngaku...
  - Expected: Negative | Predicted: Neutral (0.3)

- Text: Hmm, sebagian setuju sebagian tidak. Ada pro dan kontra yang perlu dipertimbangk...
  - Expected: Neutral | Predicted: Positive (0.48)
