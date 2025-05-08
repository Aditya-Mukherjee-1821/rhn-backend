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
from rhn_app.services.network_services.read_data import read_data 


def create_network(net):
    t_net_flow_init_k_local = t_net_flow_init_k
    t_out_k_local = t_out_k

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