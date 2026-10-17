# Scientific Experiment Audit

Audit date: 2026-09-07

This audit traces the executable training code in
`backend/ml/training/common.py` and the disease loaders in
`backend/ml/training/train_diabetes.py`, `train_heart.py`, and `train_ckd.py`.
The validation experiments are separate and do not rewrite the final model
artifacts.

## Audit findings

| Control | Evidence | Finding |
|---|---|---|
| Train/test split | `train_and_save()` calls `train_test_split(..., test_size=0.2, stratify=target, random_state=42)` | Stratified 80/20 split is implemented for all three diseases. |
| Test isolation during selection | Candidate pipelines are evaluated with `cross_validate()` on `x_train, y_train`; the test set is evaluated only after selection | No test-set use was found in candidate selection. |
| Fold-fitted preprocessing | `make_pipeline()` places `ColumnTransformer` inside sklearn `Pipeline`; `cross_validate()` receives the unfitted pipeline | Imputers, scaler, and encoder fit independently inside each training fold. |
| Final preprocessing fit | Selected pipeline is fit on `x_train` only, then evaluated on `x_test` | No preprocessing fit on the final test set. |
| Stratified CV | `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` in training; validation repeats with seeds 42, 7, 21, 100, 2026 | Stratification and seeds are explicit. |
| Feature/target separation | Disease loaders return feature frame and target separately; target columns are excluded from feature lists | No target column is passed into the feature frame. |
| Diabetes policy | Loader replaces zero in Glucose, BloodPressure, SkinThickness, Insulin, BMI with missing; zero Pregnancies is retained | Policy is explicit, but its scientific effect requires sensitivity analysis. |
| Heart target | Loader validates original `num` values and maps `0` to 0 and `1..4` to 1 before splitting | Deliberate binary transformation is implemented and documented. |
| CKD malformed rows | Loader rejects rows whose field count is not 25 and records line, width, and reason | Three rows are rejected; no source row is repaired or shifted. |
| Missing-value handling | Numeric median imputation; categorical most-frequent imputation; Heart/CKD one-hot encoding | All are pipeline steps, fit only on training folds. |
| Class imbalance | Logistic Regression and Random Forest use `class_weight="balanced"`; Gradient Boosting does not | Accuracy was not the only selection metric; selection uses CV ROC-AUC then F1. |
| Model selection | `max(comparisons, key=(cv ROC-AUC, cv F1))` | Selection is based on training-only CV, not test metrics. |
| Randomness | Model seed, split seed, and CV seed are recorded | Reproducible under the recorded environment and source files. |

## Issues and caveats found

1. The CKD loader does not strip whitespace in nominal values. The validation
   output shows variants such as `\tyes`, `\tno`, and ` yes` as separate levels.
   This is a source-format artifact and can affect encoding. It was not silently
   normalized during validation.
2. The CKD source has three 26-field records in a 25-attribute file. The current
   policy rejects them. One malformed record has a shifted/ambiguous field, so
   inclusion would require a research decision rather than an automatic repair.
3. The original Diabetes trainer still exists separately and can auto-train from
   the legacy service if its old artifact is absent. The new multi-disease
   artifacts do not use that path, but inference hardening should eventually
   remove auto-training from the legacy service.
4. The saved final artifacts contain raw `predict_proba()` outputs. No calibration
   layer is fitted or applied.
5. The final trainer records candidate CV results and selected test metrics. The
   validation runner additionally computed seed-42 held-out metrics for every
   candidate without changing artifacts.

## Conclusion

The core experiment avoids direct preprocessing leakage and test-set model
selection. The results remain subject to dataset-quality, source-format,
small-sample, calibration, and external-validation limitations documented in
`LIMITATIONS.md`.
