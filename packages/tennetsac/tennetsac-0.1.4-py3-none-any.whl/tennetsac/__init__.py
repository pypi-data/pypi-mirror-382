"""
TeNNet-SAC
==========

TeNNet-SAC (Thermodynamics-Embedded Neural Network for Segment Activity Coefficients)
is a machine learning framework for predicting molecular activity coefficients.

Quick Example
-------------
>>> from tennetsac import profile, binary_lng, multi_lng
>>> profile("CCO")
([0.0, 0.0, ...], 89.52, 70.53)    # σ-profile, area, volume

>>> binary_lng(["CCO", "ClCCCl"], 298.15, [0.0, 0.25, 0.5, 0.75, 1.0])
([1.582, 0.933, ...], [0.0, 0.104, ...])    # ln γ_1, ln γ_2

>>> multi_lng(["CCO", "ClCCCl", "CCN"], 298.15, [0.3, 0.4])
[0.310, 0.381, -0.238]    # ln γ_1, ln γ_2, ln γ_3
"""

from .core import profile, binary_lng, multi_lng