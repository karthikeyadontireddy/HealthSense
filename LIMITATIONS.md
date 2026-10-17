# Scientific Limitations

HealthSense is a research/educational machine-learning prototype. These results
must not be treated as clinical validation, diagnostic evidence, or calibrated
real-world risk.

## Dataset limitations

- Diabetes uses one public dataset with 768 rows and a 500/268 class split.
- Heart uses only the Cleveland subset with 303 rows and a deliberate binary
  transformation of the original five-class target.
- CKD uses 397 usable rows after rejecting three malformed records from a small
  public source. The source documentation reports 400 rows and 250/150 target
  counts, while one malformed record creates a positional target discrepancy.
- Demographic coverage, collection protocols, sampling mechanisms, and
  representativeness are limited or incompletely documented.
- No external validation cohort is available.
- Dataset-specific biases and selection effects may dominate the results.

## Preprocessing limitations

- Diabetes zero-coded values are treated as missing in selected measurement
  columns. This is defensible from the data representation but is not proven by
  an authoritative measurement protocol; the sensitivity experiment showed the
  choice changes results only modestly but materially.
- Heart coded variables are one-hot encoded based on source documentation. The
  binary `num=0` versus `num=1..4` target is an experiment formulation, not a
  clinical definition.
- CKD contains extensive `?` missingness and malformed-width rows. The current
  pipeline rejects the three malformed rows and imputes remaining missing data.
  Raw nominal whitespace variants remain a source-format concern.

## Statistical limitations

- The held-out samples are small, so metrics vary with the random split. Heart
  has especially wide five-seed test variability.
- CKD has very high scores across repeated splits and CV, but this is a warning,
  not evidence of a perfect model. Several individual features and categorical
  levels strongly separate the source labels, and the dataset may encode source
  or ascertainment patterns.
- Exact duplicate rows and exact train/test feature overlap were not found in
  the strict CKD analysis, but near-duplicate similarity and external source
  duplication cannot be ruled out by this validation.
- Raw model probabilities were assessed with Brier score, expected calibration
  error, and calibration curves, but no calibration method was fitted. They must
  not be described as calibrated probabilities.
- Feature importance and absolute coefficients describe model behavior, not
  disease causes or clinical importance.
- One-feature CKD ablations did not reduce the seed-42 held-out score. This
  indicates redundant or strongly separated information, but does not identify
  a leakage mechanism or establish causal importance.
- Accuracy is insufficient for imbalanced classification; precision, recall,
  F1, ROC-AUC, confusion matrices, and class proportions must be considered
  together.

## Generalizability and safety

- No prospective, temporal, geographic, or external validation was performed.
- No clinical utility, threshold analysis, cost-sensitive analysis, or decision
  curve analysis was performed.
- The models should not be used to make medical decisions or treatment changes.
- Further work requires source/provenance review, robust external validation,
  prespecified protocols, calibration evaluation, and domain review.
