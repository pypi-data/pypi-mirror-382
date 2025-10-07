import pathlib
from .main import SaltySplits
from .enums import TimeType as TimeType
from functools import partial as _partial

DEMO_SPLITS = pathlib.Path(__file__).parents[2] / "tests/run_files/gcb.lss"
LOGO_PATH = pathlib.Path(__file__).parents[2] / "docs/assets/images/logo.png"

# forwarding read_lss to main module (+ docs)
read_lss = _partial(SaltySplits.read_lss)
read_lss.__doc__ = SaltySplits.read_lss.__doc__
