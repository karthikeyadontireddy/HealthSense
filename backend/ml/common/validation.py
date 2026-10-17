from pathlib import Path

import pandas as pd


def load_csv(path: Path, *, column_names: list[str], na_values: list[str] | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return pd.read_csv(path, header=None, names=column_names, na_values=na_values)


def validate_columns(data: pd.DataFrame, expected_columns: list[str], target_column: str) -> None:
    missing = [column for column in expected_columns if column not in data.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    if target_column not in data.columns:
        raise ValueError(f"Dataset is missing target column: {target_column}")


def inspect_dataset(data: pd.DataFrame, target_column: str) -> dict:
    return {
        "rows": len(data),
        "columns": len(data.columns),
        "missing_values": data.isna().sum().to_dict(),
        "duplicates": int(data.duplicated().sum()),
        "target_values": data[target_column].value_counts(dropna=False).sort_index().to_dict(),
    }
