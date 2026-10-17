# HealthSense Research Gap Analysis

Analysis date: 2026-09-07

This document analyzes completed HealthSense experiments only. It is not a
literature review and does not claim novelty, superiority, clinical validity, or
research priority over existing work. No new experiments were run for this
analysis. Original datasets, production artifacts, application architecture,
and APIs were not modified.

## 1. Research Problem

HealthSense contains three heterogeneous supervised-learning tasks:

- Diabetes: 768 records, numeric features, binary `Outcome`, and zero-coded
  measurement values requiring an explicit missing-value policy.
- Heart Disease: 303 Cleveland records, numeric storage with coded categorical
  fields, six `?` values, and an original five-class `num` target transformed to
  binary `0` versus `1-4` for the implemented experiment.
- CKD: 397 usable records after strict rejection of three malformed rows from a
  400-record ARFF source, extensive `?` missingness, mixed numeric/nominal
  fields, and binary `class` encoding.

The scientific problem is not simply to maximize a single score. It is to
compare disease-specific preprocessing, model behavior, feature dependence,
robustness, and probability quality while preserving test-set isolation and
source-data provenance.

## 2. Existing Multi-Disease Prediction Gap

No external literature review was conducted in this phase. Therefore, the
following are candidate gaps or hypotheses, not established gaps in published
research.

### Candidate gap A: disease-specific preprocessing under one reproducible framework

**Project-supported observation:** the three datasets require different handling:
Diabetes zero-coded measurements, Heart `?` values and coded fields, and CKD
ARFF width errors, extensive missingness, and nominal whitespace artifacts.

**Hypothesis requiring literature comparison:** multi-disease studies may not
always expose these preprocessing decisions and provenance controls consistently
within one reproducible framework. This must be checked against published
methods before being called a research gap.

### Candidate gap B: comparable validation across heterogeneous disease datasets

**Established by our experiments:** the same broad candidate set and metrics
produced materially different behavior across diseases. A single accuracy
number would conceal those differences.

**Hypothesis requiring literature comparison:** a transparent multi-disease
protocol combining training-only preprocessing, stratified CV, held-out testing,
seed robustness, ablation, calibration audit, and limitations may be useful as a
comparison framework. Its novelty is not established.

### Candidate gap C: performance transparency for suspiciously high results

**Established by our experiments:** CKD remained unusually high across models,
seeds, CV, and one-feature ablations, while exact duplicates and exact
train/test feature overlap were not found.

**Hypothesis requiring literature comparison:** a structured investigation of
high performance using feature separation, categorical purity, malformed-row
policy, ablation, and provenance checks may be an underreported component of
small clinical tabular studies. This is not a claim that leakage is present.

### Candidate gap D: probability reliability alongside classification scores

**Established by our experiments:** raw probability outputs were audited with
Brier score, calibration curves, and expected calibration error, and no
calibration method was fitted. Calibration behavior differs from classification
ranking behavior and must be reported separately.

**Hypothesis requiring literature comparison:** multi-disease comparisons may
benefit from treating probability reliability as a first-class evaluation
component rather than reporting only accuracy or ROC-AUC. This requires a
literature review and stronger calibration validation.

## 3. Evidence From Our Experiments

### Performance and robustness

Repeated five-fold CV means and standard deviations:

| Disease | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Diabetes | 0.7380 +/- 0.0048 | 0.6126 +/- 0.0052 | 0.6934 +/- 0.0102 | 0.6484 +/- 0.0067 | 0.8243 +/- 0.0025 |
| Heart Disease | 0.8428 +/- 0.0065 | 0.8423 +/- 0.0073 | 0.8115 +/- 0.0082 | 0.8235 +/- 0.0080 | 0.9134 +/- 0.0063 |
| CKD | 0.9899 +/- 0.0018 | 0.9906 +/- 0.0020 | 0.9935 +/- 0.0036 | 0.9920 +/- 0.0014 | 0.9996 +/- 0.0006 |

Five-seed held-out means and standard deviations:

| Disease | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Diabetes | 0.7130 +/- 0.0388 | 0.5853 +/- 0.0516 | 0.6222 +/- 0.0609 | 0.6030 +/- 0.0548 | 0.8135 +/- 0.0329 |
| Heart Disease | 0.8656 +/- 0.0561 | 0.8645 +/- 0.0766 | 0.8429 +/- 0.0741 | 0.8520 +/- 0.0623 | 0.9387 +/- 0.0340 |
| CKD | 0.9900 +/- 0.0105 | 0.9923 +/- 0.0172 | 0.9920 +/- 0.0110 | 0.9920 +/- 0.0082 | 1.0000 +/- 0.0000 |

