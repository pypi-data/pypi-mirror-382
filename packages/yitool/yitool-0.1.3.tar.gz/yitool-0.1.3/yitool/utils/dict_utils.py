from deepmerge import always_merger
from typing import Any, Optional


class DictUtils(object):
    """字典工具类"""

    @staticmethod
    def is_empty(d: Optional[dict]) -> bool:
        """Check if the dictionary is empty or None."""
        return d is None or len(d) == 0

    @staticmethod
    def safe(d: Optional[dict]) -> dict:
        """Ensure the input is a dictionary, return empty dict if None."""
        return d if d is not None else {}

    @staticmethod
    def get_value_case_insensitive(d: dict, key: str, default: Any = None) -> Any:
        """Get a value from a dictionary in a case-insensitive manner."""
        if DictUtils.is_empty(d):
            return default
        for k, v in d.items():
            if isinstance(k, str) and k.lower() == key.lower():
                return v
        return default

    @staticmethod
    def get_value_or_raise(d: dict, key: str) -> Any:
        """Get a value from a dictionary if the key exists, otherwise raise KeyError."""
        if key in d:
            return d[key]
        raise KeyError(f"Key not found: {key}")

    @staticmethod
    def get(d: Optional[dict], key: str, default: Any = None, insensitive: bool = False) -> Any:
        """Get a value from a dictionary if the key exists, otherwise return default."""
        if d is None:
            return default
        if insensitive:
            return DictUtils.get_value_case_insensitive(d, key, default)
        return d.get(key, default)

    @staticmethod
    def set(d: Optional[dict], key: str, value: Any) -> None:
        """Set a value in a dictionary."""
        if d is None:
            raise ValueError("Cannot set value on a None dictionary.")
        d[key] = value

    @staticmethod
    def delete(d: Optional[dict], key: str) -> None:
        """Delete a key from a dictionary if it exists."""
        if d is None:
            return
        if key in d:
            del d[key]

    @staticmethod
    def shallow_merge(base: Optional[dict], override: Optional[dict]) -> dict:
        """Merge two dictionaries shallowly, with values from 'override' taking precedence."""
        base = DictUtils.safe(base)
        override = DictUtils.safe(override)
        merged = base.copy()
        merged.update(override)
        return merged

    @staticmethod
    def deep_merge(base: Optional[dict], override: Optional[dict]) -> dict:
        """Merge two dictionaries deeply, with values from 'override' taking precedence."""
        base = DictUtils.safe(base)
        override = DictUtils.safe(override)
        return always_merger.merge(base, override)