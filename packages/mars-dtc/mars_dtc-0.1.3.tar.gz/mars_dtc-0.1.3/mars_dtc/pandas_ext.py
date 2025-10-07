# ---------------- Imports ----------------
import numpy as np

from mars_dtc.mars_dtc import MarsDate, MarsTimedelta
from pandas.api.extensions import ExtensionDtype, ExtensionArray, register_extension_dtype

# ---------------- Classes and functions ----------------


@register_extension_dtype
class MarsDateDtype(ExtensionDtype):
    name = "marsdate"
    type = MarsDate
    kind = "O"
    na_value = None

    @classmethod
    def construct_array_type(cls):
        return MarsDateArray 

    @property
    def _is_numeric(self):
        return False

    @property
    def _is_boolean(self):
        return False

    @property
    def _is_datetime(self):
        return True


class MarsDateArray(ExtensionArray):
    def __init__(self, values):
        self._data = np.asarray(values, dtype=object)
        converted = []
        for v in values:
            if v is None:
                converted.append(None)
            elif isinstance(v, MarsDate):
                converted.append(v)
            elif isinstance(v, int):
                # Treat integer as ordinal sol count
                converted.append(MarsDate.from_ordinal(v))
            elif isinstance(v, (float, np.floating)) and not np.isnan(v):
                # Also handle floats that represent ordinals
                converted.append(MarsDate.from_ordinal(int(v)))
            elif isinstance(v, str):
                # Accept flexible date string formats like '214-12-22', '214/12/22', '214.12.22'
                try:
                    converted.append(MarsDate.from_string(v))
                except Exception:
                    cleaned = v.strip().replace("-", "/").replace(".", "/").replace(" ", "/")
                    converted.append(MarsDate.from_string(cleaned))
            else:
                raise TypeError(
                    f"Invalid value type {type(v)} in MarsDateArray: {v}")
        self._data = np.asarray(converted, dtype=object)

    @classmethod
    def _from_sequence(cls, scalars, dtype=None, copy=False):
        return cls(list(scalars))

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"MarsDateArray({self._data})"

    def __add__(self, other):
        if isinstance(other, MarsTimedelta):

            return MarsDateArray([v.add_sols(other.sols) if v is not None else None for v in self._data])
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, MarsTimedelta):
            # Subtract a timedelta
            return MarsDateArray([v.add_sols(-other.sols) if v is not None else None for v in self._data])
        if isinstance(other, MarsDateArray):
            # Elementwise difference → return MarsTimedelta array (list)
            return np.array(
                [MarsTimedelta(v1.to_ordinal() - v2.to_ordinal()) if (v1 and v2)
                 else None for v1, v2 in zip(self._data, other._data)],
                dtype=object,
            )
        if isinstance(other, MarsDate):
            return np.array(
                [MarsTimedelta(v.to_ordinal() - other.to_ordinal())
                 if v is not None else None for v in self._data],
                dtype=object,
            )
        return NotImplemented


    @property
    def dtype(self):
        return MarsDateDtype()

    def isna(self):
        return np.array([x is None for x in self._data], dtype=bool)

    def take(self, indices, allow_fill=False, fill_value=None):
        result = []
        n = len(self)
        if allow_fill:
            if fill_value is None:
                fill_value = None
            for i in indices:
                if i == -1:
                    result.append(fill_value)
                else:
                    if i < -n or i >= n:
                        raise IndexError("take index out of bounds")
                    result.append(self._data[i])
        else:
            for i in indices:
                if i < -n or i >= n:
                    raise IndexError("take index out of bounds")
                result.append(self._data[i])
        return MarsDateArray(result)

    # Equality
    def __eq__(self, other):
        if isinstance(other, MarsDateArray):
            return np.array([a == b for a, b in zip(self._data, other._data)], dtype=object)
        elif isinstance(other, MarsDate):
            return np.array([a == other for a in self._data], dtype=object)
        else:
            return NotImplemented

    def _compare_op(self, other, op):
        if isinstance(other, MarsDateArray):
            return np.array([op(a, b) for a, b in zip(self._data, other._data)], dtype=bool)
        elif isinstance(other, MarsDate):
            return np.array([op(a, other) for a in self._data], dtype=bool)
        else:
            raise TypeError(f"Cannot compare MarsDateArray with {type(other)}")

    def __ge__(self, other):
        import operator
        return self._compare_op(other, operator.ge)

    def __le__(self, other):
        import operator
        return self._compare_op(other, operator.le)

    def __gt__(self, other):
        import operator
        return self._compare_op(other, operator.gt)

    def __lt__(self, other):
        import operator
        return self._compare_op(other, operator.lt)


    def copy(self):
        return MarsDateArray(self._data.copy())

    def _from_factorized(self, uniques, original):
        return MarsDateArray(list(uniques))

    def _values_for_argsort(self):
        out = np.empty(len(self._data), dtype="float64")
        for i, v in enumerate(self._data):
            out[i] = np.nan if v is None else v.to_ordinal()
        return out

    def _values_for_plotting(self):
        return np.array([np.nan if v is None else v.to_ordinal() for v in self._data], dtype="float64")

    def _formatter(self, boxed=False):

        def format_func(x):
            if x is None:
                return "NaT"
            return str(x)
        return format_func


    def __array__(self, dtype=None, copy=None):
        arr = np.array(
            [np.nan if v is None else v.to_ordinal() for v in self._data],
            dtype="float64" if dtype is None else dtype,
        )
        if copy:
            arr = arr.copy()
        return arr


    def to_numpy(self, dtype=None, copy=False, na_value=np.nan):
        return np.array(
            [na_value if v is None else v.to_ordinal() for v in self._data],
            dtype="float64" if dtype is None else dtype,
        )


    def _reduce(self, name, skipna=True, **kwargs):
        vals = [v for v in self._data if v is not None]
        if not vals:
            return None
        if name == "min":
            return min(vals)
        if name == "max":
            return max(vals)
        raise TypeError(f"Reduction '{name}' not supported for MarsDateArray")

    def floor(self, freq="month"):
        return MarsDateArray([v.floor(freq) if v is not None else None for v in self._data])

    def ceil(self, freq="month"):
        return MarsDateArray([v.ceil(freq) if v is not None else None for v in self._data])

    def round(self, freq="month"):
        return MarsDateArray([v.round(freq) if v is not None else None for v in self._data])

    def diff(self, periods: int = 1, sort_before: bool = False):

        from mars_dtc.mars_dtc import MarsTimedelta

        if sort_before:

            valid = [v for v in self._data if v is not None]
            valid_sorted = sorted(valid, key=lambda x: x.to_ordinal())
            arr = list(valid_sorted)
        else:
            arr = list(self._data)

        result = []
        for i in range(len(arr)):
            if i < periods or arr[i] is None or arr[i - periods] is None:
                result.append(None)
            else:
                diff_val = arr[i].to_ordinal() - arr[i - periods].to_ordinal()
                result.append(MarsTimedelta(diff_val))
        return np.array(result, dtype=object)


# Let the dtype name resolve to the class object for construct_array_type
globals()["MarsDateArray"] = MarsDateArray

