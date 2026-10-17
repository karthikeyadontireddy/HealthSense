# Diabetes Model Improvement Experiment

Run timestamp: `2026-09-09T09:13:27.080363+00:00`  
Source: `https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv`  
Production artifact status: `research_v1` was not modified.
Review artifact: `experiments\artifacts\diabetes_research_v2_candidate` (`research_v2_candidate`, inactive).

## Executive conclusion

The baseline is `current_5__zero_as_missing__median__logistic__balanced__c1`. The top candidate by training-only cross-validation ROC-AUC/F1 is `all_8__zero_as_missing__mean__logistic__balanced__c0_1`.
On the fixed seed-42 holdout, the candidate accuracy is **0.7078** versus **0.6948** for baseline; F1 is **0.6154** versus **0.5841**, and ROC-AUC is **0.8100** versus **0.7857**.
Five-seed robustness gives candidate mean F1 **0.6325 +/- 0.0414** and mean ROC-AUC **0.8218 +/- 0.0327**, versus baseline F1 **0.6030 +/- 0.0548** and ROC-AUC **0.8135 +/- 0.0329**.
The candidate is scientifically preferable for further review; this is not approval to replace production. The fixed-holdout accuracy difference is +0.0130, and no claim of 85% accuracy is made.

## Baseline

- Model: Logistic Regression, class-weight balanced, `C=1.0`.
- Features: Glucose, BloodPressure, Insulin, BMI, Age.
- Zero policy: Glucose, BloodPressure, SkinThickness, Insulin, and BMI zeros become missing; median imputation is fitted within each training pipeline.
- Scaling: StandardScaler inside the Logistic Regression pipeline.
- Fixed holdout: accuracy 0.6948, precision 0.5593, recall 0.6111, F1 0.5841, ROC-AUC 0.7857, Brier 0.1919.
- Confusion matrix: `[[74, 26], [21, 33]]`.

## Controlled protocol

1. The remote source was read without modification; the original data file was not written.
2. A single stratified 80/20 split with seed 42 was created before candidate selection. The test partition was not used for tuning or selection.
3. Candidate selection used only stratified five-fold cross-validation on the training partition, ranking ROC-AUC first and F1 second.
4. Every imputer and scaler was inside the candidate pipeline and fit only on each training fold.
5. Robustness used independent stratified 80/20 splits with seeds 42, 7, 21, 100, 2026; it was not used to tune hyperparameters.
6. No SMOTE or other resampling was used.

## Candidate results

All candidates were evaluated. Holdout values are descriptive only; candidate selection was based on training CV.

