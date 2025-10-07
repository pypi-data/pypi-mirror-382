"""Expected metric optimization under calibration assumption.

This module implements expected threshold optimization using Dinkelbach's algorithm.
Under the calibration assumption, expected metrics can be optimized exactly by
finding optimal thresholds on calibrated probabilities.

Key simplifications:
- Single Dinkelbach implementation for all metrics
- Direct computation instead of coefficient abstraction
- Clear separation: core algorithm vs metrics vs multiclass
"""

from __future__ import annotations

import warnings
from typing import Any, Literal

import numpy as np

from .types_minimal import OptimizationResult

# ============================================================================
# Core Algorithm - Single Dinkelbach implementation
# ============================================================================


def dinkelbach_optimize(
    probabilities: np.ndarray[Any, Any],
    numerator_fn: callable,
    denominator_fn: callable,
    max_iter: int = 100,
    tol: float = 1e-12,
) -> tuple[float, float]:
    """Core Dinkelbach algorithm for ratio optimization.

    Solves: max_t numerator(t) / denominator(t)

    Parameters
    ----------
    probabilities : array of shape (n,)
        Calibrated probabilities
    numerator_fn : callable(threshold) -> float
        Computes numerator at given threshold
    denominator_fn : callable(threshold) -> float
        Computes denominator at given threshold
    max_iter : int
        Maximum iterations
    tol : float
        Convergence tolerance

    Returns
    -------
    threshold : float
        Optimal threshold
    score : float
        Optimal ratio value
    """
    # Sort probabilities once
    p = np.sort(probabilities)

    # Initial lambda
    lam = 0.5
    converged = False

    for iteration in range(max_iter):
        # Find threshold that maximizes: numerator - lambda * denominator
        def objective(t, lambda_val=lam):
            return numerator_fn(t) - lambda_val * denominator_fn(t)

        # Simple grid search over unique probabilities
        # (This is fast enough for most cases)
        candidates = np.unique(p)
        best_t = 0.5
        best_val = -np.inf

        for t in candidates:
            val = objective(t)
            if val > best_val:
                best_val = val
                best_t = t

        # Update lambda
        num = numerator_fn(best_t)
        den = denominator_fn(best_t)

        if den == 0:
            warnings.warn(
                "Dinkelbach algorithm terminated early due to zero denominator "
                f"(numerical instability) at iteration {iteration + 1}",
                RuntimeWarning,
                stacklevel=2,
            )
            break

        new_lam = num / den

        if abs(new_lam - lam) < tol:
            converged = True
            break

        lam = new_lam

    if not converged and den != 0:
        final_tolerance = abs(new_lam - lam) if "new_lam" in locals() else float("inf")
        warnings.warn(
            f"Dinkelbach algorithm did not converge within {max_iter} iterations. "
            f"Final tolerance: {final_tolerance:.2e}, target: {tol:.2e}",
            RuntimeWarning,
            stacklevel=2,
        )

    return float(best_t), float(lam)


# ============================================================================
# Metric-specific expected optimization
# ============================================================================


