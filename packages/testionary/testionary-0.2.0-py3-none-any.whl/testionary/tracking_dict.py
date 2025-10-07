class TrackingDict(dict):
    """A wrapper around dictionaries to help track access and modification to keys.

    Tracking Attributes:
        accessed_keys: Keys that has been accessed directly
        modified_keys: Keys that has had values modified after the initial creation
        has_been_iterated: True if the dictionary has been iterated over or had common iteration operations called (e.g. values() or items()), False otherwise.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.accessed_keys = set()
        self.modified_keys = set()
        self.has_been_iterated = False

    def __getitem__(self, key):
        self.accessed_keys.add(key)
        return super().__getitem__(key)

    def get(self, key, default=None, /):
        self.accessed_keys.add(key)
        return super().get(key, default)

    def __setitem__(self, key, value):
        self.modified_keys.add(key)
        return super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        kwargs = dict(kwargs)
        if args:
            other = args[0]
            if hasattr(other, "keys"):
                self.modified_keys.update(other.keys())
            else:
                self.modified_keys.update(k for k, _ in other)
            return super().update(other)
        else:
            self.modified_keys.update(kwargs.keys())
            return super().update(**kwargs)

    def __ior__(self, other):
        if hasattr(other, "keys"):
            self.modified_keys.update(other.keys())
        else:
            self.modified_keys.update(k for k, _ in other)
        return super().__ior__(other)

    def __iter__(self):
        self.has_been_iterated = True
        return super().__iter__()

    def __contains__(self, key):
        self.has_been_iterated = True
        return super().__contains__(key)

    def items(self):
        self.has_been_iterated = True
        return super().items()

    def keys(self):
        self.has_been_iterated = True
        return super().keys()

    def values(self):
        self.has_been_iterated = True
        return super().values()
