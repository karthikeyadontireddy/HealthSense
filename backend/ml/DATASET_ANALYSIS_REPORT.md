# HealthSense Multi-Disease Dataset Analysis

Inspection date: 2026-09-07

This is a read-only dataset analysis and architecture phase. No model was
trained, retrained, or evaluated, and no original dataset was modified. HealthSense
remains a supervised machine-learning research and educational prototype, not an
AI/LLM system or a medical diagnostic system.

## 1. Executive summary

Three independent disease datasets were analyzed:

- Diabetes: Plotly CSV, 768 rows and 9 columns.
- Heart Disease: Cleveland subset, 303 rows and 14 columns.
- CKD: two ARFF candidates, each 400 rows and 25 declared columns.

The datasets have different schemas, missing-value conventions, target types, and
categorical encodings. They require disease-specific preprocessing pipelines.
There is no basis for a single universal feature table or model.

The two CKD candidates have identical schemas and identical record content under
declared-field comparison, but both contain three malformed 26-field records in
a 25-attribute ARFF file. They should not be repaired silently. Final CKD source
selection and malformed-row handling require an explicit research decision.

## 2. Diabetes dataset analysis

### Source and structure

- Source: `https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv`
- Records: 768
- Columns: 9
- Target: `Outcome`
- Original target values: `0` = 500 records; `1` = 268 records
- Class proportions: approximately 65.1% and 34.9%
- Duplicate rows observed: 0
- Constant columns: none
- Near-constant columns at the 95% majority threshold: none
- Stored data types: integer columns for `Pregnancies`, `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin`, `Age`, `Outcome`; floating-point columns for `BMI` and `DiabetesPedigreeFunction`
- Categorical features: none; all columns are numeric in the CSV

All columns:

`Pregnancies`, `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin`,
`BMI`, `DiabetesPedigreeFunction`, `Age`, `Outcome`

Observed feature ranges and medians:

| Column | Minimum | Maximum | Median |
|---|---:|---:|---:|
| Pregnancies | 0 | 17 | 3 |
| Glucose | 0 | 199 | 117 |
| BloodPressure | 0 | 122 | 72 |
| SkinThickness | 0 | 99 | 23 |
| Insulin | 0 | 846 | 30.5 |
| BMI | 0 | 67.1 | 32 |
| DiabetesPedigreeFunction | 0.078 | 2.42 | 0.3725 |
| Age | 21 | 81 | 29 |

The CSV contains no empty strings or literal `?` values and no parsed nulls.
However, zero values occur in fields where zero is likely a missing or invalid
measurement representation: Glucose 5, BloodPressure 35, Insulin 374, and BMI
11. SkinThickness also contains zero values. Whether to treat these values as
missing must be decided and documented in a future pipeline; the original CSV
must remain unchanged.

### Existing baseline

The current model uses exactly:

`Glucose`, `BloodPressure`, `Insulin`, `BMI`, `Age`

It excludes `Pregnancies`, `SkinThickness`, and
`DiabetesPedigreeFunction`. The selection is reproducible but its scientific
rationale is not documented by the source project, so it should be treated as a
baseline feature subset rather than an established optimal feature set. The
application's HbA1c database field is not a feature in this dataset or in the
current trained vector. HbA1c must not be described as model input; adding it
requires a new training experiment and compatible data.

The existing baseline uses raw values with no imputation, scaling, or pipeline
object. It uses a stratified 80/20 split and a Random Forest. Its main risks are
zero-coded missing measurements, remote-source reproducibility, and the current
service behavior that can train automatically when the model artifact is absent.
The prediction API should eventually fail clearly when an approved artifact is
missing rather than retraining during inference.

## 3. Heart Disease dataset analysis

### Source and structure

- File: `backend/datasets/heart/original/processed.cleveland.data`
- Records: 303
- Columns: 14
- Target: `num`
- Original target values: `0` 164, `1` 55, `2` 36, `3` 35, `4` 13
- Duplicate rows observed: 0
- Constant columns: none
- Near-constant columns at the 95% majority threshold: none
- Stored representation: numeric text values; `?` is used for missing values

All columns, in source order:

`age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`,
`exang`, `oldpeak`, `slope`, `ca`, `thal`, `num`

Candidate numerical features are `age`, `trestbps`, `chol`, `thalach`, and
`oldpeak`. The remaining feature columns are stored numerically but are coded
categorical or ordinal fields according to the source documentation:
`sex`, `cp`, `fbs`, `restecg`, `exang`, `slope`, `ca`, and `thal`.

Observed ranges and medians include: age 29-77 (median 56), trestbps 94-200
(130), chol 126-564 (241), thalach 71-202 (153), and oldpeak 0-6.2 (0.8).
The documented coded fields stayed within their documented domains in the
inspection: no invalid values were observed for sex, cp, fbs, restecg, exang,
slope, ca, thal, or num.

Missing values are six literal `?` markers: four in `ca` and two in `thal`.
The target is not missing.

### Target decision