def dinkelbach_expected_fbeta_binary(
    y_prob: np.ndarray[Any, Any],
    beta: float = 1.0,
    sample_weight: np.ndarray[Any, Any] | None = None,
    comparison: str = ">",
) -> OptimizationResult:
    """Expected F-beta optimization under calibration using efficient O(n log n) algorithm.

    Parameters
    ----------
    y_prob : array of shape (n,)
        Calibrated probabilities for positive class
    beta : float
        F-beta parameter
    sample_weight : array of shape (n,), optional
        Sample weights
    comparison : str
        Comparison operator (kept for backward compatibility)

    Returns
    -------
    OptimizationResult
        Optimization result with threshold, score, and predict function
    """
    # Step 1: Setup and validation
    p = np.asarray(y_prob, dtype=np.float64)
    n = len(p)

    if sample_weight is None:
        w = np.ones(n, dtype=np.float64)
    else:
        w = np.asarray(sample_weight, dtype=np.float64)

    # Validate inputs
    if not np.all((0 <= p) & (p <= 1)):
        raise ValueError("Probabilities must be in [0, 1]")
    if np.any(w < 0):
        raise ValueError("Weights must be non-negative")

    # Step 2: Sort probabilities and weights together
    sort_idx = np.argsort(p)
    p_sorted = p[sort_idx]
    w_sorted = w[sort_idx]

    # Step 3: Pre-compute cumulative sums for O(1) metric evaluation
    wp_sorted = w_sorted * p_sorted
    w1mp_sorted = w_sorted * (1 - p_sorted)

    # Cumulative sums from right (for p > threshold)
    cumsum_wp_right = np.zeros(n + 1)
    cumsum_w1mp_right = np.zeros(n + 1)

    cumsum_wp_right[:-1] = np.cumsum(wp_sorted[::-1])[::-1]
    cumsum_w1mp_right[:-1] = np.cumsum(w1mp_sorted[::-1])[::-1]

    # Cumulative sums from left (for p <= threshold)
    cumsum_wp_left = np.zeros(n + 1)
    cumsum_wp_left[1:] = np.cumsum(wp_sorted)

    # Step 4: Define efficient metric functions using cumulative sums
    def compute_fbeta_at_index(idx: int) -> tuple[float, float]:
        """Compute F-beta numerator and denominator at threshold index."""
        # For threshold at p_sorted[idx], we predict positive for p > p_sorted[idx]

        # Expected TP: sum of p*w for p > threshold
        expected_tp = cumsum_wp_right[idx + 1]

        # Expected FP: sum of (1-p)*w for p > threshold
        expected_fp = cumsum_w1mp_right[idx + 1]

        # Expected FN: sum of p*w for p <= threshold
        expected_fn = cumsum_wp_left[idx + 1]

        beta2 = beta**2
        numerator = (1 + beta2) * expected_tp
        denominator = (1 + beta2) * expected_tp + expected_fp + beta2 * expected_fn

        return numerator, denominator

    # Step 5: Dinkelbach iterations with efficient evaluation
    lambda_val = 0.5
    max_iter = 100
    tol = 1e-12
    converged = False

    # Get unique threshold candidates (including edge cases)
    unique_p, unique_idx = np.unique(p_sorted, return_index=True)
    # Add threshold at endpoints for completeness
    threshold_indices = list(unique_idx) + [n]
    if len(unique_p) == 0 or unique_p[0] > 0:
        threshold_indices = [-1] + threshold_indices

    for iteration in range(max_iter):
        best_threshold = 0.5
        best_value = -np.inf
        best_score = 0.0

        # Evaluate objective at each unique threshold
        for idx in threshold_indices:
            if idx == -1:
                # Threshold = 0 (everything predicted positive)
                threshold = 0.0
                num = cumsum_wp_right[0]
                den = cumsum_wp_right[0] + cumsum_w1mp_right[0]
            elif idx == n:
                # Threshold = 1 (nothing predicted positive)
                threshold = 1.0
                num, den = 0.0, cumsum_wp_left[n]
                if den == 0:
                    den = 1.0  # Avoid division by zero
            else:
                threshold = p_sorted[idx]
                num, den = compute_fbeta_at_index(idx)

            # Objective: maximize num - lambda * den
            obj_value = num - lambda_val * den

            if obj_value > best_value:
                best_value = obj_value
                best_threshold = threshold
                if den > 0:
                    best_score = num / den
                else:
                    best_score = 0.0

        # Update lambda
        if best_threshold == 0.0:
            idx = -1
        elif best_threshold == 1.0:
            idx = n
        else:
            idx = np.searchsorted(p_sorted, best_threshold, side="right") - 1

        if idx == -1:
            num = cumsum_wp_right[0]
            den = cumsum_wp_right[0] + cumsum_w1mp_right[0]
        elif idx == n:
            num, den = 0.0, cumsum_wp_left[n]
            if den == 0:
                den = 1.0
        else:
            num, den = compute_fbeta_at_index(idx)

        if den == 0:
            warnings.warn(
                "Dinkelbach expected F-beta optimization terminated early due to zero denominator "
                f"(numerical instability) at iteration {iteration + 1}",
                RuntimeWarning,
                stacklevel=2,
            )
            break

        new_lambda = num / den if den > 0 else 0.0

        if abs(new_lambda - lambda_val) < tol:
            converged = True
            break

        lambda_val = new_lambda

    if not converged and den != 0:
        final_tolerance = (
            abs(new_lambda - lambda_val) if "new_lambda" in locals() else float("inf")
        )
        warnings.warn(
            f"Dinkelbach expected F-beta optimization did not converge within {max_iter} iterations. "
            f"Final tolerance: {final_tolerance:.2e}, target: {tol:.2e}",
            RuntimeWarning,
            stacklevel=2,
        )

    best_threshold_float = float(best_threshold)
    best_score_float = float(best_score)

    # Create prediction function (closure captures threshold and comparison)
    def predict_binary(probs):
        p = np.asarray(probs)
        if p.ndim == 2 and p.shape[1] == 2:
            p = p[:, 1]  # Use positive class probabilities
        elif p.ndim == 2 and p.shape[1] == 1:
            p = p.ravel()
        if comparison == ">=":
            return (p >= best_threshold_float).astype(int)
        else:
            return (p > best_threshold_float).astype(int)

    return OptimizationResult(
        thresholds=np.array([best_threshold_float]),
        scores=np.array([best_score_float]),
        predict=predict_binary,
        metric=f"expected_f{beta}",
        n_classes=2,
    )


