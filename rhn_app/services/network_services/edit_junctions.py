from rhn_app.services.network_services.constants import *
import pandapipes as pp

def edit_junctions_from_df(net, t_net_flow_init_k_local):
    ## Create pandapipes junctions from imported data.
    # Creates separate networks for supply and return lines. Supply and return
    # lines join at sinks and heat sources.

    # Get number of nodes from dataframe
    for i in range(len(net.junction)):
        if net.junction.at[i,'name'].endswith('supply'):
            net.junction.at[i,'tfluid_k']=t_net_flow_init_k_local
