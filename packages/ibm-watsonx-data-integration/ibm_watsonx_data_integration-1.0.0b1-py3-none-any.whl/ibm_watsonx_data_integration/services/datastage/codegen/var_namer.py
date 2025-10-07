import keyword
import re


class VarNamer:
    def __init__(self):
        self.name_set = VarNameSet()

    def grant_name(self, name: str):
        """
        Convert an arbitrary string into a legal Python variable name.
        """
        # replace invalid chars with underscore
        name = re.sub(r"[^0-9a-zA-Z_]", "_", name)
        # prefix underscore if it starts with a digit
        if name and name[0].isdigit():
            name = "_" + name
        # fallback for empty string or all‐underscores
        if not name or name.strip("_") == "":
            name = "var"
        # insert underscore between uppercase sequences followed by a lowercase letter: SEQOne -> seq_one
        name = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", name)
        # insert underscores between camelCase or PascalCase words: camelCase → camel_case, PascalCase → pascal_case
        name = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", name)
        # convert all to lowercase
        name = name.lower()
        # avoid Python keywords
        if keyword.iskeyword(name):
            name += "_"

        return self.name_set.reserve(name)


class VarNameSet:
    def __init__(self, used_names=None):
        """
        Initialize with an iterable of names that are already taken.
        """
        self._used = set(used_names or [])

    def reserve(self, prefix: str) -> str:
        """
        Reserve and return a name starting with `prefix`.
        - If `prefix` isn't taken, returns `prefix`.
        - Otherwise returns `prefix_2`, `prefix_3`, ... picking the first free one.
        """
        # if prefix itself is free, use it
        if prefix not in self._used:
            name = prefix
        else:
            # otherwise find the lowest integer suffix that’s free
            i = 2
            while f"{prefix}_{i}" in self._used:
                i += 1
            name = f"{prefix}_{i}"
        self._used.add(name)
        return name

    def is_reserved(self, name: str) -> bool:
        """Check whether a name is already reserved."""
        return name in self._used

    def release(self, name: str) -> None:
        """Optionally free up a name so it can be reused later."""
        self._used.discard(name)
