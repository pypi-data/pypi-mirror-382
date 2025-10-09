cdef double estimate_causal_effect(
        int n_condition_is_true, 
        int n_condition_is_false,
        int n_condition_is_true_and_target_is_true,
        int n_condition_is_false_and_target_is_true,
        float beta = ?)