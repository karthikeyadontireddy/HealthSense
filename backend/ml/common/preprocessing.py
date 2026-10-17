"""Shared preprocessing extension points for disease-specific pipelines.

Preprocessing must be selected from the inspected source dataset and documented
in the corresponding training pipeline. Original datasets remain unchanged.
"""


def build_preprocessor(*, numerical_features, categorical_features):
    raise NotImplementedError(
        "Choose and document preprocessing after inspecting the disease dataset."
    )
