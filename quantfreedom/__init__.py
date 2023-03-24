# Import version
import os
os.environ["NUMBA_CACHE_DIR"]="numba_cache"

from quantfreedom._version import __version__ as _version

__version__ = _version


# Most important classes
from quantfreedom.utils import *
from quantfreedom.data import *
from quantfreedom.backtester import *
from quantfreedom.backtester.base import *
from quantfreedom.backtester.enums import *
from quantfreedom.backtester.nb import *
from quantfreedom.backtester.indicators import *

# silence NumbaExperimentalFeatureWarning
import warnings
from numba.core.errors import NumbaExperimentalFeatureWarning

warnings.filterwarnings("ignore", category=NumbaExperimentalFeatureWarning)