| Candidate | CV accuracy | CV F1 | CV ROC-AUC | Test accuracy | Test F1 | Test ROC-AUC | Test Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| `all_8__zero_as_missing__mean__logistic__balanced__c0_1` | 0.7687 +/- 0.0071 | 0.6825 +/- 0.0143 | 0.8462 +/- 0.0137 | 0.7078 | 0.6154 | 0.8100 | 0.1814 |
| `all_8__zero_as_missing__median__logistic__balanced__c0_1` | 0.7671 +/- 0.0091 | 0.6823 +/- 0.0188 | 0.8450 +/- 0.0146 | 0.7078 | 0.6154 | 0.8104 | 0.1811 |
| `all_8__zero_as_missing__mean__logistic__balanced__c1` | 0.7638 +/- 0.0115 | 0.6753 +/- 0.0149 | 0.8449 +/- 0.0165 | 0.7338 | 0.6496 | 0.8117 | 0.1818 |
| `all_8__zero_as_missing__median__logistic__balanced__c1` | 0.7622 +/- 0.0124 | 0.6724 +/- 0.0149 | 0.8444 +/- 0.0180 | 0.7338 | 0.6496 | 0.8126 | 0.1814 |
| `all_8__zero_as_missing__mean__logistic__balanced__c10` | 0.7638 +/- 0.0132 | 0.6753 +/- 0.0181 | 0.8440 +/- 0.0174 | 0.7338 | 0.6496 | 0.8122 | 0.1819 |
| `all_8__zero_as_missing__mean__logistic__unweighted__c1` | 0.7882 +/- 0.0221 | 0.6585 +/- 0.0225 | 0.8440 +/- 0.0199 | 0.6948 | 0.5253 | 0.8122 | 0.1757 |
| `all_8__zero_as_missing__median__logistic__balanced__c10` | 0.7622 +/- 0.0124 | 0.6724 +/- 0.0149 | 0.8439 +/- 0.0189 | 0.7338 | 0.6496 | 0.8124 | 0.1815 |
| `all_8__zero_as_missing__mean__logistic__balanced__c10__unscaled` | 0.7622 +/- 0.0124 | 0.6724 +/- 0.0149 | 0.8439 +/- 0.0174 | 0.7338 | 0.6496 | 0.8120 | 0.1819 |
| `all_8__zero_as_missing__mean__logistic__balanced__c1__unscaled` | 0.7638 +/- 0.0132 | 0.6739 +/- 0.0163 | 0.8438 +/- 0.0187 | 0.7273 | 0.6379 | 0.8117 | 0.1823 |
| `all_8__zero_as_missing__median__logistic__balanced__c10__unscaled` | 0.7638 +/- 0.0132 | 0.6739 +/- 0.0163 | 0.8438 +/- 0.0191 | 0.7338 | 0.6496 | 0.8124 | 0.1815 |
| `all_8__zero_as_missing__median__logistic__unweighted__c1__unscaled` | 0.7882 +/- 0.0244 | 0.6563 +/- 0.0325 | 0.8438 +/- 0.0216 | 0.7013 | 0.5400 | 0.8130 | 0.1761 |
| `all_8__zero_as_missing__median__logistic__balanced__c1__unscaled` | 0.7638 +/- 0.0132 | 0.6739 +/- 0.0171 | 0.8434 +/- 0.0194 | 0.7338 | 0.6496 | 0.8126 | 0.1818 |
| `all_8__zero_as_missing__median__logistic__unweighted__c1` | 0.7882 +/- 0.0213 | 0.6545 +/- 0.0273 | 0.8434 +/- 0.0207 | 0.7078 | 0.5455 | 0.8130 | 0.1754 |
| `all_8__zero_as_missing__mean__logistic__unweighted__c1__unscaled` | 0.7882 +/- 0.0213 | 0.6601 +/- 0.0244 | 0.8429 +/- 0.0204 | 0.7013 | 0.5400 | 0.8115 | 0.1764 |
| `all_8__zero_as_missing__mean__logistic__balanced__c0_1__unscaled` | 0.7557 +/- 0.0104 | 0.6663 +/- 0.0145 | 0.8413 +/- 0.0203 | 0.7013 | 0.6102 | 0.8070 | 0.1843 |
| `all_8__zero_as_missing__median__logistic__balanced__c0_1__unscaled` | 0.7557 +/- 0.0158 | 0.6650 +/- 0.0183 | 0.8408 +/- 0.0217 | 0.7143 | 0.6207 | 0.8081 | 0.1839 |
| `all_8__zero_as_missing__mean__random_forest__unweighted__depth4` | 0.7704 +/- 0.0156 | 0.6194 +/- 0.0245 | 0.8392 +/- 0.0215 | 0.7208 | 0.5376 | 0.7972 | 0.1726 |
| `all_8__zero_as_missing__mean__random_forest__balanced__depth4` | 0.7671 +/- 0.0242 | 0.6953 +/- 0.0257 | 0.8392 +/- 0.0217 | 0.7403 | 0.6774 | 0.8133 | 0.1760 |
| `all_8__zero_as_missing__median__random_forest__unweighted__depth4` | 0.7736 +/- 0.0155 | 0.6272 +/- 0.0213 | 0.8391 +/- 0.0206 | 0.7208 | 0.5376 | 0.7985 | 0.1725 |
| `all_8__zero_as_missing__median__random_forest__balanced__depth4` | 0.7655 +/- 0.0209 | 0.6939 +/- 0.0198 | 0.8387 +/- 0.0205 | 0.7273 | 0.6613 | 0.8126 | 0.1762 |
| `current_5__zero_as_missing__median__random_forest__unweighted__depth4` | 0.7687 +/- 0.0180 | 0.6286 +/- 0.0150 | 0.8364 +/- 0.0271 | 0.7338 | 0.5773 | 0.8033 | 0.1703 |
| `current_5__zero_as_missing__mean__random_forest__unweighted__depth4` | 0.7687 +/- 0.0235 | 0.6288 +/- 0.0276 | 0.8357 +/- 0.0272 | 0.7338 | 0.5773 | 0.8037 | 0.1705 |
| `current_5__zero_as_missing__median__random_forest__balanced__depth4` | 0.7622 +/- 0.0187 | 0.6959 +/- 0.0199 | 0.8353 +/- 0.0261 | 0.7468 | 0.6829 | 0.8104 | 0.1739 |
| `all_8__raw_zeros__median__logistic__balanced__c10__unscaled` | 0.7605 +/- 0.0175 | 0.6794 +/- 0.0236 | 0.8349 +/- 0.0375 | 0.7338 | 0.6496 | 0.8250 | 0.1746 |
| `all_8__raw_zeros__median__logistic__balanced__c10` | 0.7589 +/- 0.0175 | 0.6779 +/- 0.0217 | 0.8348 +/- 0.0373 | 0.7338 | 0.6496 | 0.8252 | 0.1745 |
| `all_8__raw_zeros__median__logistic__balanced__c1` | 0.7589 +/- 0.0175 | 0.6779 +/- 0.0217 | 0.8348 +/- 0.0372 | 0.7338 | 0.6496 | 0.8248 | 0.1745 |
| `current_5__zero_as_missing__mean__random_forest__balanced__depth4` | 0.7589 +/- 0.0188 | 0.6919 +/- 0.0163 | 0.8348 +/- 0.0251 | 0.7468 | 0.6829 | 0.8115 | 0.1743 |
| `all_8__raw_zeros__median__logistic__balanced__c0_1` | 0.7622 +/- 0.0198 | 0.6795 +/- 0.0249 | 0.8346 +/- 0.0352 | 0.7403 | 0.6610 | 0.8211 | 0.1746 |
| `current_5__zero_as_missing__mean__logistic__balanced__c0_1` | 0.7524 +/- 0.0225 | 0.6667 +/- 0.0262 | 0.8340 +/- 0.0194 | 0.6883 | 0.5862 | 0.7833 | 0.1917 |
| `all_8__raw_zeros__median__logistic__balanced__c1__unscaled` | 0.7605 +/- 0.0175 | 0.6794 +/- 0.0236 | 0.8339 +/- 0.0380 | 0.7403 | 0.6610 | 0.8244 | 0.1749 |
| `current_5__zero_as_missing__median__logistic__balanced__c0_1` | 0.7524 +/- 0.0194 | 0.6666 +/- 0.0243 | 0.8336 +/- 0.0197 | 0.6883 | 0.5862 | 0.7846 | 0.1913 |
| `all_8__raw_zeros__median__logistic__unweighted__c1` | 0.7882 +/- 0.0177 | 0.6579 +/- 0.0241 | 0.8334 +/- 0.0397 | 0.7143 | 0.5600 | 0.8230 | 0.1679 |
| `current_5__zero_as_missing__median__logistic__balanced__c0_1__unscaled` | 0.7508 +/- 0.0128 | 0.6620 +/- 0.0201 | 0.8332 +/- 0.0226 | 0.6948 | 0.5841 | 0.7859 | 0.1921 |
| `current_5__zero_as_missing__median__logistic__balanced__c1` | 0.7524 +/- 0.0153 | 0.6635 +/- 0.0215 | 0.8332 +/- 0.0219 | 0.6948 | 0.5841 | 0.7857 | 0.1919 |
| `current_5__zero_as_missing__mean__logistic__balanced__c1` | 0.7508 +/- 0.0172 | 0.6621 +/- 0.0239 | 0.8331 +/- 0.0210 | 0.7013 | 0.5965 | 0.7859 | 0.1923 |
| `current_5__zero_as_missing__median__logistic__balanced__c10` | 0.7508 +/- 0.0128 | 0.6620 +/- 0.0201 | 0.8331 +/- 0.0226 | 0.6948 | 0.5841 | 0.7861 | 0.1921 |
| `current_5__zero_as_missing__median__logistic__balanced__c1__unscaled` | 0.7508 +/- 0.0128 | 0.6620 +/- 0.0201 | 0.8331 +/- 0.0228 | 0.6948 | 0.5841 | 0.7861 | 0.1921 |
| `current_5__zero_as_missing__median__logistic__balanced__c10__unscaled` | 0.7508 +/- 0.0128 | 0.6620 +/- 0.0201 | 0.8331 +/- 0.0228 | 0.6948 | 0.5841 | 0.7861 | 0.1921 |
| `current_5__zero_as_missing__mean__logistic__unweighted__c1__unscaled` | 0.7768 +/- 0.0310 | 0.6430 +/- 0.0422 | 0.8327 +/- 0.0242 | 0.7078 | 0.5545 | 0.7876 | 0.1853 |
| `current_5__zero_as_missing__median__logistic__unweighted__c1` | 0.7768 +/- 0.0300 | 0.6392 +/- 0.0415 | 0.8325 +/- 0.0252 | 0.7078 | 0.5545 | 0.7881 | 0.1847 |
| `current_5__zero_as_missing__mean__logistic__unweighted__c1` | 0.7801 +/- 0.0289 | 0.6463 +/- 0.0401 | 0.8325 +/- 0.0243 | 0.7078 | 0.5545 | 0.7872 | 0.1850 |
| `current_5__zero_as_missing__mean__logistic__balanced__c10` | 0.7524 +/- 0.0160 | 0.6635 +/- 0.0228 | 0.8325 +/- 0.0217 | 0.7013 | 0.5965 | 0.7867 | 0.1925 |
| `current_5__zero_as_missing__mean__logistic__balanced__c0_1__unscaled` | 0.7524 +/- 0.0160 | 0.6635 +/- 0.0228 | 0.8323 +/- 0.0219 | 0.7013 | 0.5965 | 0.7867 | 0.1924 |
| `current_5__zero_as_missing__median__logistic__unweighted__c1__unscaled` | 0.7736 +/- 0.0320 | 0.6360 +/- 0.0437 | 0.8323 +/- 0.0257 | 0.7143 | 0.5686 | 0.7885 | 0.1850 |
| `current_5__zero_as_missing__mean__logistic__balanced__c1__unscaled` | 0.7524 +/- 0.0160 | 0.6635 +/- 0.0228 | 0.8322 +/- 0.0217 | 0.7013 | 0.5965 | 0.7865 | 0.1925 |
| `current_5__zero_as_missing__mean__logistic__balanced__c10__unscaled` | 0.7524 +/- 0.0160 | 0.6635 +/- 0.0228 | 0.8322 +/- 0.0217 | 0.7013 | 0.5965 | 0.7865 | 0.1925 |
| `all_8__raw_zeros__median__logistic__balanced__c0_1__unscaled` | 0.7589 +/- 0.0241 | 0.6795 +/- 0.0293 | 0.8320 +/- 0.0422 | 0.7338 | 0.6496 | 0.8191 | 0.1772 |
| `all_8__raw_zeros__median__logistic__unweighted__c1__unscaled` | 0.7882 +/- 0.0177 | 0.6596 +/- 0.0266 | 0.8318 +/- 0.0410 | 0.7143 | 0.5600 | 0.8230 | 0.1686 |
| `all_8__raw_zeros__median__random_forest__unweighted__depth4` | 0.7687 +/- 0.0187 | 0.6097 +/- 0.0300 | 0.8297 +/- 0.0235 | 0.7208 | 0.5474 | 0.8074 | 0.1700 |
| `all_8__raw_zeros__median__random_forest__balanced__depth4` | 0.7508 +/- 0.0235 | 0.6714 +/- 0.0197 | 0.8289 +/- 0.0278 | 0.7403 | 0.6721 | 0.8150 | 0.1755 |
| `current_5__raw_zeros__median__random_forest__unweighted__depth4` | 0.7671 +/- 0.0273 | 0.6145 +/- 0.0426 | 0.8278 +/- 0.0338 | 0.7403 | 0.5833 | 0.8085 | 0.1671 |
| `current_5__zero_as_missing__median__gradient_boosting__lr005` | 0.7622 +/- 0.0139 | 0.6327 +/- 0.0207 | 0.8274 +/- 0.0311 | 0.7338 | 0.5773 | 0.8134 | 0.1692 |
| `current_5__zero_as_missing__mean__gradient_boosting__lr005` | 0.7654 +/- 0.0277 | 0.6368 +/- 0.0352 | 0.8271 +/- 0.0335 | 0.7338 | 0.5773 | 0.8106 | 0.1714 |
| `current_5__raw_zeros__median__random_forest__balanced__depth4` | 0.7605 +/- 0.0338 | 0.6855 +/- 0.0412 | 0.8270 +/- 0.0368 | 0.7468 | 0.6829 | 0.8167 | 0.1722 |
| `current_5__raw_zeros__median__logistic__balanced__c0_1` | 0.7605 +/- 0.0281 | 0.6751 +/- 0.0397 | 0.8266 +/- 0.0419 | 0.7013 | 0.6034 | 0.7970 | 0.1851 |
| `current_5__zero_as_missing__mean__gradient_boosting__lr01` | 0.7605 +/- 0.0279 | 0.6320 +/- 0.0347 | 0.8264 +/- 0.0347 | 0.7273 | 0.5625 | 0.8108 | 0.1712 |
| `current_5__zero_as_missing__median__gradient_boosting__lr01` | 0.7622 +/- 0.0277 | 0.6346 +/- 0.0429 | 0.8260 +/- 0.0315 | 0.7403 | 0.5833 | 0.8151 | 0.1685 |
| `current_5__raw_zeros__median__gradient_boosting__lr01` | 0.7605 +/- 0.0166 | 0.6218 +/- 0.0275 | 0.8260 +/- 0.0443 | 0.7403 | 0.5918 | 0.8194 | 0.1672 |
| `current_5__raw_zeros__median__gradient_boosting__lr005` | 0.7622 +/- 0.0216 | 0.6234 +/- 0.0322 | 0.8258 +/- 0.0423 | 0.7403 | 0.5918 | 0.8177 | 0.1687 |
| `current_5__raw_zeros__median__logistic__balanced__c1` | 0.7589 +/- 0.0346 | 0.6719 +/- 0.0510 | 0.8256 +/- 0.0449 | 0.6883 | 0.5932 | 0.7996 | 0.1852 |
| `current_5__raw_zeros__median__logistic__balanced__c0_1__unscaled` | 0.7572 +/- 0.0374 | 0.6705 +/- 0.0535 | 0.8255 +/- 0.0456 | 0.6948 | 0.6050 | 0.8002 | 0.1853 |
| `current_5__raw_zeros__median__logistic__balanced__c10__unscaled` | 0.7572 +/- 0.0374 | 0.6705 +/- 0.0535 | 0.8254 +/- 0.0457 | 0.6948 | 0.6050 | 0.8002 | 0.1853 |
| `current_5__raw_zeros__median__logistic__balanced__c1__unscaled` | 0.7572 +/- 0.0374 | 0.6705 +/- 0.0535 | 0.8253 +/- 0.0457 | 0.6948 | 0.6050 | 0.8002 | 0.1853 |
| `current_5__raw_zeros__median__logistic__unweighted__c1` | 0.7817 +/- 0.0244 | 0.6510 +/- 0.0390 | 0.8253 +/- 0.0461 | 0.7273 | 0.5882 | 0.7987 | 0.1777 |
| `current_5__raw_zeros__median__logistic__unweighted__c1__unscaled` | 0.7834 +/- 0.0252 | 0.6544 +/- 0.0413 | 0.8253 +/- 0.0467 | 0.7273 | 0.5882 | 0.7993 | 0.1779 |
| `current_5__raw_zeros__median__logistic__balanced__c10` | 0.7572 +/- 0.0374 | 0.6705 +/- 0.0535 | 0.8252 +/- 0.0459 | 0.6883 | 0.5932 | 0.8000 | 0.1853 |
| `all_8__zero_as_missing__mean__random_forest__balanced__unlimited` | 0.7720 +/- 0.0195 | 0.6816 +/- 0.0250 | 0.8244 +/- 0.0289 | 0.7403 | 0.6552 | 0.8286 | 0.1633 |
| `all_8__zero_as_missing__median__random_forest__balanced__unlimited` | 0.7703 +/- 0.0255 | 0.6808 +/- 0.0246 | 0.8236 +/- 0.0279 | 0.7403 | 0.6491 | 0.8294 | 0.1633 |
| `all_8__raw_zeros__median__gradient_boosting__lr01` | 0.7605 +/- 0.0281 | 0.6217 +/- 0.0453 | 0.8220 +/- 0.0301 | 0.7338 | 0.5941 | 0.8222 | 0.1652 |
| `all_8__zero_as_missing__median__gradient_boosting__lr005` | 0.7540 +/- 0.0164 | 0.6130 +/- 0.0340 | 0.8216 +/- 0.0170 | 0.7403 | 0.6000 | 0.8187 | 0.1681 |
| `all_8__raw_zeros__median__gradient_boosting__lr005` | 0.7671 +/- 0.0260 | 0.6373 +/- 0.0441 | 0.8214 +/- 0.0288 | 0.7338 | 0.5941 | 0.8211 | 0.1667 |
| `all_8__zero_as_missing__median__gradient_boosting__lr01` | 0.7557 +/- 0.0241 | 0.6189 +/- 0.0387 | 0.8210 +/- 0.0201 | 0.7338 | 0.5859 | 0.8237 | 0.1656 |
| `all_8__zero_as_missing__mean__gradient_boosting__lr01` | 0.7524 +/- 0.0200 | 0.6156 +/- 0.0356 | 0.8209 +/- 0.0165 | 0.7403 | 0.6000 | 0.8207 | 0.1655 |
| `all_8__zero_as_missing__mean__gradient_boosting__lr005` | 0.7524 +/- 0.0200 | 0.6112 +/- 0.0398 | 0.8198 +/- 0.0186 | 0.7273 | 0.5714 | 0.8183 | 0.1676 |
| `all_8__raw_zeros__median__random_forest__balanced__unlimited` | 0.7703 +/- 0.0330 | 0.6767 +/- 0.0376 | 0.8176 +/- 0.0288 | 0.7208 | 0.6261 | 0.8242 | 0.1650 |
| `current_5__zero_as_missing__median__random_forest__balanced__unlimited` | 0.7540 +/- 0.0341 | 0.6583 +/- 0.0377 | 0.8126 +/- 0.0334 | 0.7468 | 0.6549 | 0.8198 | 0.1643 |
| `current_5__zero_as_missing__mean__random_forest__balanced__unlimited` | 0.7556 +/- 0.0411 | 0.6647 +/- 0.0471 | 0.8110 +/- 0.0366 | 0.7532 | 0.6667 | 0.8172 | 0.1652 |
| `current_5__raw_zeros__median__random_forest__balanced__unlimited` | 0.7377 +/- 0.0481 | 0.6380 +/- 0.0543 | 0.8003 +/- 0.0427 | 0.7727 | 0.6957 | 0.8257 | 0.1621 |