These are dataset-specific research metrics, not clinical performance estimates.

### Probability quality

The raw model outputs were not calibrated:

- Diabetes: Brier `0.1755 +/- 0.0186`; ECE `0.1054 +/- 0.0244`.
- Heart Disease: Brier `0.0956 +/- 0.0130`; ECE `0.1020 +/- 0.0259`.
- CKD: Brier `0.0094 +/- 0.0040`; ECE `0.0432 +/- 0.0071`.

The CKD values reflect strong separation in this source and do not establish
calibrated or real-world probabilities.

### Model-selection context

The corrected controlled CV comparison used only the seed-42 training partition.
Its selected production models were not replaced:

- Diabetes: Logistic Regression remained the recorded candidate.
- Heart Disease: Logistic Regression remained the recorded candidate.
- CKD: Random Forest remained the recorded candidate.

On the corrected CV comparison, Diabetes Gradient Boosting had the highest
accuracy and ROC-AUC among the listed candidates, but the project retained its
existing selection policy and artifacts. This illustrates why model choice
should not be changed from one metric or one test split without a prespecified
selection rule.

## 4. Observed Findings

### Diabetes

- The task is the least performant of the three in this project: five-seed
  held-out ROC-AUC mean `0.8135` and F1 mean `0.6030`.
- Holdout variability is meaningful, especially for recall (`0.0609` SD).
- Removing Glucose reduced seed-42 test ROC-AUC from `0.7857` to `0.7072` and
  increased Brier score from `0.1919` to `0.2246`.
- Removing BMI or Age changed ROC-AUC less on that split.
- Treating selected zeros as missing versus retaining raw zeros produced close
  mean ROC-AUC values, `0.8135` versus `0.8129`, so the data convention remains
  a methodological sensitivity rather than a settled truth.
- The current feature contract excludes HbA1c because it is not in the source
  dataset; the application must not imply otherwise.

### Heart Disease

- Heart performance is higher than Diabetes in this project, but the five-seed
  held-out metrics have the widest variability: accuracy SD `0.0561`, precision
  SD `0.0766`, and recall SD `0.0741`.
- The binary target transformation makes the experiment reproducible, but it
  removes the original distinction among target levels 1, 2, 3, and 4.
- Removing `ca` or `cp` lowered seed-42 ROC-AUC from `0.9665` to `0.9426` and
  `0.9405`, respectively.
- Removing `thal` increased the single-split score; this should not be treated
  as evidence that `thal` is harmful because it is a split-specific result.
- The dataset's coded fields and small sample size make encoding and uncertainty
  important parts of the research description.

### CKD

- CKD is consistently and unusually high: CV ROC-AUC mean `0.9996` and
  five-seed held-out accuracy mean `0.9900`.
- Logistic Regression, Random Forest, and Gradient Boosting all remain very
  strong in corrected CV; the Random Forest has the highest recorded CV F1.
- Removing any of the tested high-importance raw features (`hemo`, `sc`, `pcv`,
  `al`, `rbcc`) left the seed-42 held-out metrics at `1.0000`.
- Numeric separation is strong, including univariate AUCs for `sc` `0.9219`,
  `bu` `0.7488`, and `bgr` `0.7353`; hemoglobin and packed cell volume have
  near-inverse separation values `0.0308` and `0.0444`.
- Several categorical groups are highly class-pure in the retained parsed data.
- No exact duplicate rows or exact train/test feature overlap were found in the
  completed diagnostics.
- These observations support strong source-level class separation and possible
  dataset artifacts as hypotheses. They do not demonstrate leakage.

## 5. Potential Research Contribution

The current work can support a modest, defensible contribution centered on
methodological transparency:

### Contribution 1: disease-specific preprocessing and model selection

**Established by experiments:** disease-specific pipelines are required and
produce different model behavior. The same candidate family does not have the
same ranking or tradeoffs across diseases.

**Supported by project documentation:** each artifact records source, target,
features, preprocessing, policy, model, and limitations.

**Still requiring literature comparison:** whether this organization is novel or
meaningfully better than existing multi-disease frameworks.

### Contribution 2: unified evaluation of heterogeneous tabular disease tasks

**Established by experiments:** a common evaluation protocol exposed different
performance, robustness, feature dependence, and probability-quality profiles.

**Supported by project documentation:** the project already defines shared
metrics, stratification, seeds, held-out testing, ablation, and calibration
audits while preserving disease-specific preprocessing.

**Still requiring literature comparison:** whether comparable published studies
perform this complete combination of analyses and whether the framework adds
knowledge beyond standard practice.

