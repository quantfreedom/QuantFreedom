# Import version
import os
os.environ["NUMBA_CACHE_DIR"]="numba_cache"

from old_quantfreedom._version import __version__ as _version

__version__ = _version


# Most important classes
from old_quantfreedom import *
from old_quantfreedom.utils import *
from old_quantfreedom.data import *
from old_quantfreedom.base import *
from old_quantfreedom.enums import *
from old_quantfreedom.nb import *
from old_quantfreedom.indicators import *
from old_quantfreedom.evaluators import *
from old_quantfreedom.plotting import *
from old_quantfreedom.poly import *

# silence NumbaExperimentalFeatureWarning
import warnings
from numba.core.errors import NumbaExperimentalFeatureWarning

warnings.filterwarnings("ignore", category=NumbaExperimentalFeatureWarning)