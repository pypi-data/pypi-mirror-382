import os
import sys
import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .weompy import *

packageDirectory = os.path.dirname(__file__)
sys.path.append(packageDirectory)

sys.modules[__name__] = importlib.import_module(f"weompy.weompy", package=__name__)

