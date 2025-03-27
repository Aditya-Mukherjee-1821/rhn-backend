from rhn_app.services.network_services.constants import *
import pandapipes as pp

def create_junctions_from_df(df_heater, df_sink, df_connection, df_nodetype, net, g, t_net_flow_init_k_local, t_out_k_local):
    ## Create pandapipes junctions from imported data.
    # Creates separate networks for supply and return lines. Supply and return
    # lines join at sinks and heat sources.

    # Get number of nodes from dataframe
    num_nodes = len(df_nodetype)

    # tracker tracks number of junctions created
    junction_tracker = 0

    # Iterate over all nodes to find and create junctions
    for i in range(num_nodes):

        if df_nodetype.at[i, 'Node Type'] == "Junction":
            
            # Replace dashes with underscores to conform with Python markup
            junction_name = str(df_nodetype.at[i, 'Name']).replace("Junction-",
                                                                "Junction_")
            
            junction_pos_x = float(df_nodetype.at[i, 'X-Coordinate'])
            junction_pos_y = float(df_nodetype.at[i, 'Y-Coordinate'])
            junction_pos_flow = (junction_pos_x, junction_pos_y)
            junction_pos_return = (junction_pos_x, junction_pos_y-100)

            # Define supply and return flow network junctions
            g['%s_supply' % junction_name] = pp.create_junction(net,
                pn_bar=net_flow_p_bar,
                tfluid_k=t_net_flow_init_k_local,
                geodata=junction_pos_flow,
                name=junction_name + '_supply')
            g['%s_return' % junction_name] = pp.create_junction(net,
                pn_bar=net_return_p_bar,
                tfluid_k=t_net_return_init_k,
                geodata=junction_pos_return,
                name=junction_name + '_return')

            junction_tracker += 2
