#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SPIce is a modular-based Python package for performing shallow diving-wave 
analysis of node-type data from hammer seismics. 

SPIce was developed to study the firn and shallow ice structures in ice sheets 
and permafrost. Every step in the seismic refraction workflow is included, 
beginning with data handling and processing, first break picking of diving 
waves, travel-time curve fitting and seismic velocity analysis, and various 
plot operations. Data visualisation provides an interactive graphical platform 
for users if they wish to manually pick and export first breaks while viewing 
the detailed shape of waveforms.
"""

__version__ = "0.1.0"
__author__ = "Shyla Kupis"

# Import main classes for easy access
from .spice import spice
from .inversion import inversion
from .spicey_plotter import spicey_plotter
from .pykonal_plotter import pykonal_plotter

__all__ = [
    'spice',
    'inversion', 
    'spicey_plotter',
    'pykonal_plotter',
]