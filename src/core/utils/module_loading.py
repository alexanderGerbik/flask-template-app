from importlib import import_module


def import_string(dotted_path):
    """
    Import a module by the given import path and return the attribute
    which is separated by the colon from the import path.
    Return module if the attribute is not given.
    Raise ImportError if the import failed.
    """
    if ":" not in dotted_path:
        module_path, attribute = dotted_path, None
    else:
        module_path, attribute = dotted_path.rsplit(":", 1)

    module = import_module(module_path)

    if not attribute:
        return module

    try:
        attr = getattr(module, attribute)
    except AttributeError:
        raise ImportError(
            f"Module '{module_path}' doesn't have a '{attribute}' attribute"
        ) from None
    return attr
