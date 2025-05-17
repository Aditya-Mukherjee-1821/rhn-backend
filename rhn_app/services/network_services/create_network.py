import json
import os
import pandas as pd
import pandapipes as pp
import numpy as np
from rhn_app.services.network_services.create_junctions import create_junctions_from_df
from rhn_app.services.network_services.create_sources import create_sources_from_df
from rhn_app.services.network_services.create_sinks import create_sinks_from_df
from rhn_app.services.network_services.create_connections import create_connections_from_df
from rhn_app.services.network_services.constants import *
from rhn_app.services.network_services.edit_junctions import edit_junctions_from_df
from rhn_app.services.network_services.edit_sources import edit_sources_from_df
from rhn_app.services.model_limit.lower_limit import returnLowerLimit
# from rhn_app.services.network_services.read_data import read_data 

import os
import pandas as pd
import json

def read_data():
    print("Reading from Excel and saving as JSON with state field...")

    # Get the absolute path of the Excel file
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sourcefile = os.path.join(BASE_DIR, "data", "Data.xlsx")

    # Read all sheets into DataFrames
    df_heater = pd.read_excel(sourcefile, sheet_name=0)
    df_sink = pd.read_excel(sourcefile, sheet_name=1)
    df_connection = pd.read_excel(sourcefile, sheet_name=2)
    df_nodetype = pd.read_excel(sourcefile, sheet_name=3)

    # Add a new 'state' column with value 1 (meaning "in use")
    for df in [df_heater, df_sink, df_connection, df_nodetype]:
        df["state"] = 1

    # Convert to dicts for JSON saving
    data_dict = {
        "heater": df_heater.to_dict(orient="records"),
        "sink": df_sink.to_dict(orient="records"),
        "connection": df_connection.to_dict(orient="records"),
        "nodetype": df_nodetype.to_dict(orient="records")
    }

    # Save the JSON
    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','saved_networks')
    os.makedirs(save_dir, exist_ok=True)
    json_path = os.path.join(save_dir,"input_rhn.json")

    with open(json_path, "w") as f:
        json.dump(data_dict, f, indent=2)

    print("✅ Data with state saved to input_rhn.json")
    return df_heater, df_sink, df_connection, df_nodetype

def use_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # rhn_app/
    json_path = os.path.join(base_dir, '..', '..', 'saved_networks', "input_rhn.json")
    json_path = os.path.abspath(json_path)

    with open(json_path, "r") as f:
        data = json.load(f)

    df_heater = pd.DataFrame(data["heater"])
    df_sink = pd.DataFrame(data["sink"])
    df_connection = pd.DataFrame(data["connection"])
    df_nodetype = pd.DataFrame(data["nodetype"])

    return df_heater, df_sink, df_connection, df_nodetype

def create_network(net,state):
    t_net_flow_init_k_local = t_net_flow_init_k
    t_out_k_local = t_out_k

    if(state):    
        df_heater, df_sink, df_connection, df_nodetype = use_data()
    else:
        df_heater, df_sink, df_connection, df_nodetype = read_data()
    # Run simulation
    g={}
    # Create junctions
    print("Creating supply and return junctions...")
    create_junctions_from_df(df_heater, df_sink, df_connection, df_nodetype, net, g, t_net_flow_init_k_local, t_out_k_local)

    # Create sources
    print("Creating sources...")
    create_sources_from_df(df_heater, df_sink, df_connection, df_nodetype, net, g, t_net_flow_init_k_local, t_out_k_local)

    # Create sinks
    print("Creating sinks...")
    create_sinks_from_df(df_heater, df_sink, df_connection, df_nodetype, net, g, t_net_flow_init_k_local, t_out_k_local)

    # Create connections
    print("Creating connections...")
    create_connections_from_df(df_heater, df_sink, df_connection, df_nodetype, net, g, t_net_flow_init_k_local, t_out_k_local)

    # Run the pipeflow simulation
    print("Running pipeflow simulation...")
    pp.pipeflow(net, mode="sequential")
    
    junctions = {
        net.junction.at[_, 'name']: {
            "type": net.junction.at[_,"type"],
            "x": float(str(net.junction_geodata.at[_, 'x'])),
            "y": float(str(net.junction_geodata.at[_, 'y'])),
            "t": 0.0
        }
        for _, row in net.res_junction.iterrows()
    }

    # Get current file directory → rhn_app/services/network_services
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rhn_app_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
    save_dir = os.path.join(rhn_app_dir, 'saved_networks')
    os.makedirs(save_dir, exist_ok=True)

    # Final JSON file path
    json_path = os.path.join(save_dir, 'junctions.json')

    # Save to JSON
    with open(json_path, 'w') as f:
        json.dump(junctions, f, indent=4)

    print(f"✅ Saved junctions data to {json_path}")
    
    pipes = {
    net.pipe.at[_, 'name']: {
            "from": str(net.junction.at[int(net.pipe.at[_,"from_junction"]), 'name']),
            "to": str(net.junction.at[int(net.pipe.at[_,"to_junction"]), 'name']),
            "massflow": 0.0
        }
        for _, row in net.res_pipe.iterrows()
    }

    
    json_path = os.path.join(save_dir, 'pipes.json')

    # Save to JSON
    with open(json_path, 'w') as f:
        json.dump(pipes, f, indent=4)

    print(f"✅ Saved pipes data to {json_path}")