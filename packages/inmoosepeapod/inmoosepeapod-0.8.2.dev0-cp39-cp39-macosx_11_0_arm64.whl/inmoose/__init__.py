import importlib.metadata

__version__ = "0.8.2-dev0" # importlib.metadata.version(__package__)

from . import edgepy as edgepy
from . import pycombat as pycombat
from . import utils as utils
from . import consensus_clustering as consensus_clustering
from . import deseq2 as deseq2
from . import diffexp as diffexp
from . import cohort_qc as cohort_qc
