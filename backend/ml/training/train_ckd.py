from pathlib import Path
import csv
import re

import pandas as pd

from backend.ml.training.common import train_and_save

DATA_PATH = Path(__file__).resolve().parents[1] / ".." / "datasets" / "ckd" / "original" / "chronic_kidney_disease.arff"
COLUMNS = ["age", "bp", "sg", "al", "su", "rbc", "pc", "pcc", "ba", "bgr", "bu", "sc", "sod", "pot", "hemo", "pcv", "wbcc", "rbcc", "htn", "dm", "cad", "appet", "pe", "ane", "class"]
NUMERIC = ["age", "bp", "bgr", "bu", "sc", "sod", "pot", "hemo", "pcv", "wbcc", "rbcc"]
CATEGORICAL = ["sg", "al", "su", "rbc", "pc", "pcc", "ba", "htn", "dm", "cad", "appet", "pe", "ane"]


def load_dataset():
    text = DATA_PATH.read_text(encoding="utf-8", errors="replace")
    if "@data" not in text.lower():
        raise ValueError("CKD ARFF is missing its data section")
    rows = []
    dropped = []
    in_data = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.lower() == "@data":
            in_data = True
            continue
        if not in_data or not stripped or stripped.startswith("%"):
            continue
        row = next(csv.reader([stripped]))
        if len(row) != len(COLUMNS):
            dropped.append({"line": line_number, "field_count": len(row), "reason": "field count differs from 25 declared attributes"})
            continue
        rows.append(row)
    data = pd.DataFrame(rows, columns=COLUMNS).replace("?", pd.NA)
    for column in NUMERIC:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    if not set(data["class"].dropna().unique()).issubset({"ckd", "notckd"}):
        raise ValueError("CKD target contains values outside declared classes")
    data["class"] = (data["class"] == "ckd").astype(int)
    return data[NUMERIC + CATEGORICAL], data["class"], dropped


def train():
    features, target, dropped = load_dataset()
    return train_and_save(
        disease_id="chronic_kidney_disease",
        display_name="Chronic Kidney Disease Risk",
        dataset_name="Early stage of Indians Chronic Kidney Disease",
        dataset_source="backend/datasets/ckd/original/chronic_kidney_disease.arff",
        target_name="class_binary",
        feature_names=NUMERIC + CATEGORICAL,
        numeric_features=NUMERIC,
        categorical_features=CATEGORICAL,
        features=features,
        target=target,
        output_dir=Path(__file__).resolve().parents[1] / "models" / "ckd",
        model_version="research_v1",
        preprocessing_description="Literal ? values become missing; median numeric imputation and most-frequent categorical imputation plus one-hot encoding are fitted on training data.",
        dataset_policy=f"Deterministically selected chronic_kidney_disease.arff because both preserved candidates had identical research-relevant content during Phase 4 analysis. Rows with field counts other than 25 are rejected, not repaired or silently shifted. Rejected rows: {len(dropped)}; resulting dataset size: {len(features)}.",
        limitations=["Small public dataset", "Three malformed source rows were rejected under an explicit width-validation policy", "Target-count discrepancy in source documentation requires provenance follow-up", "No external validation", "Model probability calibration was not evaluated"],
        dropped_rows=dropped,
    )


if __name__ == "__main__":
    train()
