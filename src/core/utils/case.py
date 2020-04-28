import re


def camel_to_snake_case(name):
    s1 = _first_cap_re.sub(r"\1_\2", name)
    return _all_cap_re.sub(r"\1_\2", s1).lower()


def snake_to_camel_case(name):
    parts = iter(name.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def hyphen_to_snake_case(name):
    return name.replace("-", "_")


def snake_to_hyphen_case(name):
    return name.replace("_", "-")


_first_cap_re = re.compile("(.)([A-Z][a-z]+)")
_all_cap_re = re.compile("([a-z0-9])([A-Z])")
