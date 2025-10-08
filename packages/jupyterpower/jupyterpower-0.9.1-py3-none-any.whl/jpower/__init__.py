from ._version import __version__
from .paths import ROOT, DATA_DIR, RESULTS_DIR
from .io import load_csv
from .utils import moving_average
from .model import fit_linear_time
from .viz import plot_series_with_smooth, save_fig

__all__ = [
    "__version__", "ROOT", "DATA_DIR", "RESULTS_DIR",
    "load_csv", "moving_average", "fit_linear_time",
    "plot_series_with_smooth", "save_fig",
]
