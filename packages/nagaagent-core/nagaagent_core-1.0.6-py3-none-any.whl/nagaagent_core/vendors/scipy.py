"""NagaAgent core proxy for scipy"""  #
import scipy as _scipy  #
from scipy import *  # noqa #

__all__ = getattr(_scipy, "__all__", [])  #

