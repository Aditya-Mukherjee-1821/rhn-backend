import os
import pandas as pd
import numpy as np
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA

def next_hour_prediction():  # Fixed typo in function name
    print("Applying modifications...")

    # Get the absolute path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sourcefile = os.path.join(BASE_DIR, "data", "Data.xlsx")

    # Read all sheets into separate dataframes
    df_heater = pd.read_excel(sourcefile, sheet_name=0)
    df_sink = pd.read_excel(sourcefile, sheet_name=1)
    df_connection = pd.read_excel(sourcefile, sheet_name=2)
    df_nodetype = pd.read_excel(sourcefile, sheet_name=3)

    return df_heater, df_sink, df_connection, df_nodetype