## Zero-policy comparison

The comparison below keeps the feature set/model family selection visible rather than choosing a zero policy from holdout performance. `zero_as_missing` follows the documented clinical plausibility policy; `raw_zeros` preserves the source encoding.

| Feature set | Model | Missing median CV ROC-AUC | Missing mean CV ROC-AUC | Raw zeros CV ROC-AUC |
|---|---|---:|---:|---:|
| Current 5 | logistic_regression | 0.8336 | 0.8340 | 0.8266 |
| Current 5 | random_forest | 0.8364 | 0.8357 | 0.8278 |
| Current 5 | gradient_boosting | 0.8274 | 0.8271 | 0.8260 |
| All 8 | logistic_regression | 0.8450 | 0.8462 | 0.8349 |
| All 8 | random_forest | 0.8391 | 0.8392 | 0.8297 |
| All 8 | gradient_boosting | 0.8216 | 0.8209 | 0.8220 |

## Scaling comparison

Scaling is tested explicitly for Logistic Regression while keeping the feature set, zero policy, imputation, class weight, and C value matched. Tree models are reported without scaling because their split thresholds are invariant to monotonic numeric rescaling.

| Feature set | Zero policy | Imputation | C | Scaled CV ROC-AUC | Unscaled CV ROC-AUC |
|---|---|---|---:|---:|---:|
| Current 5 | zero_as_missing | median | 0.1 | 0.8336 | 0.8332 |
| Current 5 | zero_as_missing | median | 1.0 | 0.8332 | 0.8331 |
| Current 5 | zero_as_missing | mean | 0.1 | 0.8340 | 0.8323 |
| Current 5 | zero_as_missing | mean | 1.0 | 0.8331 | 0.8327 |
| Current 5 | raw_zeros | median | 0.1 | 0.8266 | 0.8255 |
| Current 5 | raw_zeros | median | 1.0 | 0.8256 | 0.8253 |
| All 8 | zero_as_missing | median | 0.1 | 0.8450 | 0.8408 |
| All 8 | zero_as_missing | median | 1.0 | 0.8444 | 0.8438 |
| All 8 | zero_as_missing | mean | 0.1 | 0.8462 | 0.8413 |
| All 8 | zero_as_missing | mean | 1.0 | 0.8449 | 0.8438 |
| All 8 | raw_zeros | median | 0.1 | 0.8346 | 0.8320 |
| All 8 | raw_zeros | median | 1.0 | 0.8348 | 0.8339 |

