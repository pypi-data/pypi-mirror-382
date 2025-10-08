"""Collection of generic Python utilities."""

from __future__ import annotations

import subprocess  # noqa: S404
import weakref
from bisect import bisect_left
from enum import EnumMeta, IntEnum

import numpy as np


class StrEnumBase(IntEnum):
    __mapping__: list[tuple[str, int]] = []
    # default for when there is value. Leaving None throws an error
    __default__ = None
    # default when the string is not found in the mapping
    __invalid__ = None

    @classmethod
    def from_string(cls, s: str):
        if not s:
            return cls(cls.__default__)
        mapping = dict(cls.__mapping__)
        return cls(mapping.get(s.lower(), cls.__invalid__ if cls.__invalid__ is not None else s))

    def to_string(self) -> str:
        reverse__mapping__ = {v: k for k, v in self.__mapping__}
        return reverse__mapping__[self]

    def __str__(self):
        return f"{self.__class__.__name__}.{self.name}"

    @classmethod
    def default(cls):
        return cls(cls.__default__)


class CumulativeError(Exception):
    def __init__(self, errors=None):
        self.errors = errors or []
        self.is_error_appended = False

    def append(self, func_name, err):
        self.errors.append((func_name, err))
        self.is_error_appended = True

    def __bool__(self):
        return bool(self.errors)

    def __str__(self):
        if not self.errors:
            return "No errors."
        messages = [f"{func_name}: {type(err).__name__} -> {err}" for func_name, err in self.errors]
        return "Operation failed with multiple errors:\n" + "\n".join(messages)

    def raise_if_any(self):
        if self:
            raise self


def dict_filter_map(dic, mapp):
    """Filters a dict and converts the keys according to a given map"""
    return {mapp[key]: val for key, val in dic.items() if key in mapp}


def docopt_sanitize(docopt_opts):
    """Sanitizes docopt parsed key names"""
    opts = {}
    for key, val in docopt_opts.items():
        key = key.strip("<>-").replace("-", "_")
        if isinstance(val, str):
            if val.lower() in {"off", "false"}:
                val = False
            elif val.lower() in {"on", "true"}:
                val = True
        opts[key] = val
    return opts


class WeakList(list):  # noqa: FURB189
    def append(self, item):
        list.append(self, weakref.ref(item, self.remove))


class ConfigT:
    """Base class for configurations.

    This class serves as a base for set of configurations.
    By inheriting and setting several class-level attributes, instances will
    be able to initialize from kwargs and dictionaries with the same keys,
    effectively working as validators of fields with default values.
    Furthermore, for validation of values, the attributes may be Enums.

    ::\n
     class RunConfig(ConfigT):
        # NOTE: Enum fields: the FIRST value is the default
        mode = Enum("Mode", "BUILD_SIMULATE BUILD_ONLY")
        model_path = None
    """

    class _ConfigFlag:
        """A lightweith internal class to create flags"""

        __slots__ = ()

    REQUIRED = _ConfigFlag()

    def __init__(self, opt_dict=None, **opts):
        opt_dict = opt_dict or {}
        opt_dict.update(opts)
        self._init(self, opt_dict)

    @classmethod
    def _init(cls, obj, opts):
        for name, value in opts.items():
            if value is not None and not name.startswith("_") and hasattr(obj, name):
                default = getattr(obj, name)
                if type(default) is EnumMeta:
                    value = default[value]  # enum as validator
                setattr(obj, name, value)

        for name, value in cls.__dict__.items():
            if name not in obj.__dict__ and (value is cls.REQUIRED or type(value) is EnumMeta):
                raise ValueError(f"Config field {name} is mandatory")

        obj._all = opts

    # dict interface for compat
    def __setitem__(self, name, value):
        self._all[name] = value

    def __getitem__(self, name):
        return self._all[name]

    def get(self, *args):
        return self._all.get(*args)

    def __contains__(self, name):
        return name in self._all

    all = property(lambda self: self._all)

    def as_dict(self, subset=None, excludes=()):
        return {
            key: val
            for key, val in vars(self).items()
            if val is not None
            and not key.startswith("_")
            and key not in excludes
            and (subset is None or key in subset)
        }


def bin_search(container, key, keyf=None):
    """Performs binary search in a container, retrieving the index where key should be inserted
    to keep ordering. Accepts a key function to be applied to each element of the container.

    Args:
        container: The container to be searched through
        key: The key to look for
        keyf: (Optional) the function transforming container elements into comparable keys

    Returns: The position where the element is to be inserted to keep ordering.

    """
    if keyf is None:
        return bisect_left(container, key)

    binsrch_low = 0
    binsrch_high = len(container)

    while binsrch_low < binsrch_high:
        binsrch_mid = int((binsrch_low + binsrch_high) * 0.5)
        if key > keyf(container[binsrch_mid]):
            binsrch_low = binsrch_mid + 1
        else:
            binsrch_high = binsrch_mid
    return binsrch_low


class ConsoleColors:
    """Helper class for formatting console text."""

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, _, DEFAULT = range(30, 40)
    NORMAL, BOLD, DIM, UNDERLINED, BLINK, INVERTED, HIDDEN = [a << 8 for a in range(7)]

    # These are the sequences needed to control output
    _CHANGE_SEQ = "\033[{}m"
    _RESET_SEQ = "\033[0m"

    @classmethod
    def reset(cls):
        return cls._RESET_SEQ

    @classmethod
    def format_text(cls, text, color, style=None):
        style = (style or color) >> 8
        format_seq = str(color & 0x00FF) + ((";" + str(style)) if style else "")
        return cls._CHANGE_SEQ.format(format_seq) + text + cls._RESET_SEQ


def append_recarray(target_array, record):
    """Append a np.record to a np.recarray"""
    if target_array is None:
        target_array = np.recarray(1, dtype=record.dtype)
        target_array[0] = record
    elif not isinstance(target_array, np.recarray) or target_array.dtype != record.dtype:
        raise TypeError("Can not append a recode with a different dtype to the target array")
    else:
        nrows = target_array.shape[0]
        target_array.resize(nrows + 1, refcheck=False)
        target_array[nrows] = record
    return target_array


def gen_ranges(limit, blocklen, low=0, block_increase_rate=1):
    """Generates ranges in block intervals for a given length
    block_increase_rate may be >1 in case we want the block to get increasingly large
    """
    while low < limit:
        high = min(low + blocklen, limit)
        yield low, high
        low = high
        blocklen = int(blocklen * block_increase_rate)


def rmtree(path):
    """Recursively remove a path

    Note: shutils.rmtree wouldn't complete for directories with many files.
    See:
    https://github.com/openbraininstitute/neurodamus/pull/247/files/e9d12100b22bf512fdcd624022d9d999cb50db77#r2079776328  # noqa: E501
    """  # noqa: E501
    subprocess.call(["/bin/rm", "-rf", path])  # noqa: S603


def cache_errors(func):
    """Decorator that catches exceptions and appends
    (func name, exception) to `cumulative_error` if provided.
    """

    def wrapper(*args, cumulative_error: CumulativeError | None = None, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if cumulative_error is not None:
                cumulative_error.append(func.__name__, e)
            else:
                raise
            return None

    return wrapper