The source target is ordinal-looking five-class `num`, where the source
information describes 0 as no presence and 1 through 4 as presence levels.
This report does not transform it. A future experiment must explicitly choose
between:

- retaining the original five-class target and evaluating multiclass output; or
- defining a documented binary experiment such as `0` versus `1-4`, with the
  mapping recorded in metadata and reports.

The binary option is a research design choice, not a silent cleanup step.

## 4. CKD dataset analysis

### Provenance

The archive includes `chronic_kidney_disease.info.txt`. It describes the
source as an early-stage Indian CKD dataset, attributed to Dr. P.
Soundarapandian and created by L. Jerlin Rubini at Alagappa University, dated
July 2015. The documentation states 400 instances, 25 attributes, 250 CKD and
150 not-CKD records, with missing values denoted by `?`.

### Shared declared schema

Both candidates declare 25 columns: 24 features and target `class`.

`age`, `bp`, `sg`, `al`, `su`, `rbc`, `pc`, `pcc`, `ba`, `bgr`, `bu`, `sc`,
`sod`, `pot`, `hemo`, `pcv`, `wbcc`, `rbcc`, `htn`, `dm`, `cad`, `appet`,
`pe`, `ane`, `class`

Declared numerical features:

`age`, `bp`, `bgr`, `bu`, `sc`, `sod`, `pot`, `hemo`, `pcv`, `wbcc`, `rbcc`

Declared categorical/nominal features:

`sg`, `al`, `su`, `rbc`, `pc`, `pcc`, `ba`, `htn`, `dm`, `cad`, `appet`, `pe`,
`ane`

Target: `class`, declared classes `ckd` and `notckd`.

Observed numerical ranges across each candidate are identical: age 2-90,
bp 50-180, bgr 22-490, bu 1.5-391, sc 0.4-76, sod 4.5-163, pot 2.5-47,
hemo 3.1-17.8, pcv 9-54, wbcc 2200-26400, and rbcc 2.1-8.

Each candidate contains 400 records, zero complete duplicate rows, no constant
columns, and no near-constant columns at the 95% majority threshold.

### Missing values and source-quality issues

Both candidates use literal `?` markers. The per-column counts are identical:

- age 9; bp 12; sg 47; al 46; su 49
- rbc 152; pc 65; pcc 4; ba 4
- bgr 44; bu 19; sc 17; sod 87; pot 88
- hemo 52; pcv 70; wbcc 105; rbcc 130
- htn 2; dm 3; cad 2; appet 1; pe 1; ane 1
- class 0

The candidates also contain three rows with 26 comma-separated fields despite
25 declared attributes. Two rows have an extra trailing empty field. One row
contains an empty `dm` field and an additional shifted value, creating an
alignment ambiguity. A naïve positional parse exposes one `no` value where the
ARFF target declaration permits only `ckd` and `notckd`; the source documentation
still reports 250 and 150 target instances. This must be resolved explicitly
before training. No source value should be deleted, shifted, or repaired in
place.

### CKD candidate comparison and recommendation

The two files have identical declared schemas, 400 rows, record content in
order, target counts under the same declared-field parse, missingness counts,
and source-format problems. No meaningful feature or record difference was
observed. They remain separate original files because their provenance/export
identity has not been independently established.

Recommendation: do not choose one merely because it is easier to parse. First
confirm whether they are duplicate exports of the same source. If confirmed,
select one using an explicit reproducibility rule and record the chosen filename.
Before training, define a strict policy for the three malformed records and the
250/150 versus positional-target discrepancy.

## 5. Data-quality findings

- Diabetes: zero-coded measurements are possible missing-value representations;
  no literal null markers or duplicate rows were observed.
- Heart: six `?` markers occur in two columns; no documented-domain violations
  or duplicate rows were observed.
- CKD: extensive `?` missingness, three malformed-width records in both files,
  and one target alignment discrepancy require validation before modeling.
- No dataset should be edited to resolve these findings. Processed copies and
  decisions belong in a reproducible training pipeline with audit metadata.

## 6. Leakage and contamination risks

- Split before fitting imputers, encoders, scalers, selectors, or resamplers.
  Fit every transformation on training folds only.
- Keep target columns out of feature matrices. For Heart, do not include `num`;
  for CKD, do not include `class`; for Diabetes, do not include `Outcome`.
- Check duplicate rows before splitting. Current complete-duplicate counts are
  zero, but future processed data must be checked again.
- Do not combine disease datasets or use profile fields that were not part of a
  model's approved feature contract.
- Treat Diabetes zero-coded clinical measurements as a declared preprocessing
  decision, not as silently valid values.
- Treat Heart coded fields according to their source semantics; do not infer
  clinical meaning beyond the dataset documentation.
- Resolve CKD malformed rows and target alignment before any split. Do not let a
  parser silently shift fields.
- Keep a final untouched test set. Use stratification where compatible with the
  selected target and report the exact split seed.
- The current Diabetes service can auto-train when its artifact is missing.
  Future inference should load a versioned saved pipeline only and fail if it is
  unavailable.

