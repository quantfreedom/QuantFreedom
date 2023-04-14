# Import version
import os
os.environ["NUMBA_CACHE_DIR"]="numba_cache"

from quantfreedom._version import __version__ as _version

__version__ = _version


# Most important classes
from quantfreedom import *
from quantfreedom.levon_qf import *
from quantfreedom.utils import *
from quantfreedom.data import *
from quantfreedom.base import *
from quantfreedom.enums import *
from quantfreedom.nb import *
from quantfreedom.indicators import *
from quantfreedom.evaluators import *
from quantfreedom.plotting import *

# silence NumbaExperimentalFeatureWarning
import warnings
from numba.core.errors import NumbaExperimentalFeatureWarning

warnings.filterwarnings("ignore", category=NumbaExperimentalFeatureWarning)