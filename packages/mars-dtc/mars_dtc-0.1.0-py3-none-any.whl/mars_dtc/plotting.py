# ---------------- Imports ----------------
import matplotlib.units as munits
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from mars_dtc.mars_dtc import MarsDate
from mars_dtc.pandas_ext import MarsDateArray


# ---------------- Classes and functions ----------------
class MarsDateConverter(munits.ConversionInterface):
    @staticmethod
    def convert(value, unit, axis):
        if isinstance(value, MarsDate):
            return value.to_ordinal()
        if isinstance(value, MarsDateArray):
            return value._values_for_plotting()
        if isinstance(value, (list, np.ndarray)):
            return [np.nan if v is None else (v.to_ordinal() if isinstance(v, MarsDate) else v) for v in value]
        return value

    @staticmethod
    def axisinfo(unit, axis):
        majloc = mticker.MaxNLocator(integer=True)
        def fmt(x, pos):
            if np.isnan(x):
                return "NaT"
            return str(MarsDate.from_ordinal(int(x)))
        majfmt = mticker.FuncFormatter(fmt)
        return munits.AxisInfo(majloc=majloc, majfmt=majfmt)

    @staticmethod
    def default_units(x, axis):
        return None

munits.registry[MarsDate] = MarsDateConverter()
munits.registry[MarsDateArray] = MarsDateConverter()




def plot(data, kind=None, **kwargs):

    xcol = kwargs.get("x", None)
    if xcol is not None:
        ser = data[xcol]
        is_mars = getattr(getattr(ser, "dtype", None), "name", "") == "marsdate"
        if is_mars:
            import matplotlib.pyplot as plt
            ax = kwargs.pop("ax", None)
            if ax is None:
                _, ax = plt.subplots()


            x_numeric = ser.to_numpy()
            yarg = kwargs.pop("y", None)
            ycols = (
                [yarg] if isinstance(yarg, (str, int))
                else list(yarg) if yarg
                else [c for c in data.columns if c != xcol]
            )

            for col in ycols:
                ax.plot(x_numeric, data[col].to_numpy(), label=str(col), **kwargs)

            from matplotlib.ticker import FuncFormatter
            ax.xaxis.set_major_formatter(
                FuncFormatter(
                    lambda x, pos: "NaT"
                    if np.isnan(x)
                    else str(mdt.MarsDate.from_ordinal(int(x)))
                )
            )
            ax.set_xlabel(str(xcol))
            ax.legend()
            ax.grid(True)
            return ax

    # fallback: call Matplotlib manually
    import matplotlib.pyplot as plt
    ax = kwargs.pop("ax", None)
    if ax is None:
        _, ax = plt.subplots()

    # Handle common pandas-style kwargs
    title = kwargs.pop("title", None)
    grid = kwargs.pop("grid", False)

    y = kwargs.pop("y", None)
    x = kwargs.pop("x", None)

    if x is not None and y is not None:
        ax.plot(data[x], data[y], **kwargs)
    elif y is not None:
        ax.plot(data.index, data[y], **kwargs)
    else:
        ax.plot(data, **kwargs)

    if title:
        ax.set_title(title)
    if grid:
        ax.grid(True)

    return ax


def _enable_backend():
    try:
        # Only set if not already set to something else custom
        if pd.options.plotting.backend in (None, "matplotlib", ""):
            pd.options.plotting.backend = __name__
    except Exception:

        pass

_enable_backend()

