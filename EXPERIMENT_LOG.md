# Scientific Experiment Log

All entries below correspond to experiments actually run on 2026-09-07. No
metrics are fabricated. The source files were not modified.

## EXP-001: Existing three-model training audit

- Disease: Diabetes, Heart Disease, CKD
- Dataset: Plotly Diabetes; Cleveland Heart; selected CKD ARFF candidate
- Preprocessing: disease-specific sklearn pipelines; training-fold imputation,
  scaling for Logistic Regression, and one-hot encoding for nominal fields
- Features: disease-specific feature contracts in each artifact metadata file
- Models: Logistic Regression, Random Forest, Gradient Boosting candidates
- Hyperparameters: Logistic Regression `max_iter=2000`, balanced class weight;
  Random Forest `n_estimators=300`, balanced class weight; Gradient Boosting
  `random_state=42`
- Random seed: 42
- Validation: stratified 5-fold CV on training split plus isolated 20% test set
- Observation: selected models were Diabetes Logistic Regression, Heart Logistic
  Regression, and CKD Random Forest.
- Limitation: one holdout is not sufficient for generalization.

## EXP-002: Five-seed holdout robustness

- Experiment ID: EXP-002
- Disease: all three
- Dataset: same immutable sources and policies as EXP-001
- Preprocessing: same pipelines, refit within each split
- Models: selected model per disease
- Seeds: 42, 7, 21, 100, 2026
- Validation: independent stratified 80/20 splits; final model artifacts were not
  overwritten
- Results:
  - Diabetes: accuracy 0.7130 +/- 0.0388, precision 0.5853 +/- 0.0516,
    recall 0.6222 +/- 0.0609, F1 0.6030 +/- 0.0548, ROC-AUC 0.8135 +/- 0.0329.
  - Heart: accuracy 0.8656 +/- 0.0561, precision 0.8645 +/- 0.0766,
    recall 0.8429 +/- 0.0741, F1 0.8520 +/- 0.0623, ROC-AUC 0.9387 +/- 0.0340.
  - CKD: accuracy 0.9900 +/- 0.0105, precision 0.9923 +/- 0.0172,
    recall 0.9920 +/- 0.0110, F1 0.9920 +/- 0.0082, ROC-AUC 1.0000 +/- 0.0000.
- Observation: Diabetes and Heart vary across holdouts; CKD remains unusually high.

## EXP-003: Repeated stratified cross-validation

- Experiment ID: EXP-003
- Disease: all three
- Validation: 5-fold stratified CV repeated with seeds 42, 7, 21, 100, 2026
- Results:
  - Diabetes: accuracy 0.7380 +/- 0.0048, precision 0.6126 +/- 0.0052,
    recall 0.6934 +/- 0.0102, F1 0.6484 +/- 0.0067, ROC-AUC 0.8243 +/- 0.0025.
  - Heart: accuracy 0.8428 +/- 0.0065, precision 0.8423 +/- 0.0073,
    recall 0.8115 +/- 0.0082, F1 0.8235 +/- 0.0080, ROC-AUC 0.9134 +/- 0.0063.
  - CKD: accuracy 0.9899 +/- 0.0018, precision 0.9906 +/- 0.0020,
    recall 0.9935 +/- 0.0036, F1 0.9920 +/- 0.0014, ROC-AUC 0.9996 +/- 0.0006.
- Observation: CV confirms CKD separation is unusually strong but not a clinical claim.

## EXP-004: Probability calibration audit

- Experiment ID: EXP-004
- Disease: all three
- Method: raw `predict_proba()` on five holdout seeds; Brier score, ten-bin
  calibration curves, and expected calibration error
- Results:
  - Diabetes: Brier 0.1755 +/- 0.0186; ECE 0.1054 +/- 0.0244.
  - Heart: Brier 0.0956 +/- 0.0130; ECE 0.1020 +/- 0.0259.
  - CKD: Brier 0.0094 +/- 0.0040; ECE 0.0432 +/- 0.0071.
- Observation: lower scores on CKD reflect strong separation in this source, not
  validated probability calibration. No calibration model was added.

## EXP-005: Diabetes zero-value sensitivity

- Experiment ID: EXP-005
- Disease: Diabetes
- Comparison: selected documented policy versus retaining raw zeros
- Preprocessing: same training-fold median imputation pipeline for the policy
  condition; raw-zero condition uses the same pipeline without zero conversion
