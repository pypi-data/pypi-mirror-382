cimport cython
from libc.math cimport sqrt

@cython.cdivision(True)
cdef double estimate_causal_effect(
        int n_condition_is_true, 
        int n_condition_is_false,
        int n_condition_is_true_and_target_is_true,
        int n_condition_is_false_and_target_is_true,
        float beta = 2.0):
    cdef double causal_effect
    causal_effect = (n_condition_is_true_and_target_is_true + 1) / <double>(n_condition_is_true + 2)
    causal_effect -= (n_condition_is_false_and_target_is_true + 1) / <double>(n_condition_is_false + 2)
    causal_effect -= 0.5 * beta / sqrt(n_condition_is_true + 2)
    causal_effect -= 0.5 * beta / sqrt(n_condition_is_false + 2)
    return causal_effect    