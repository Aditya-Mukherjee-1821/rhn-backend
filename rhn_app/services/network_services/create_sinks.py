from rhn_app.services.network_services.constants import *
import pandapipes as pp
import pandas as pd

def create_sinks_from_df(df_heater, df_sink, df_connection, df_nodetype, net, g, t_net_flow_init_k_local, t_out_k_local):
    # define col
    col = 10
    # demand in kW
    col_name=df_sink.columns[col]
    # Get number of sinks and connections
    num_sinks = len(df_sink)
    num_connections = len(df_connection)

    # Tracker tracks number of sinks created
    sink_tracker = 0

    # Iterate over number of raw data rows to find and create sinks
    for i in range(num_sinks):

        sink_get = str(df_sink.at[i, 'Name'])
        sink_name=sink_get.replace('Junction-','Sink_')
        # Get sink details
        sink_type = str(df_sink.at[i, 'Category'])
        sink_priority = int(float(str(df_sink.at[i, 'Priority'])))
        sink_demand_kW = float(str(df_sink.at[i, col_name]))
        mdot_kg_per_s_demand = float(str(df_sink.at[i, 'Base Demand [kg/s]']))
        sink_x = float(str(df_sink.at[i, 'X-Coordinate']))
        sink_y = float(str(df_sink.at[i, 'Y-Coordinate']))

        g[sink_get.replace('Junction-','Sink_')+'_supply']=pp.create_junction(net,
                                                                            pn_bar=net_flow_p_bar,
                                                                            tfluid_k=t_net_flow_init_k_local,
                                                                            geodata=(sink_x,sink_y),
                                                                            name=sink_get.replace('Junction-','Sink_') + '_supply')
        g[sink_get.replace('Junction-','Sink_')+'_return']=pp.create_junction(net,
                                                                            pn_bar=net_return_p_bar,
                                                                            tfluid_k=t_net_return_init_k,
                                                                            geodata=(sink_x,sink_y-100),
                                                                            name=sink_get.replace('Junction-','Sink_') + '_return')
        # Define sink
        pp.create_heat_consumer(net,
                                from_junction=g[sink_get.replace('Junction-','Sink_')+'_supply'],
                                to_junction=g[sink_get.replace('Junction-','Sink_')+'_return'],
                                diameter_m=43.1/1000,
                                qext_w=sink_demand_kW*1000,
                                # controlled_mdot_kg_per_s=mdot_kg_per_s_capacity,
                                #controlled_mdot_kg_per_s=mdot_kg_per_s_demand,
                                # deltat_k=50,
                                treturn_k=t_return_k,
                                name=sink_name, type=sink_type
                                )
        
        sink_flow = g[sink_get.replace('Junction-','Sink_')+'_supply']
        sink_return = g[sink_get.replace('Junction-','Sink_')+'_return']
        # Get connecting junction and pipe diameter
        for k in range(num_connections):
            if df_connection.at[k, "End Node"] == sink_get:
                junction_source = g[str(df_connection.at[k, 'Start Node']).
                                        replace("Junction-", "Junction_") + '_supply']
                junction_return = g[str(df_connection.at[k, 'Start Node']).
                                        replace("Junction-", "Junction_") + '_return']
                connection_d_mm = float(str(df_connection.at[k, 'Diameter [mm]']))
                mdot_kg_per_s_capacity = float(str(df_connection.at[k, 'Capacity [kg/s]']))
                
                pp.create_pipe_from_parameters(net,
                    from_junction=junction_source,
                    to_junction=sink_flow,
                    length_km=float(str(df_connection.at[k, 'Length [m]']))/1000,
                    diameter_m=float(str(df_connection.at[k, 'Diameter [mm]']))/1000,
                    alpha_w_per_m2k=float(str(df_connection.at[k, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                    text_k=int(temp_ext_k),
                    name=str(df_connection.at[k,'Name']+'_supply')
                    )
                pp.create_pipe_from_parameters(net,
                    from_junction=sink_return,
                    to_junction=junction_return,
                    length_km=float(str(df_connection.at[k, 'Length [m]']))/1000,
                    diameter_m=float(str(df_connection.at[k, 'Diameter [mm]']))/1000,
                    alpha_w_per_m2k=float(str(df_connection.at[k, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                    text_k=int(temp_ext_k),
                    name=str(df_connection.at[k,'Name']+'_return')
                    ) 

            elif df_connection.at[k, "Start Node"] == sink_get:
                junction_source = g[str(df_connection.at[k, 'End Node']).
                                        replace("Junction-", "Junction_") + '_supply']
                junction_return = g[str(df_connection.at[k, 'End Node']).
                                        replace("Junction-", "Junction_") + '_return']
                connection_d_mm = float(str(df_connection.at[k, 'Diameter [mm]']))
                mdot_kg_per_s_capacity = float(str(df_connection.at[k, 'Capacity [kg/s]']))
                pp.create_pipe_from_parameters(net,
                    from_junction=junction_source,
                    to_junction=sink_flow,
                    length_km=float(str(df_connection.at[k, 'Length [m]']))/1000,
                    diameter_m=float(str(df_connection.at[k, 'Diameter [mm]']))/1000,
                    alpha_w_per_m2k=float(str(df_connection.at[k, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                    text_k=int(temp_ext_k),
                    name=str(df_connection.at[k,'Name']+'_supply')
                    )
                pp.create_pipe_from_parameters(net,
                    from_junction=sink_return,
                    to_junction=junction_return,
                    length_km=float(str(df_connection.at[k, 'Length [m]']))/1000,
                    diameter_m=float(str(df_connection.at[k, 'Diameter [mm]']))/1000,
                    alpha_w_per_m2k=float(str(df_connection.at[k, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                    text_k=int(temp_ext_k),
                    name=str(df_connection.at[k,'Name']+'_return')
                    )  
            
        sink_tracker += 1
