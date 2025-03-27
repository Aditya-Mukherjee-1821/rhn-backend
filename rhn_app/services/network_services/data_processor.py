import os
import pandas as pd

def extract_and_modify_data(modifications):
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
    if "demand_change" in modifications:
        demand_change = float(modifications["demand_change"])  # Convert to float
        df_sink["Base Demand [kW]"] *= (1 + demand_change / 100)
        df_sink["Base Demand [kg/s]"] *= (1 + demand_change / 100)
        print("Base demand increased by", demand_change, "%")
    
    # Remove Pipe Connections
    if "remove_pipes" in modifications:
        pipe_names = modifications["remove_pipes"]  # List of pipe names
        for pipe in pipe_names:
            if pipe in df_connection["Name"].values:
                df_connection.loc[df_connection["Name"] == pipe, ["Has Supply Line", "Has Return Line"]] = False
                print(f"Pipe {pipe} removed successfully.")
            else:
                print(f"Warning: Pipe {pipe} not found in df_connection.")
    
    return df_heater, df_sink, df_connection, df_nodetype
