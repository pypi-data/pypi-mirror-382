"""
Computes the cross-correlation between a reference signal and a subject signal,
assessing their similarity over a synchronized time span.
"""

import numpy as np


def cross_correlation(reference, subject, verbose=False):
    """
    Computes the cross-correlation between a reference signal and a subject signal,
    assessing their similarity over a synchronized time span.

    The function aligns the two signals by resampling them onto a common time grid,
    computes the cross-correlation, and determines the optimal time shift for maximum correlation.
    It also evaluates the relative error and L2-norm error rate between the signals.

    Parameters:
    -----------
    reference : ndarray
        A 2D NumPy array of shape (N, 2) representing the reference signal.
        The first column contains time values, and the second column contains signal values.

    subject : ndarray
        A 2D NumPy array of shape (M, 2) representing the subject signal.
        The first column contains time values, and the second column contains signal values.

    verbose : bool, optional (default=False)
        If True, prints detailed intermediate results for debugging and analysis.

    Returns:
    --------
    t_span_corr : ndarray
        The synchronized time vector after cross-correlation.

    y_span_corr : ndarray
        The subject signal interpolated and shifted to best align with the reference signal.

    rel_corr_error : float
        The relative error between the maximum cross-correlation and the self-correlation of the reference signal.

    L2_norm_error_rate : float
        The L2-norm of the difference between the aligned subject signal and the reference signal,
        normalized by the number of samples.

    Notes:
    ------
    - The function normalizes time intervals to ensure proper synchronization.
    - Cross-correlation is performed using NumPy’s `np.correlate` function.
    - The optimal time shift is determined by the peak of the cross-correlation function.
    - Interpolation is used to handle differences in time sampling between the two signals.

    Example:
    --------
    >>> import numpy as np
    >>> ref_signal = np.array([[0, 1], [1, 2], [2, 3], [3, 4]])
    >>> sub_signal = np.array([[0, 1.1], [1, 2.1], [2, 3.1], [3, 4.1]])
    >>> t_corr, y_corr, rel_err, l2_err = cross_correlation(ref_signal, sub_signal)
    >>> print(rel_err, l2_err)
    """

    if verbose:
        print("\nThis is xymodel.cross_correlation...")
        print(f"reference: {reference}")
        print(f"subject: {subject}")

    ref_delta_t = reference[1, 0] - reference[0, 0]
    ref_t_min = reference[0, 0]
    ref_t_max = reference[-1, 0]

    dt = subject[1, 0] - subject[0, 0]  # sample delta t
    t_min = subject[0, 0]
    t_max = subject[-1, 0]

    # globalized interval and frequency
    DT = np.minimum(ref_delta_t, dt)
    T_MIN = np.minimum(ref_t_min, t_min)
    T_MAX = np.maximum(ref_t_max, t_max)

    n_samples = int((T_MAX - T_MIN) / DT) + 1
    t_span = np.linspace(T_MIN, T_MAX, n_samples, endpoint=True)

    if verbose:
        print("\nSynchronization...")
        print(
            f"  Reference [t_min, t_max] by dt (s): [{ref_t_min}, {ref_t_max}] by {ref_delta_t}"
        )
        print(
            f"  Subject [t_min, t_max] by dt (s): [{t_min}, {t_max}] by {dt}"
        )
        print(
            f"  Globalized [t_min, t_max] by dt (s): [{T_MIN}, {T_MAX}] by {DT}"
        )
        print(f"  Globalized times: {t_span}")
        print(f"  Length of globalized times: {len(t_span)}")

    ref_y_span = np.interp(
        t_span, reference[:, 0], reference[:, 1], left=0.0, right=0.0
    )

    y_span = np.interp(
        t_span, subject[:, 0], subject[:, 1], left=0.0, right=0.0
    )

    cross_corr = np.correlate(ref_y_span, y_span, mode="full")
    cross_corr_max = np.max(cross_corr)

    cross_corr_unit = np.correlate(
        ref_y_span / np.linalg.norm(ref_y_span),
        y_span / np.linalg.norm(y_span),
        mode="full",
    )

    ref_self_corr = np.correlate(ref_y_span, ref_y_span)[
        0
    ]  # self correlated reference
    rel_corr_error = 0.0

    if ref_self_corr > 0:
        rel_corr_error = abs(cross_corr_max - ref_self_corr) / ref_self_corr

    offset_index = np.argmax(cross_corr)

    # shift time full-left, then incrementally to the right
    # t_shift = t_span - t_span[-1] + t_span[offset_index]  # nope!
    # t_shift = t_span - t_span[-1] + offset_index * DT  # bug! should shift to t0 referance signal
    t_shift = t_span - t_span[-1] + t_span[0] + offset_index * DT

    T_MIN_CORR = np.minimum(ref_t_min, t_shift[0])
    T_MAX_CORR = np.maximum(ref_t_max, t_shift[-1])

    n_samples_corr = (
        int((T_MAX_CORR - T_MIN_CORR) / DT) + 1
    )  # DT unchanged pre-shift
    t_span_corr = np.linspace(
        T_MIN_CORR, T_MAX_CORR, n_samples_corr, endpoint=True
    )

    ref_y_span_corr = np.interp(
        t_span_corr, reference[:, 0], reference[:, 1], left=0.0, right=0.0
    )

    y_span_corr = np.interp(t_span_corr, t_shift, y_span, left=0.0, right=0.0)

    error = y_span_corr - ref_y_span_corr

    L2_norm_error_rate = np.linalg.norm(error) / n_samples_corr

    if verbose:
        print("\nCorrelation...")
        print(f"  Sliding dot product (cross-correlation): {cross_corr}")
        print(f"  Length of the sliding dot product: {len(cross_corr)}")
        print(
            f"  Max sliding dot product (cross-correlation): {cross_corr_max}"
        )
        print(
            f"  Sliding dot product of normalized signals (cross-correlation): {cross_corr_unit}"
        )

        print(f"  Correlated time_shift (from full left)={offset_index * DT}")
        print(f"  Correlated index_shift (from full left)={offset_index}")

        print(f"  Correlated time step (s): {DT}")
        print(f"  Correlated t_min (s): {T_MIN_CORR}")
        print(f"  Correlated t_max (s): {T_MAX_CORR}")
        print(f"  Correlated times: {t_span_corr}")
        print(f"  Correlated reference f(t): {ref_y_span_corr}")
        print(f"  Correlated subject f(t): {y_span_corr}")
        print(f"  Correlated error f(t): {error}")

        print(f"  reference_self_correlation: {ref_self_corr}")
        print(f"  cross_correlation: {cross_corr_max}")
        print(f"    >> cross_correlation_relative_error={rel_corr_error}")
        print(f"    >> L2-norm error rate: {L2_norm_error_rate}")

    return t_span_corr, y_span_corr, rel_corr_error, L2_norm_error_rate
