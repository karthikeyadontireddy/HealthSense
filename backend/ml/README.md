# HealthSense ML Architecture

HealthSense is a supervised machine-learning research prototype, not an AI or
LLM system and not a medical diagnostic system. It currently targets three
independent research datasets/models:

- Diabetes
- Heart Disease
- Chronic Kidney Disease (CKD)

Each disease has its own dataset configuration, preprocessing decisions,
training pipeline, saved model, and evaluation metadata. Training is an offline
operation. The prediction API must only perform inference with a previously
trained artifact and must never retrain a model.

## Dataset policy

Files under `backend/datasets/<disease>/original/` are immutable source data.
They must not be edited, cleaned, relabeled, or overwritten. Any processed data
or preprocessing artifacts belong under separate processed/model locations and
must be generated reproducibly by an approved training pipeline.

## Current status

- Diabetes: `research_v1` artifact is available at `backend/ml/models/diabetes`.
- Heart Disease: `research_v1` artifact is available at `backend/ml/models/heart`.
  The source `num` target is explicitly mapped to binary 0 versus 1-4 for this
  experiment.
- CKD: `research_v1` artifact is available at `backend/ml/models/ckd`. The
  deterministic source is `chronic_kidney_disease.arff`; three malformed rows
  were rejected by strict width validation. The other original remains intact.

Training comparison results and limitations are recorded in the repository root
`EXPERIMENTS.md` and `MODEL_CARD.md`. The registry reports a disease as trained
only when both its saved artifact and metadata exist.

Metrics must only be reported after a real offline training run on an approved
split and evaluation protocol. Outputs must be described as model-estimated
risk or model predictions for research/educational use, never as diagnoses.
