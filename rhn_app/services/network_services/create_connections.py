from rhn_app.services.network_services.constants import *
import pandapipes as pp
import pandas as pd

def create_connections_from_df(df_heater, df_sink, df_connection, df_nodetype, net, g, t_net_flow_init_k_local, t_out_k_local):
    # Tracker tracks number of pipes created
    pipe_tracker = 0

    # Concatenate source and sink names to single NumPy array
    np_heaters_sinks = pd.concat([df_heater[['Name']], df_sink[['Name']]]).to_numpy()
    num_heaters_sinks = len(np_heaters_sinks)
    num_connections = len(df_connection)
    for i in range(num_connections):
        
        pipe_get = str(df_connection.at[i, 'Name']).replace("-", "_")

        start_node = str(df_connection.at[i, 'Start Node'])
        end_node = str(df_connection.at[i, 'End Node'])

        if str(df_connection.at[i, 'Has Supply Line']) == 'True': supply_line = True
        else: supply_line = False
        if str(df_connection.at[i, 'Has Return Line']) == 'True': return_line = True
        else: return_line = False
    
        # Exclude source and sink node connections (defined earlier)
        if start_node not in np_heaters_sinks and end_node not in np_heaters_sinks:
                
            # Create supply line pipe
            if supply_line == True:
                
                pipe_from = g[str(df_connection.at[i, 'Start Node']).
                                    replace("Junction-", "Junction_") + '_supply']
                pipe_to = g[str(df_connection.at[i, 'End Node']).
                                    replace("Junction-", "Junction_") + '_supply']
                pipe_name = pipe_get + '_supply'

                pp.create_pipe_from_parameters(net,
                    from_junction=pipe_from,
                    to_junction=pipe_to,
                    length_km=float(str(df_connection.at[i, 'Length [m]']))/1000,
                    diameter_m=float(str(df_connection.at[i, 'Diameter [mm]']))/1000,
                    k_mm=.05,
                    alpha_w_per_m2k=float(str(df_connection.at[i, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                    sections=5,
                    text_k=int(temp_ext_k),
                    name=pipe_name
                    )
                pipe_tracker += 1
            
            # Create return line pipe
            if return_line == True:

                pipe_from = g[str(df_connection.at[i, 'End Node']).
                    replace("Junction-", "Junction_") + '_return']
                pipe_to = g[str(df_connection.at[i, 'Start Node']).
                    replace("Junction-", "Junction_") + '_return']
                pipe_name = pipe_get + '_return'

                pp.create_pipe_from_parameters(net,
                    from_junction=pipe_from,
                    to_junction=pipe_to,
                    length_km=float(str(df_connection.at[i, 'Length [m]']))/1000,
                    diameter_m=float(str(df_connection.at[i, 'Diameter [mm]']))/1000,
                    alpha_w_per_m2k=float(str(df_connection.at[i, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                    text_k=int(temp_ext_k),
                    name=pipe_name,
                    sections=5,
                    k_mm=.05
                    )
                pipe_tracker += 1