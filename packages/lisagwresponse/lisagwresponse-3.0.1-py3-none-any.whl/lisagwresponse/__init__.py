"""LISA GW Response module."""

import importlib_metadata

from . import psd
from .response import (
    GalacticBinary,
    ReadResponse,
    ReadStrain,
    Response,
    ResponseFromStrain,
    VerificationBinary,
)
from .stochastic import StochasticBackground, StochasticPointSource

# Automatically set by `poetry dynamic-versioning`
__version__ = "3.0.1"


try:
    metadata = importlib_metadata.metadata("lisagwresponse").json
    __author__ = metadata["author"]
    __email__ = metadata["author_email"]
except importlib_metadata.PackageNotFoundError:
    pass