## Best candidate details

```json
{
  "candidate_id": "all_8__zero_as_missing__mean__logistic__balanced__c0_1",
  "feature_set": "all_8",
  "features": [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age"
  ],
  "zero_policy": "zero_as_missing",
  "imputation": "mean",
  "model_name": "logistic_regression",
  "class_weight": "balanced",
  "scale_numeric": true,
  "hyperparameters": {
    "C": 0.1
  },
  "cv": {
    "folds": [
      {
        "accuracy": 0.7723577235772358,
        "precision": 0.6666666666666666,
        "recall": 0.6976744186046512,
        "f1": 0.6818181818181818,
        "roc_auc": 0.8630813953488371,
        "brier_score": 0.14972932688975304,
        "confusion_matrix": [
          [
            65,
            15
          ],
          [
            13,
            30
          ]
        ],
        "fold": 1
      },
      {
        "accuracy": 0.7560975609756098,
        "precision": 0.6226415094339622,
        "recall": 0.7674418604651163,
        "f1": 0.6875,
        "roc_auc": 0.8406976744186047,
        "brier_score": 0.16599051674759346,
        "confusion_matrix": [
          [
            60,
            20
          ],
          [
            10,
            33
          ]
        ],
        "fold": 2
      },
      {
        "accuracy": 0.7723577235772358,
        "precision": 0.6923076923076923,
        "recall": 0.627906976744186,
        "f1": 0.6585365853658537,
        "roc_auc": 0.8523255813953488,
        "brier_score": 0.14791591968869247,
        "confusion_matrix": [
          [
            68,
            12
          ],
          [
            16,
            27
          ]
        ],
        "fold": 3
      },
      {
        "accuracy": 0.7723577235772358,
        "precision": 0.6595744680851063,
        "recall": 0.7209302325581395,
        "f1": 0.6888888888888889,
        "roc_auc": 0.8482558139534884,
        "brier_score": 0.1605564139931543,
        "confusion_matrix": [
          [
            64,
            16
          ],
          [
            12,
            31
          ]
        ],
        "fold": 4
      },
      {
        "accuracy": 0.7704918032786885,
        "precision": 0.64,
        "recall": 0.7619047619047619,
        "f1": 0.6956521739130435,
        "roc_auc": 0.8264880952380952,
        "brier_score": 0.1760664344277148,
        "confusion_matrix": [
          [
            62,
            18
          ],
          [
            10,
            32
          ]
        ],
        "fold": 5
      }
    ],
    "mean": {
      "accuracy": 0.7687325069972012,
      "precision": 0.6562380672986856,
      "recall": 0.715171650055371,
      "f1": 0.6824791659971935,
      "roc_auc": 0.8461697120708749,
      "brier_score": 0.1600517223493816
    },
    "std": {
      "accuracy": 0.0071092118081236095,
      "precision": 0.02652031595414255,
      "recall": 0.056724325091612605,
      "f1": 0.014261009138173039,
      "roc_auc": 0.013652479781334314,
      "brier_score": 0.011681444150399251
    }
  },
  "holdout": {
    "accuracy": 0.7077922077922078,
    "precision": 0.5714285714285714,
    "recall": 0.6666666666666666,
    "f1": 0.6153846153846154,
    "roc_auc": 0.8099999999999999,
    "brier_score": 0.18138990984019795,
    "confusion_matrix": [
      [
        73,
        27
      ],
      [
        18,
        36
      ]
    ]
  }
}
```