### Contribution 3: transparent investigation of high performance

**Established by experiments:** CKD high performance persists after seed changes,
CV, candidate changes, and one-feature ablations; exact duplicate/overlap checks
were negative; strong feature and categorical separation is present.

**Supported by project documentation:** CKD malformed records, target-count
ambiguity, and whitespace artifacts are explicitly logged.

**Still requiring literature comparison:** whether this audit pattern is a
recognized gap and whether further source or external-dataset analysis changes
the interpretation.

### Contribution 4: interpretability and probability-quality comparison

**Established by experiments:** selected-model feature importance/coefficients,
Brier scores, calibration curves, and ECE were generated without causal claims
or calibration claims.

**Supported by project documentation:** model cards and experiment logs separate
model behavior from disease causation and separate model-estimated probability
from calibrated probability.

**Still requiring literature comparison:** whether this combination is novel or
sufficiently rigorous relative to existing papers.

## 6. What We Cannot Claim

The current evidence does not support claims that:

- any model is clinically accurate, clinically useful, or deployment-ready;
- CKD leakage has been demonstrated;
- CKD performance is perfect in a generalizable sense;
- one disease model is superior to published systems;
- the approach is state-of-the-art or novel;
- feature importance identifies causes of disease;
- raw probabilities are calibrated patient probabilities;
- the Heart binary target is clinically equivalent to the original five-class
  target;
- the results generalize across hospitals, populations, time periods, or
  external datasets;
- the project has identified a research gap in the published literature.

## 7. Remaining Experiments Required

No additional experiments were run for this analysis. Before making a paper-level
contribution claim, the following work is needed:

1. Conduct a literature review that defines the comparison set and verifies
   whether the proposed methodological gap is already addressed.
2. Perform external or cross-source validation, especially for CKD.
3. Resolve CKD provenance, malformed-row interpretation, and raw whitespace
   normalization under a prespecified policy.
4. Assess near-duplicate and source-export duplication more formally.
5. Evaluate calibration with a separate calibration protocol or validation set;
   do not fit calibration on the final test set.
6. Prespecify whether Diabetes feature selection and zero handling are fixed or
   compared as formal study factors.
7. Consider Heart multiclass analysis as a separate experiment because the
   binary mapping loses target-level information.
8. Report confidence intervals or repeated resampling intervals appropriate to
   the final study design.

## 8. Candidate Research Questions

1. How does disease-specific preprocessing affect reproducibility and model
   behavior across heterogeneous tabular health datasets?
2. How stable are model rankings when evaluation includes held-out testing,
   repeated seeds, feature ablation, and calibration diagnostics rather than
   accuracy alone?
3. Can a common experiment registry improve transparency without forcing a
   universal preprocessing or feature schema across diseases?
4. What evidence is needed to distinguish genuine class separation from
   source-specific artifacts in unusually high-performing small datasets?
5. How does the Heart five-class-to-binary target decision change model ranking,
   interpretability, and evaluation conclusions?
6. Do feature-ablation patterns remain stable under external validation, or are
   they specific to the source datasets?

These are candidate questions, not claims that the project has answered them.

## 9. Candidate Paper Titles

These are neutral working titles, not novelty claims:

1. **A Reproducible Disease-Specific Evaluation Framework for Heterogeneous
   Tabular Health Datasets**
2. **Comparing Preprocessing, Model Robustness, and Probability Reliability Across
   Diabetes, Heart Disease, and CKD Prediction Tasks**
3. **Auditing Feature Dependence and Unexpectedly High Performance in Small
   Multi-Disease Clinical Tabular Datasets**
4. **From Classification Scores to Reliability Audits: A Transparent Multi-Disease
   Machine-Learning Study**

## Ranked Top Three Candidate Contributions

| Rank | Candidate contribution | Scientific defensibility | Feasibility | Student-paper usefulness | Additional work |
|---:|---|---|---|---|---|
| 1 | Disease-specific preprocessing plus unified, test-isolated evaluation | High for the current evidence; novelty not established | High | High | Literature review, final protocol, and external validation if feasible |
| 2 | Feature-ablation and robustness comparison across heterogeneous diseases | Moderate to high as an empirical study; no causal interpretation | High | High | More prespecified ablations, uncertainty intervals, and external checks |
| 3 | CKD high-performance audit and source-artifact investigation | Moderate; evidence is strong but no leakage mechanism is demonstrated | Moderate | High | Provenance resolution, near-duplicate analysis, and independent validation |

The strongest current position is therefore a transparent methodological study,
not a claim that HealthSense produces clinically reliable predictions or novel
state-of-the-art models.
