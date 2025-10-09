def estimate_causal_effect(
        n_condition_is_true: int, 
        n_condition_is_false: int,
        n_condition_is_true_and_target_is_true: int,
        n_condition_is_false_and_target_is_true: int,
        beta: float = 2.0) -> float: ...
    """ 
    estimates the causal effect based on https://eda.mmci.uni-saarland.de/pubs/2021/dice-budhathoki,boley,vreeken.pdf
    """