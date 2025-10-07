#!/usr/bin/env python3
"""
Test script for import errors.
"""

# Missing modules
import pandas as pd
import requests
import matplotlib.pyplot as plt
import sklearn

# Wrong import names
import nunpy as np  # Should be numpy
import pandsa as pd  # Should be pandas
import requets  # Should be requests

print("All imports successful!")
