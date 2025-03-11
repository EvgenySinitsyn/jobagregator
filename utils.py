def filter_params(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}
