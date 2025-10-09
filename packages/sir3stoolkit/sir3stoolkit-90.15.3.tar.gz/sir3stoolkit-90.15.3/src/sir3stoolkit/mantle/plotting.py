# -*- coding: utf-8 -*-
"""
Created on Thu Okt 7 13:39:13 2025

@author: Jablonski

"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Union, Tuple, Literal, Dict, Any

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, base
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize, LogNorm, ListedColormap
from matplotlib.cm import get_cmap


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

from sir3stoolkit.core.wrapper import SIR3S_Model

class Plotting_SIR3S_Model(SIR3S_Model):

    pass