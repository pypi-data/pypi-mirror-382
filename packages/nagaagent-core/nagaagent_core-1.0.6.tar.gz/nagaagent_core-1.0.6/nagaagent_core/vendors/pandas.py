"""NagaAgent core proxy for pandas"""  #
import pandas as _pd  #
from pandas import *  # noqa #

__all__ = getattr(_pd, "__all__", [])  #

