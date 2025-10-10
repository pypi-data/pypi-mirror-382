def public(func):
    setattr(func, 'public', True)
    return func