## 7. Recommended disease-specific preprocessing

### Diabetes

1. Validate columns and binary target values.
2. Decide whether zero values in Glucose, BloodPressure, SkinThickness, Insulin,
   and BMI represent missingness; document the rule.
3. Compare the current five-feature baseline with a documented alternative using
   available non-target columns. Do not add HbA1c because it is absent from the
   source dataset.
4. Fit numeric imputation and any scaling inside the training folds only.
5. Preserve the feature list and preprocessing decisions in the artifact.

### Heart Disease

1. Parse `?` as missing and validate all documented domains.
2. Decide the target formulation before training: original five-class or an
   explicitly documented binary mapping.
3. Impute `ca` and `thal` within training folds.
4. One-hot encode nominal fields where appropriate; retain continuous fields as
   numeric. Scaling is needed for linear models and optional for tree models.
5. Save the target mapping, feature encoding, and preprocessing with the model.

### CKD

1. Select a source only after provenance confirmation; do not silently prefer a
   candidate.
2. Implement strict ARFF row-width validation and resolve the three malformed
   rows through an approved, documented policy.
3. Validate the target against the declared `{ckd, notckd}` classes.
4. Impute numeric and nominal missing values separately inside training folds.
5. One-hot encode nominal features, with an explicit policy for unseen values.
6. Save all preprocessing, source filename, target policy, and validation results
   with the model artifact.

## 8. Recommended model experiments

Each disease should have an independent experiment set, not a shared universal
model.

- Diabetes: Logistic Regression with imputation and scaling; Random Forest as a
  nonlinear baseline; Gradient Boosting as a second nonlinear comparison.
- Heart: Logistic Regression for an interpretable baseline; Random Forest for
  nonlinear interactions; Gradient Boosting if the small sample size and
  validation design support it.
- CKD: Logistic Regression with one-hot encoding and scaling; Random Forest for
  mixed nonlinear effects; Gradient Boosting only with careful stratified
  validation because the dataset is small and heavily incomplete.

Model choice must be based on validation results, not assumed in advance.

## 9. Evaluation methodology

For each disease, reserve an untouched stratified test set after deciding the
label formulation. Use training-only preprocessing and stratified cross-
validation on the training portion for model comparison. Fix and record random
seeds, split proportions, folds, software versions, source filename, and target
mapping.

Report, without fabricating values:

- Accuracy
- Precision, with positive class or averaging method stated
- Recall, with positive class or averaging method stated
- F1-score, with positive class or averaging method stated
- ROC-AUC where the target and probability output make it appropriate
- Confusion matrix

For multiclass Heart experiments, report macro and weighted summaries and a
multiclass one-vs-rest ROC-AUC only if the evaluation design supports it. Because
CKD and Diabetes are imbalanced, include class-specific and balanced summaries;
do not rely on accuracy alone. Calibration should be evaluated separately before
any probability is described as calibrated.

## 10. Proposed multi-disease ML architecture

Each disease owns its dataset configuration, validation, preprocessing,
training, artifact, and inference adapter:

```text
Diabetes source -> diabetes validation -> diabetes preprocessing -> diabetes model -> diabetes inference
Heart source    -> heart validation    -> heart preprocessing    -> heart model    -> heart inference
CKD source      -> CKD validation      -> CKD preprocessing      -> CKD model      -> CKD inference
```

A common registry interface should expose disease identifier, display name,
source file, target definition, feature contract, preprocessing version, model
version, training status, and evaluation metadata. The saved artifact should be
a single pipeline containing fitted preprocessing and estimator. A common
prediction response can expose disease, model-estimated risk or class
probabilities, model name/version, timestamp, and research-use disclaimer,
while each disease adapter validates its own input schema.

The current registry records Diabetes as the existing baseline, Heart as a
confirmed untrained dataset, and CKD as two candidates pending selection. No
Heart or CKD prediction endpoint should return a fabricated result before a real
artifact exists.

## 11. Open research questions

These are technical opportunities or hypotheses, not established literature
claims:

- Can one registry provide reproducible lifecycle controls while preserving
  disease-specific preprocessing and feature contracts?
- How should heterogeneous numeric and nominal clinical fields be compared
  without masking disease-specific semantics?
- Which evaluation strategy is most stable for small, incomplete datasets?
- How should model interpretability be reported consistently across linear and
  tree models?
- What provenance and version metadata are sufficient to reproduce each model?
- How should target transformations, especially the Heart five-class to binary
  decision, affect comparability and scientific interpretation?

## 12. Decisions required before training

1. Confirm whether the two CKD ARFF files are duplicate exports and select the
   source-selection rule.
2. Approve the CKD malformed-row and target-alignment handling policy.
3. Decide whether Heart training is five-class or an explicitly documented binary
   experiment.
4. Decide how Diabetes zero-coded measurements will be treated.
5. Approve the split, cross-validation, positive-class, and metric averaging
   protocol.

No models were trained and no metrics were generated in this phase.
