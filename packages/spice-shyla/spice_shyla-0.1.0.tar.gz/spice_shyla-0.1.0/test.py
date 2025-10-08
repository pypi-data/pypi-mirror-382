#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 14:59:59 2025

@author: shylakupis
"""

from spice import spice, inversion, spicey_plotter
import pandas as pd

# Test instantiation
processor = spice()
hwi = inversion()
plotter = spicey_plotter()

print("All classes instantiated successfully!")

# Test a simple method
test_df = pd.DataFrame({'x': [0, 10, 20, 30], 't': [0, 5, 9, 12]})
result = hwi.DivingWaveAnalysis(test_df, Vice=3.8, plot_results=False)
print(f"Inversion test returned {len(result)} rows")