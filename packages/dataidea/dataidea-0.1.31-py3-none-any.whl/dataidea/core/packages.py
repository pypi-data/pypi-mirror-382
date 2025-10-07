"""
Convenient imports of commonly used packages
"""
from pathlib import Path
import scipy as sp
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dotenv import load_dotenv

# Load environment variables if .env file exists
load_dotenv()

__all__ = ['sp', 'np', 'pd', 'px', 'go', 'requests'] 