def expected_precision(
    probabilities: np.ndarray[Any, Any], weights: np.ndarray[Any, Any] | None = None
) -> tuple[float, float]:
    """Expected precision optimization.

    Precision = TP / (TP + FP)
    """
    p = np.asarray(probabilities, dtype=np.float64)

    if weights is None:
        weights = np.ones_like(p)

    wp = weights * p
    w1mp = weights * (1 - p)

    def numerator(t):
        mask = p > t
        return np.sum(wp[mask])  # Expected TP

    def denominator(t):
        mask = p > t
        return np.sum(wp[mask]) + np.sum(w1mp[mask])  # Expected TP + FP

    return dinkelbach_optimize(p, numerator, denominator)


def expected_jaccard(
    probabilities: np.ndarray[Any, Any], weights: np.ndarray[Any, Any] | None = None
) -> tuple[float, float]:
    """Expected Jaccard/IoU optimization.

    Jaccard = TP / (TP + FP + FN)
    """
    p = np.asarray(probabilities, dtype=np.float64)

    if weights is None:
        weights = np.ones_like(p)

    wp = weights * p

    def numerator(t):
        mask = p > t
        return np.sum(wp[mask])  # Expected TP

    def denominator(t):
        # TP + FP + FN = all predicted positive + all actual positive - TP
        mask = p > t
        tp = np.sum(wp[mask])
        predicted_pos = np.sum(weights[mask])
        actual_pos = np.sum(wp)  # Total expected positives
        return predicted_pos + actual_pos - tp

    return dinkelbach_optimize(p, numerator, denominator)


# ============================================================================
# Multiclass/Multilabel wrapper
# ============================================================================


