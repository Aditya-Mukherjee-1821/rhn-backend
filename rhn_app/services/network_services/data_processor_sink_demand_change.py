import os
import pandas as pd

def process_sink_demand_change(modifications):
    print("Applying modifications...")
    """Extracts data from Excel, modifies it based on API request."""
    # Get the absolute path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(BASE_DIR)
    sourcefile = os.path.join(BASE_DIR, "data", "Data.xlsx")

    # Read all sheets into separate dataframes
    df_heater = pd.read_excel(sourcefile, sheet_name=0)
    df_sink = pd.read_excel(sourcefile, sheet_name=1)
    df_connection = pd.read_excel(sourcefile, sheet_name=2)
    df_nodetype = pd.read_excel(sourcefile, sheet_name=3)
    
    # Apply modifications based on request
    if "name" in modifications and "demand_change" in modifications:
        name = modifications["name"]  # Get the name value from the request
        demand_change = float(modifications["demand_change"])  # Convert to float
        
        # Apply the change only to the row where "Name" matches the given value
        df_sink.loc[df_sink["Name"] == name, "Base Demand [kW]"] *= (1 + demand_change / 100)
        df_sink.loc[df_sink["Name"] == name, "Base Demand [kg/s]"] *= (1 + demand_change / 100)
        
        print(f"Base demand for '{name}' increased by {demand_change}%")
        
        return df_heater, df_sink, df_connection, df_nodetype
