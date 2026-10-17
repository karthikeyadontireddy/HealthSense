# HealthSense Model Cards

HealthSense is an educational and research prototype for supervised machine
learning. These artifacts are not medical diagnostic systems, are not clinically
validated, and do not establish whether a person has a medical condition.
Probability calibration has been audited with Brier score, calibration curves,
and expected calibration error, but no calibration method has been fitted.
Outputs must not be described as calibrated probabilities.

## Diabetes

- Dataset: Plotly diabetes dataset (`diabetes.csv`), 768 rows
- Target: `Outcome` (0/1)
- Features: `Glucose`, `BloodPressure`, `Insulin`, `BMI`, `Age`
- Policy: zero values in selected measurement fields are treated as missing;
  zero `Pregnancies` is retained. HbA1c is not a source feature.
- Preprocessing: training-fold median imputation; scaling for Logistic Regression
- Selected model: Logistic Regression
- Version: `research_v1`
- Training/test samples: 614 / 154
- Metrics: stored in `backend/ml/models/diabetes/metadata.json`
- Calibration audit: Brier 0.1755 +/- 0.0186; expected calibration error
  0.1054 +/- 0.0244 across five holdout seeds.
- Limitations: single public dataset, no external validation, and zero-coded
  measurements require sensitivity analysis.

## Heart Disease

- Dataset: UCI Heart Disease Cleveland subset, 303 rows
- Target source: `num` values 0, 1, 2, 3, 4
- Training target: deliberate binary mapping `num=0 -> 0`, `num=1..4 -> 1`
- Features: 13 Cleveland fields excluding `num`
- Preprocessing: `?` missing values; training-fold median numeric imputation;
  training-fold most-frequent imputation and one-hot encoding for coded fields
- Selected model: Logistic Regression
- Version: `research_v1`
- Training/test samples: 242 / 61
- Metrics: stored in `backend/ml/models/heart/metadata.json`
- Calibration audit: Brier 0.0956 +/- 0.0130; expected calibration error
  0.1020 +/- 0.0259 across five holdout seeds.
- Limitations: small single-subset dataset, target transformation is a research
  choice, and no external validation.

## Chronic Kidney Disease

- Dataset: `chronic_kidney_disease.arff`, selected deterministically from the
  two preserved candidates after Phase 4 found identical research-relevant
  content; the other original remains preserved unchanged.
- Declared target: `class` (`ckd`, `notckd`)
- Training target: binary encoding `ckd -> 1`, `notckd -> 0`
- Features: 24 declared source features
- Policy: strict 25-field row validation; three malformed-width records rejected,
  not repaired or silently shifted; resulting dataset size 397
- Preprocessing: training-fold median numeric imputation; training-fold
  most-frequent imputation and one-hot encoding for nominal fields
- Selected model: Random Forest
- Version: `research_v1`
- Training/test samples: 317 / 80
- Metrics: stored in `backend/ml/models/ckd/metadata.json`
- Calibration audit: Brier 0.0094 +/- 0.0040; expected calibration error
  0.0432 +/- 0.0071 across five holdout seeds. This does not establish
  calibration or clinical validity.
- Limitations: small public dataset, malformed source rows rejected under an
  explicit policy, source documentation has a target-count discrepancy, and no
  external validation.