### Best candidate confusion matrix

`[[73, 27], [18, 36]]`

## Five-seed robustness

| Candidate | Mean accuracy +/- std | Mean precision +/- std | Mean recall +/- std | Mean F1 +/- std | Mean ROC-AUC +/- std |
|---|---:|---:|---:|---:|---:|
| `current_5__zero_as_missing__median__logistic__balanced__c1` | 0.7130 +/- 0.0388 | 0.5853 +/- 0.0516 | 0.6222 +/- 0.0609 | 0.6030 +/- 0.0548 | 0.8135 +/- 0.0329 |
| `all_8__zero_as_missing__mean__logistic__balanced__c0_1` | 0.7312 +/- 0.0339 | 0.6095 +/- 0.0483 | 0.6593 +/- 0.0483 | 0.6325 +/- 0.0414 | 0.8218 +/- 0.0327 |

Per-seed rows are included in the JSON result for reproducibility.

## Limitations

- One public dataset and no external validation cohort.
- The remote dataset source is recorded, but full offline retraining requires obtaining that source separately.
- The positive class is a minority (268/768); accuracy alone is insufficient, so precision, recall, F1, ROC-AUC, Brier score, and confusion matrices are reported.
- Five-seed robustness reduces dependence on one split but does not replace external validation or confidence intervals.
- Feature removal is not treated as an improvement claim; the all-feature configuration is the primary complete predictor comparison.
- No production artifact, API, frontend, authentication, database schema, Heart Disease model, CKD model, or original dataset was changed.

## Replacement decision

`research_v1` remains the production artifact. A `research_v2` artifact should only be prepared after explicit approval and only if independent review accepts the training-CV and five-seed evidence above. This experiment does not claim approximately 85% accuracy unless the reported controlled results actually support that claim.
