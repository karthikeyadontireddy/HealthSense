# Dataset Inspection Report

Inspection date: 2026-09-07

This report records source inspection only. No model was trained in this phase.
Original source files were not modified.

## Diabetes

- Dataset: Plotly diabetes dataset used by the existing baseline
- Source/file: `https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv` (loaded by the existing baseline script; no local original copy was supplied for this phase)
- Rows: 768, as recorded by the existing trained baseline metadata
- Columns: 9 in the source dataset; the baseline selects 5 features plus `Outcome`
- Target: `Outcome`
- Classes: 0 and 1, as used by the existing baseline
- Numerical features: `Glucose`, `BloodPressure`, `Insulin`, `BMI`, `Age`
- Categorical features: none used by the existing baseline
- Missing values: not re-inspected in this phase
- Duplicates: not re-inspected in this phase
- Potential preprocessing requirements: the existing baseline uses raw selected values without preprocessing. Any future change requires a new documented training run.

## Heart Disease

- Dataset: UCI Heart Disease Cleveland subset
- Source/file: `backend/datasets/heart/original/processed.cleveland.data`
- Source archive: `C:\Users\dbred\Downloads\heart+disease.zip`, archive member `processed.cleveland.data`
- Rows: 303
- Columns: 14
- Columns, in source order: `age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, `thal`, `num`
- Target: `num`
- Original target values: `0` (164), `1` (55), `2` (36), `3` (35), `4` (13)
- Target interpretation documented by the source: 0 indicates no presence and 1 through 4 indicate presence levels; the project does not transform or collapse these classes in Phase 3.
- Numerical features: all 14 parsed columns are numeric after interpreting `?` as missing; `num` is the target and the other 13 are candidate features.
- Categorical features: none stored as text. Several integer-coded fields have categorical semantics in the source documentation; encoding decisions require explicit training-phase review.
- Missing values: six literal `?` markers in the original file, corresponding to 4 missing `ca` values and 2 missing `thal` values. No other column has missing values.
- Duplicates: 0 complete duplicate rows.
- Potential preprocessing requirements: decide how to handle missing `ca` and `thal`; verify categorical encoding for coded fields; decide whether the original five-class target is retained or transformed. Do not make these decisions automatically.

## Chronic Kidney Disease

- Dataset: Early stage of Indians Chronic Kidney Disease (ARFF)
- Source files: `backend/datasets/ckd/original/chronic_kidney_disease.arff` and `backend/datasets/ckd/original/chronic_kidney_disease_full.arff`
- Provenance file: `Chronic_Kidney_Disease/chronic_kidney_disease.info.txt` in the downloaded archive; it attributes the source to Dr. P. Soundarapandian and the dataset creation to L. Jerlin Rubini at Alagappa University, dated July 2015.
- Rows: 400 in each candidate
- Declared columns: 25 (24 features plus `class`)
- Columns: `age`, `bp`, `sg`, `al`, `su`, `rbc`, `pc`, `pcc`, `ba`, `bgr`, `bu`, `sc`, `sod`, `pot`, `hemo`, `pcv`, `wbcc`, `rbcc`, `htn`, `dm`, `cad`, `appet`, `pe`, `ane`, `class`
- Target: `class`
- Declared target classes: `ckd`, `notckd`
- Observed target values after retaining declared positions: `ckd` 250, `notckd` 149, plus one malformed row whose positional value is `no`; the source documentation states 250 CKD and 150 not-CKD instances. This discrepancy requires resolution before training.
- Numerical features: `age`, `bp`, `bgr`, `bu`, `sc`, `sod`, `pot`, `hemo`, `pcv`, `wbcc`, `rbcc`
- Categorical features: `sg`, `al`, `su`, `rbc`, `pc`, `pcc`, `ba`, `htn`, `dm`, `cad`, `appet`, `pe`, `ane`
- Missing representation: literal `?`; no quoted empty-string convention is declared. The two candidates each contain 1,010 question-mark markers across columns. Missingness is highest in `rbcc` (130), `wbcc` (105), `rbc` (152), `pot` (88), and `sod` (87).
- Duplicates: 0 complete duplicate rows in each candidate after reading declared fields.
- Format issue: both candidates contain three records with 26 comma-separated fields despite 25 declarations. Two have an extra trailing empty field; one contains an empty `dm` field and a shifted extra value. The originals must not be repaired in place.
- Numeric ranges observed: `age` 2-90, `bp` 50-180, `bgr` 22-490, `bu` 1.5-391, `sc` 0.4-76, `sod` 4.5-163, `pot` 2.5-47, `hemo` 3.1-17.8, `pcv` 9-54, `wbcc` 2200-26400, `rbcc` 2.1-8.
- Potential preprocessing requirements: define a strict ARFF validation policy; resolve malformed rows and the target-count discrepancy without editing source data; impute numeric and categorical missing values using training-fold-fitted transformers; encode nominal features; preserve the original target until a documented experiment decision.

## CKD candidate comparison

- Schemas: identical declarations and column order.
- Records: 400 each; identical record content in order under the declared-field comparison.
- Target distributions: identical under the same parsing; both expose the same malformed-row target discrepancy described above.
- Missingness: identical per column and identical total question-mark count.
- Meaningful differences: no record or missingness differences were observed. The filenames and archive members remain distinct source candidates, and provenance does not establish that one should be preferred.
- Recommendation: do not choose one based on apparent ease. Retain both until provenance and the malformed-record policy are explicitly resolved. If provenance confirms they are duplicate exports of the same source, select one by an explicit reproducibility rule and record that decision before training.

## Safety and provenance

This report does not claim clinical validity or calibrated probabilities. No
Heart Disease or CKD model artifact or evaluation metrics were created.
