import pandas as pd
from rhn_app import pandapipes as pp
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