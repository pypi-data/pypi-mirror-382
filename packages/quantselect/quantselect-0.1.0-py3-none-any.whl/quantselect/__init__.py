"""QuantSelect - An open-source Python package of the AlphaPept ecosystem"""

__version__ = "0.1.0"

# Keep the warning filters
import warnings

warnings.filterwarnings(
    "ignore", message="Numba extension module.*rocket_fft.*failed to load.*"
)
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="Mean of empty slice"
)
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="Degrees of freedom <= 0 for slice"
)
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="A worker stopped while some jobs were given to the executor.*",
    module="joblib.externals.loky.process_executor",
)
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="All-NaN slice encountered"
)
