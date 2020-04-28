from functools import reduce, wraps


def compose(*decorators):
    def inner(func):
        composed = reduce(lambda f, d: d(f), reversed(decorators), func)
        return wraps(func)(composed)

    return inner
