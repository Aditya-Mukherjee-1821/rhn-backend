import json
import pandas as pd
import pandapipes as pp
import numpy as np
import pandapipes.plotting as plot
from rhn_app.services.network_services.create_junctions import create_junctions_from_df
from rhn_app.services.network_services.create_sources import create_sources_from_df
from rhn_app.services.network_services.create_sinks import create_sinks_from_df
from rhn_app.services.network_services.create_connections import create_connections_from_df
from rhn_app.services.network_services.constants import *

def calc_pipeflow_from_df(df_heater, df_sink, df_connection, df_nodetype):
    # define variables for optimization
    # function for lower limit
    s = 80.0
    e = upper_limit_temp
    iter = 0
    mid = 0
    
    t_net_flow_init_k_local = t_net_flow_init_k
    t_out_k_local = t_out_k

    print("Starting optimizer: ")
    # Optimizer
    while s <= e and iter < 30:
        g = {}
        iter += 1
        mid = (s + e) / 2.0
        t_net_flow_init_k_local=mid-5
        t_out_k_local=mid
        net = pp.create_empty_network(name="Data", fluid="water")

        # Run simulation
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
        pp.pipeflow(net, mode="hydraulics")

        total_mdot_kg_per_s_INST = net.res_circ_pump_pressure.at[0,'mdot_flow_kg_per_s']+net.res_circ_pump_pressure.at[1,'mdot_flow_kg_per_s']
        
        # Calculate relative error
        error = abs(total_mdot_kg_per_s_INST - total_mdot_kg_per_s)
        #rel_error = error / total_mdot_kg_per_s
        
        # Check convergence
        if error <= 1.0:  # 1% error tolerance
            print("\nConverged!")
            print(f"Optimal Temp: {mid:.2f}°C")
            print(f"Obtained mdot: {total_mdot_kg_per_s_INST:.4f} kg/s")
            print(f"Required mdot: {total_mdot_kg_per_s} kg/s")
            break
        
        # Adjust search range with adaptive step size
        step = max(0.1, error / 10)  # Minimum step of 0.1, dynamically adjusted
        
        if total_mdot_kg_per_s_INST > total_mdot_kg_per_s:
            s = mid + step
        else:
            e = mid - step
        
        # Early exit if oscillation detected
        if prev_mid is not None and abs(mid - prev_mid) < 0.05:
            print("\nOscillation detected, stopping early.")
            break
        prev_mid = mid
        
        # Logging
        print(f"Temp = {mid:.2f}°C")
        print(f"\tObtained mdot: {total_mdot_kg_per_s_INST:.4f} kg/s")
        print(f"\tRequired mdot: {total_mdot_kg_per_s} kg/s")

    # Extract relevant mass flow rate values



    # Convert to JSON string
    response = json.dumps({"message" : "converged"})

    return response
