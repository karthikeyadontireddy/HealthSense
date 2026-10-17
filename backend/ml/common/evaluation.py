"""Shared evaluation extension points for offline model training."""


def evaluate_classifier(model, features, target):
    raise NotImplementedError(
        "Evaluation is intentionally deferred until a disease model is approved and trained."
    )
