"""Optimized O(n log n) sort-and-scan kernel for piecewise-constant metrics.

This module provides an exact optimizer for binary classification metrics that are
piecewise-constant with respect to the decision threshold. The algorithm sorts
predictions once and scans all n cuts in a single pass, achieving true O(n log n)
complexity with vectorized operations.

Notes on `require_proba`:
- If `require_proba=True`, inputs are validated to lie in [0, 1].
- The returned threshold is *usually* in [0, 1]; however, in boundary or tie cases,
  we may nudge it by one floating-point ULP beyond the range to correctly realize
  strict inclusivity/exclusivity (e.g., to ensure “predict none” with '>=' when max p == 1.0).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from .metrics import (
    _confusion_matrix_from_labels,
    apply_metric_to_confusion_counts,
    compute_vectorized_confusion_matrices,
)
from .types_minimal import OptimizationResult
from .validation import validate_binary_classification, validate_weights

Array = np.ndarray[Any, Any]

# NOTE: NUMERICAL_TOLERANCE moved to function parameters for user control


def _compute_threshold_midpoint(
    p_sorted: Array, k_star: int, inclusive: bool = False, tolerance: float = 1e-10
) -> float:
    """Compute threshold as midpoint between adjacent sorted scores.

    With k indexed so that:
      k = 0: predict none positive (threshold > max score)
      k = 1..n-1: predict top-k items positive
      k = n: predict all positive (threshold <= min score)
    """
    n = p_sorted.size

    # k == 0: threshold must exclude every score
    if k_star == 0:
        max_prob = float(p_sorted[0])
        # For '>=', make threshold strictly greater than max_prob to exclude ties
        return float(np.nextafter(max_prob, np.inf)) if inclusive else max_prob

    # k == n: threshold must include every score
    if k_star == n:
        min_prob = float(p_sorted[-1])
        # For '>', make threshold strictly smaller than min_prob to include ties
        return float(np.nextafter(min_prob, -np.inf)) if not inclusive else min_prob

    # General case: separate p_sorted[k_star-1] (included) and p_sorted[k_star] (excluded)
    inc = float(p_sorted[k_star - 1])
    exc = float(p_sorted[k_star])

    if inc - exc > tolerance:
        thr = 0.5 * (inc + exc)
        # For '>=' we bias a half-ulp downward so equals land in the included side
        return float(np.nextafter(thr, -np.inf)) if inclusive else thr

    # Tied (or nearly tied) scores: choose side per operator
    tied = exc
    # For '>', place threshold just above tied to exclude equals.
    # For '>=', place just below tied to include equals.
    return float(np.nextafter(tied, np.inf)) if not inclusive else float(np.nextafter(tied, -np.inf))


def _realized_k(p_sorted: Array, threshold: float, inclusive: bool) -> int:
    """Given a threshold and comparison mode, return #positives among p_sorted (desc)."""
    # Convert to ascending by negation and use searchsorted with the right side
    q = -p_sorted
    t = -threshold
    side = "right" if inclusive else "left"
    return int(np.searchsorted(q, t, side=side))


def _predict_from_threshold(probs: Array, threshold: float, inclusive: bool) -> Array:
    """Predict labels (0/1) from probabilities and threshold."""
    p = np.asarray(probs)
    if p.ndim == 2 and p.shape[1] == 2:
        p = p[:, 1]
    elif p.ndim == 2 and p.shape[1] == 1:
        p = p.ravel()
    return (p >= threshold).astype(np.int32) if inclusive else (p > threshold).astype(np.int32)


