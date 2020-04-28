class Registry:
    discriminator = None
    _cache = {}

    def __init_subclass__(cls, **kwargs):
        if cls.discriminator:
            if cls.discriminator in cls._cache:
                name = cls._cache[cls.discriminator].__name__
                raise TypeError(
                    f"{name} is already registered for '{cls.discriminator}'"
                )
            cls._cache[cls.discriminator] = cls

    @classmethod
    def _create(cls, discriminator, *args, **kwargs):
        class_ = cls._cache[discriminator]
        return class_(*args, **kwargs)