- Results:
  - Zero-as-missing: accuracy 0.7130 +/- 0.0388, F1 0.6030 +/- 0.0548,
    ROC-AUC 0.8135 +/- 0.0329.
  - Raw zeros retained: accuracy 0.7195 +/- 0.0439, F1 0.6198 +/- 0.0583,
    ROC-AUC 0.8129 +/- 0.0394.
- Observation: retaining zeros performed slightly better on these holdouts, but
  this is not a reason to treat implausible zeros as valid measurements. The
  policy remains a scientific sensitivity choice requiring domain justification.

## EXP-006: CKD source-quality and separation audit

- Experiment ID: EXP-006
- Disease: CKD
- Dataset: selected `chronic_kidney_disease.arff`; other original preserved
- Validation: strict row-width policy, feature duplicate check, exact train/test
  overlap check, univariate numeric separation, categorical target-rate tables
- Results: 3 malformed 26-field rows rejected; 0 complete feature duplicates;
  0 exact train/test feature overlap under seed 42. Numeric univariate AUCs
  include serum creatinine (`sc`) 0.9219, blood urea (`bu`) 0.7488,
  random glucose (`bgr`) 0.7353, hemoglobin (`hemo`) 0.0308, and packed cell
  volume (`pcv`) 0.0444. Several categorical levels are highly class-pure,
  including `htn=yes` and `dm=yes` in the retained parsed rows.
- Observation: the model is exploiting strong source-level class separation;
  no direct target column or duplicate overlap was found. The result remains
  scientifically suspect until provenance, whitespace artifacts, malformed rows,
  and external validation are resolved.

## EXP-007: Heart target formulation audit

- Experiment ID: EXP-007
- Disease: Heart Disease
- Original target: `num` values 0, 1, 2, 3, 4
- Training target: `0 -> 0`, `1..4 -> 1`
- Observation: binary formulation is reproducible and matches the source
  documentation's presence-versus-absence distinction, but it loses severity
  information and is not a clinical endpoint validation.

## EXP-008: Controlled candidate comparison

- Date: 2026-09-07
- Disease: Diabetes, Heart Disease, CKD
- Dataset/source: existing immutable sources and existing disease policies
- Features: each disease's complete approved feature set
- Preprocessing: reused existing disease-specific sklearn pipelines; all
  transformations fit inside each training fold
- Models: Logistic Regression, Random Forest, Gradient Boosting
- Hyperparameters: existing candidate definitions in `backend/ml/training/common.py`
- Random seed: 42
- Validation: stratified 5-fold CV and seed-42 held-out test evaluation
- Metrics: accuracy, precision, recall, F1, ROC-AUC, Brier, ECE
- Output: `experiments/results/controlled_ml_experiments_20260907T081721Z.json`
- Observation: CKD remained unusually strong across all candidate algorithms.
- Limitation: no external validation and no calibration fitting.

## EXP-009: Selected-model feature ablation

- Date: 2026-09-07
- Disease: Diabetes, Heart Disease, CKD
- Dataset/source: same immutable sources and policies as EXP-008
- Features: full set, then one prespecified high-importance raw feature removed
  per retraining variant
- Preprocessing: same disease-specific pipelines refit for every variant
- Models: existing selected model per disease
- Random seed: 42
- Validation: stratified 5-fold CV on training data plus untouched seed-42 test
- Observation: removing Diabetes Glucose reduced test ROC-AUC from 0.7857 to
  0.7072; removing Heart `ca` or `cp` reduced ROC-AUC; CKD remained 1.0000
  after every tested one-feature removal.
- Limitation: one-feature ablations do not establish causality or explain CKD
  provenance; multi-feature and external-source analysis remain necessary.

## EXP-010: Protocol correction and reproducible rerun

- Date: 2026-09-07
- Issue: the first controlled runner output was preserved, but its CV helper used
  the full dataset rather than isolating the held-out split first.
- Correction: the runner now performs the seed-42 stratified split first and
  runs all five-fold CV only on the training partition; the held-out test remains
  unused until final evaluation.
- Output: `experiments/results/controlled_ml_experiments_20260907T081721Z.json`
- Observation: corrected CV values are the primary controlled-experiment results
  documented in `EXPERIMENTS.md`.