def optimal_threshold_sortscan(
    y_true: Array,
    pred_prob: Array,
    metric_fn: Callable[[Array, Array, Array, Array], Array],
    *,
    sample_weight: Array | None = None,
    inclusive: bool = False,   # True for ">=", False for ">"
    require_proba: bool = True,
    tolerance: float = 1e-10,
) -> OptimizationResult:
    """Exact optimizer for piecewise-constant metrics using O(n log n) sort-and-scan.

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Binary labels in {0, 1}.
    pred_prob : array-like of shape (n_samples,)
        Predicted probabilities in [0, 1] or arbitrary scores if require_proba=False.
    metric_fn : callable
        Vectorized metric: (tp_vec, tn_vec, fp_vec, fn_vec) -> score_vec.
        Each input/output is a 1D array over the n+1 possible cuts (k=0..n).
    sample_weight : array-like, optional
        Non-negative sample weights of shape (n_samples,).
    inclusive : bool, default=False
        If True, use ">="; if False, use ">".
    require_proba : bool, default=True
        Validate inputs in [0, 1]. Threshold may be nudged by ±1 ULP outside [0,1]
        to exactly realize inclusivity/exclusivity in boundary/tie cases.
    tolerance : float, default=1e-10
        Numerical tolerance for floating-point comparisons when computing
        threshold midpoints and handling ties between scores.

    Returns
    -------
    OptimizationResult
        thresholds : array([optimal_threshold])
        scores     : array([achieved_score])
        predict    : callable(probs) -> {0,1}^n
        metric     : str, set to "piecewise_metric"
        n_classes  : 2
        diagnostics: dict with keys:
            - k_argmax: theoretical best cut index (0..n) from the sweep
            - k_realized: positives realized by the returned threshold
            - score_theoretical: score at k_argmax
            - score_actual: score achieved by the returned threshold
            - tie_discrepancy: abs(theoretical - actual)
            - inclusive: bool
            - require_proba: bool
    """
    # 1) Validate inputs
    y, p, _ = validate_binary_classification(y_true, pred_prob, require_proba=require_proba)
    n = y.shape[0]
    weights = (
        validate_weights(sample_weight, n)
        if sample_weight is not None
        else np.ones(n, dtype=np.float64)
    )

    # 2) Sort once by descending score (stable)
    order = np.argsort(-p, kind="mergesort")
    y_sorted = y[order]
    p_sorted = p[order]
    w_sorted = weights[order]

    # 3) Vectorized confusion counts at all n+1 cuts (k=0..n)
    tp_vec, tn_vec, fp_vec, fn_vec = compute_vectorized_confusion_matrices(y_sorted, w_sorted)

    # 4) Vectorized metric over all cuts; take argmax
    score_vec = apply_metric_to_confusion_counts(metric_fn, tp_vec, tn_vec, fp_vec, fn_vec)
    k_star = int(np.argmax(score_vec))
    score_theoretical = float(score_vec[k_star])

    # 5) Convert k* to a concrete threshold with correct > / >= semantics
    threshold = _compute_threshold_midpoint(p_sorted, k_star, inclusive, tolerance)

    # 6) Evaluate the achieved score at that threshold (handles ties & numerics)
    pred_labels = _predict_from_threshold(p, threshold, inclusive)
    tp, tn, fp, fn = _confusion_matrix_from_labels(y, pred_labels, sample_weight=weights)
    score_actual = float(metric_fn(
        np.array([tp]), np.array([tn]), np.array([fp]), np.array([fn])
    )[0])

    # 7) If the realized score differs meaningfully (e.g., due to ties), probe a few
    #    locally optimal alternatives (extremes and one-ULP nudges around the boundary).
    tie_discrepancy = abs(score_actual - score_theoretical)
    if tie_discrepancy > max(1e-6, 100 * tolerance):
        best_thr = threshold
        best_score = score_actual

        min_s = float(p_sorted[-1])
        max_s = float(p_sorted[0])

        candidates: list[float] = []
        if inclusive:
            # Include all vs exclude all
            candidates.extend([min_s, float(np.nextafter(max_s, np.inf))])
        else:
            candidates.extend([float(np.nextafter(min_s, -np.inf)), max_s])

        if 0 < k_star < n:
            inc = float(p_sorted[k_star - 1])  # last included by k*
            exc = float(p_sorted[k_star])      # first excluded by k*
            candidates.extend([
                float(np.nextafter(inc, -np.inf)),  # just below included
                float(np.nextafter(exc, np.inf)),   # just above excluded
            ])

        # Evaluate candidates
        for t in candidates:
            # If require_proba, clamp only if it does not alter intended decision boundary;
            # we accept tiny excursions beyond [0,1] when necessary for semantics.
            t_eval = t
            pred_labels_alt = _predict_from_threshold(p, t_eval, inclusive)
            tp2, tn2, fp2, fn2 = _confusion_matrix_from_labels(y, pred_labels_alt, sample_weight=weights)
            s2 = float(metric_fn(
                np.array([tp2]), np.array([tn2]), np.array([fp2]), np.array([fn2])
            )[0])
            if s2 > best_score:
                best_score = s2
                best_thr = t_eval

        threshold = best_thr
        score_actual = best_score

    # 8) Diagnostics and final return
    k_real = _realized_k(p_sorted, threshold, inclusive)

    def predict_binary(probs: Array) -> Array:
        return _predict_from_threshold(probs, threshold, inclusive)

    diagnostics = {
        "k_argmax": k_star,
        "k_realized": k_real,
        "score_theoretical": score_theoretical,
        "score_actual": score_actual,
        "tie_discrepancy": abs(score_actual - score_theoretical),
        "inclusive": inclusive,
        "require_proba": require_proba,
    }

    return OptimizationResult(
        thresholds=np.array([float(threshold)], dtype=float),
        scores=np.array([float(score_actual)], dtype=float),
        predict=predict_binary,
        metric="piecewise_metric",
        n_classes=2,
        diagnostics=diagnostics,
    )