def dinkelbach_expected_fbeta_multilabel(
    y_prob: np.ndarray[Any, Any],
    beta: float = 1.0,
    sample_weight: np.ndarray[Any, Any] | None = None,
    average: Literal["macro", "micro", "weighted"] = "macro",
    true_labels: np.ndarray[Any, Any] | None = None,
    comparison: str = ">",
) -> OptimizationResult:
    """Expected F-beta optimization for multilabel/multiclass.

    Parameters
    ----------
    y_prob : array of shape (n_samples, n_classes)
        Class probabilities
    beta : float
        F-beta parameter
    sample_weight : array of shape (n_samples,), optional
        Sample weights
    average : str
        Averaging strategy:
        - "macro": Per-class thresholds, unweighted mean
        - "micro": Single global threshold
        - "weighted": Per-class thresholds, weighted by true class frequencies
    true_labels : array of shape (n_samples,), optional
        True class labels. Required when average="weighted" to compute class
        frequencies.
        Should contain integer class indices from 0 to n_classes-1.
    comparison : str
        Comparison operator (kept for backward compatibility)

    Returns
    -------
    dict
        Results with 'thresholds' and 'score' keys
    """
    P = np.asarray(y_prob, dtype=np.float64)

    if P.ndim != 2:
        raise ValueError(f"Expected 2D probabilities, got shape {P.shape}")

    n_samples, n_classes = P.shape

    if average == "micro":
        # Flatten all probabilities into single binary problem
        p_flat = P.ravel()

        if sample_weight is not None:
            # Repeat weights for each class
            w_flat = np.repeat(sample_weight, n_classes)
        else:
            w_flat = None

        result = dinkelbach_expected_fbeta_binary(p_flat, beta, w_flat)
        threshold = result.threshold
        score = result.score

        # Create prediction function for micro averaging (single threshold for all classes)
        def predict_multiclass_micro(probs):
            p = np.asarray(probs)
            if p.ndim != 2:
                raise ValueError("Multiclass requires 2D probabilities")
            # Apply same threshold to all classes and predict highest valid probability
            thresholds = np.full(n_classes, threshold)
            if comparison == ">=":
                valid = p >= thresholds[None, :]
            else:
                valid = p > thresholds[None, :]
            masked = np.where(valid, p, -np.inf)
            predictions = np.argmax(masked, axis=1)

            # For samples where no class is above threshold, predict highest probability
            no_valid = np.all(~valid, axis=1)
            if np.any(no_valid):
                predictions[no_valid] = np.argmax(p[no_valid], axis=1)

            return predictions.astype(int)

        return OptimizationResult(
            thresholds=np.full(n_classes, threshold),
            scores=np.full(n_classes, score),
            predict=predict_multiclass_micro,
            metric=f"expected_f{beta}",
            n_classes=n_classes,
        )

    else:  # macro or weighted
        # Optimize per-class thresholds
        thresholds = np.zeros(n_classes)
        scores = np.zeros(n_classes)

        for k in range(n_classes):
            result = dinkelbach_expected_fbeta_binary(P[:, k], beta, sample_weight)
            thresholds[k] = result.threshold
            scores[k] = result.score

        # Note: Previous avg_score calculation removed as it was unused
        # Validate weighted averaging requirements
        if average == "weighted" and true_labels is None:
            raise ValueError(
                "Weighted averaging requires true_labels to compute class "
                "frequencies"
            )

        # Create prediction function for macro/weighted averaging (per-class thresholds)
        def predict_multiclass_macro(probs):
            p = np.asarray(probs)
            if p.ndim != 2:
                raise ValueError("Multiclass requires 2D probabilities")
            # Apply per-class thresholds and predict highest valid probability
            if comparison == ">=":
                valid = p >= thresholds[None, :]
            else:
                valid = p > thresholds[None, :]
            masked = np.where(valid, p, -np.inf)
            predictions = np.argmax(masked, axis=1)

            # For samples where no class is above threshold, predict highest probability
            no_valid = np.all(~valid, axis=1)
            if np.any(no_valid):
                predictions[no_valid] = np.argmax(p[no_valid], axis=1)

            return predictions.astype(int)

        return OptimizationResult(
            thresholds=thresholds,
            scores=scores,
            predict=predict_multiclass_macro,
            metric=f"expected_f{beta}",
            n_classes=n_classes,
        )


