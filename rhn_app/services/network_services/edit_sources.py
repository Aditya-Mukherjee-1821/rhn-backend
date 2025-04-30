from rhn_app.services.network_services.constants import *
import pandapipes as pp
import pandas as pd

def edit_sources_from_df(net,t_out_k_local):
    # Clean up column names
    for i in range(len(net.circ_pump_pressure)):
        net.circ_pump_pressure.at[i,'t_flow_k'] = t_out_k_local
