def evaluate_yield_stress_limit_state(x, threshold, yield_stress):
    return {"g": threshold - yield_stress}