def expected_optimize_multiclass(
    probabilities: np.ndarray[Any, Any],
    metric: str = "f1",
    average: Literal["macro", "micro", "weighted"] = "macro",
    weights: np.ndarray[Any, Any] | None = None,
    **metric_params,
) -> OptimizationResult:
    """Expected optimization for multiclass/multilabel.

    Parameters
    ----------
    probabilities : array of shape (n_samples, n_classes)
        Class probabilities
    metric : str
        Metric to optimize ("f1", "precision", "jaccard")
    average : str
        Averaging strategy
    weights : array of shape (n_samples,), optional
        Sample weights
    **metric_params
        Additional parameters (e.g., beta for F-beta)

    Returns
    -------
    OptimizationResult
        Optimization result with thresholds, scores, and predict function
    """
    P = np.asarray(probabilities, dtype=np.float64)

    if P.ndim != 2:
        raise ValueError(f"Expected 2D probabilities, got shape {P.shape}")

    n_samples, n_classes = P.shape

    # Select metric function
    if metric.lower() in {"f1", "fbeta"}:
        beta = metric_params.get("beta", 1.0)

        def metric_fn(p, w):
            return dinkelbach_expected_fbeta_binary(p, beta, w)
    elif metric.lower() == "precision":
        metric_fn = expected_precision
    elif metric.lower() in {"jaccard", "iou"}:
        metric_fn = expected_jaccard
    else:
        raise ValueError(f"Unsupported metric: {metric}")

    # Handle different averaging strategies
    if average == "micro":
        # Flatten all probabilities into single binary problem
        p_flat = P.ravel()

        if weights is not None:
            # Repeat weights for each class
            w_flat = np.repeat(weights, n_classes)
        else:
            w_flat = None

        result_micro = metric_fn(p_flat, w_flat)
        if isinstance(result_micro, OptimizationResult):
            # For F1/Fbeta metrics
            threshold = result_micro.threshold
            score = result_micro.score
        else:
            # For precision/jaccard metrics that return tuples
            threshold, score = result_micro

        # Create prediction function for micro averaging
        def predict_micro(probs):
            p = np.asarray(probs)
            if p.ndim == 2:
                # Apply same threshold to all classes, predict argmax of those above threshold
                above_threshold = p > threshold
                if np.any(above_threshold, axis=1).all():
                    masked = np.where(above_threshold, p, -np.inf)
                    return np.argmax(masked, axis=1)
                else:
                    # Fallback to argmax for samples with no class above threshold
                    return np.argmax(p, axis=1)
            else:
                # Binary case
                return (p > threshold).astype(int)

        return OptimizationResult(
            thresholds=np.full(n_classes, threshold),
            scores=np.full(n_classes, score),
            predict=predict_micro,
            metric=f"expected_{metric}",
            n_classes=n_classes,
        )

    else:  # macro or weighted
        # Optimize per-class thresholds
        thresholds = np.zeros(n_classes)
        scores = np.zeros(n_classes)

        for k in range(n_classes):
            result_k = metric_fn(P[:, k], weights)
            if isinstance(result_k, OptimizationResult):
                # For F1/Fbeta metrics
                thresholds[k] = result_k.threshold
                scores[k] = result_k.score
            else:
                # For precision/jaccard metrics that return tuples
                thresholds[k], scores[k] = result_k

        # Weight by class frequency for weighted average
        if average == "weighted":
            # Weight by class frequency
            if weights is not None:
                class_weights = np.sum(P * weights[:, None], axis=0)
            else:
                class_weights = np.sum(P, axis=0)

            class_weights /= class_weights.sum()

        # Create prediction function for macro/weighted averaging
        def predict_macro(probs):
            p = np.asarray(probs)
            if p.ndim == 2:
                # Apply per-class thresholds, predict argmax of those above threshold
                above_threshold = p > thresholds[None, :]
                has_valid = np.any(above_threshold, axis=1)
                predictions = np.zeros(p.shape[0], dtype=int)
                
                # For samples with at least one class above threshold
                if np.any(has_valid):
                    masked = np.where(above_threshold, p, -np.inf)
                    predictions[has_valid] = np.argmax(masked[has_valid], axis=1)
                
                # For samples with no class above threshold, use argmax
                if np.any(~has_valid):
                    predictions[~has_valid] = np.argmax(p[~has_valid], axis=1)
                
                return predictions
            else:
                # Binary case - use first threshold
                return (p > thresholds[0]).astype(int)

        return OptimizationResult(
            thresholds=thresholds,
            scores=scores,
            predict=predict_macro,
            metric=f"expected_{metric}",
            n_classes=n_classes,
        )


# ============================================================================
# Simple API
# ============================================================================


def optimize_expected_threshold(
    probabilities: np.ndarray[Any, Any], metric: str = "f1", **kwargs
) -> float | np.ndarray[Any, Any]:
    """Simple API for expected threshold optimization.

    Parameters
    ----------
    probabilities : array
        Probabilities (1D for binary, 2D for multiclass)
    metric : str
        Metric to optimize
    **kwargs
        Additional parameters

    Returns
    -------
    float or array
        Optimal threshold(s)
    """
    p = np.asarray(probabilities)

    if p.ndim == 1:
        # Binary case
        if metric.lower() in {"f1", "fbeta"}:
            result = dinkelbach_expected_fbeta_binary(
                p, beta=kwargs.get("beta", 1.0)
            )
            return result.threshold
        elif metric.lower() == "precision":
            threshold, _ = expected_precision(p)
        elif metric.lower() in {"jaccard", "iou"}:
            threshold, _ = expected_jaccard(p)
        else:
            raise ValueError(f"Unknown metric: {metric}")

        return threshold

    else:
        # Multiclass case
        result = expected_optimize_multiclass(p, metric, **kwargs)
        return result.thresholds
