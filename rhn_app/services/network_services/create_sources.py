from rhn_app.services.network_services.constants import *
import pandapipes as pp
import pandas as pd

def create_sources_from_df(df_heater, df_sink, df_connection, df_nodetype, net, g, t_net_flow_init_k_local, t_out_k_local):
    # Clean up column names
    df_connection['Start Node'] = df_connection['Start Node'].str.strip()
    df_connection['End Node'] = df_connection['End Node'].str.strip()

    # Get source connections and create source nodes
    for i in range(len(df_heater)):
        
        if str(df_heater.iloc[i,0]) != "Ericsson": # Ericsson special case below
            source_name = str(df_heater.iloc[i,0])
            # Define supply and return flow network sources
            source_row=df_nodetype.loc[df_nodetype['Name']==source_name]
            source_pos_flow=(source_row['X-Coordinate'].values[0],source_row['Y-Coordinate'].values[0])
            source_pos_return=(source_row['X-Coordinate'].values[0],source_row['Y-Coordinate'].values[0]-100)
            g['%s_supply' % source_name] = pp.create_junction(net,
                pn_bar=net_flow_p_bar,
                tfluid_k=t_net_flow_init_k_local+5,
                geodata=source_pos_flow,
                name=source_name + '_supply')
            g['%s_return' % source_name] = pp.create_junction(net,
                pn_bar=net_return_p_bar-1,
                tfluid_k=t_net_return_init_k,
                geodata=source_pos_return,
                name=source_name + '_return')
            
            source_flow=g[source_name+'_supply']
            source_return=g[source_name+'_return']
            
            pp.create_circ_pump_const_pressure(net,
                                                flow_junction=source_flow,
                                                return_junction=source_return,
                                                plift_bar=pressure_lift,
                                                p_flow_bar=source_flow_bar,
                                                mdot_flow_kg_per_s=pd.to_numeric(df_heater.iloc[i,2])/e_flow_conv_ratio,                
                                                t_flow_k=t_out_k_local,
                                                name=source_name)
            
            for j in range(len(df_connection)):
                
                if str(df_connection.at[j, 'Start Node']) == source_name:
                    
                    junction_flow = g[str(df_connection.at[j, 'End Node'])
                                            .replace("Junction-", "Junction_") + 
                                            '_supply']
                    
                    junction_return = g[str(df_connection.at[j, 'End Node'])
                                            .replace("Junction-", "Junction_") +
                                            '_return']
                    
                    pp.create_pipe_from_parameters(net,
                                                from_junction=source_flow,
                                                to_junction=junction_flow,
                                                length_km=float(str(df_connection.at[j, 'Length [m]']))/1000,
                                                diameter_m=float(str(df_connection.at[j, 'Diameter [mm]']))/1000,
                                                alpha_w_per_m2k=float(str(df_connection.at[j, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                                                text_k=int(temp_ext_k),
                                                name=str(df_connection.at[j,'Name'])+'_supply')

                    pp.create_pipe_from_parameters(net,
                                                from_junction=junction_return,
                                                to_junction=source_return,
                                                length_km=float(str(df_connection.at[j, 'Length [m]']))/1000,
                                                diameter_m=float(str(df_connection.at[j, 'Diameter [mm]']))/1000,
                                                alpha_w_per_m2k=float(str(df_connection.at[j, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                                                text_k=int(temp_ext_k),
                                                name=str(df_connection.at[j,'Name'])+'_supply')
            
                elif str(df_connection.at[j, 'End Node']) == source_name:

                    junction_flow = g[str(df_connection.at[j, 'Start Node'])
                                            .replace("Junction-", "Junction_") + 
                                            '_supply']
                    
                    junction_return = g[str(df_connection.at[j, 'Start Node'])
                                            .replace("Junction-", "Junction_") +
                                            '_return']
                    
                    pp.create_pipe_from_parameters(net,
                                                from_junction=source_flow,
                                                to_junction=junction_flow,
                                                length_km=float(str(df_connection.at[j, 'Length [m]']))/1000,
                                                diameter_m=float(str(df_connection.at[j, 'Diameter [mm]']))/1000,
                                                alpha_w_per_m2k=float(str(df_connection.at[j, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                                                text_k=int(temp_ext_k),
                                                name=str(df_connection.at[j,'Name'])+'_supply')

                    pp.create_pipe_from_parameters(net,
                                                from_junction=junction_return,
                                                to_junction=source_return,
                                                length_km=float(str(df_connection.at[j, 'Length [m]']))/1000,
                                                diameter_m=float(str(df_connection.at[j, 'Diameter [mm]']))/1000,
                                                alpha_w_per_m2k=float(str(df_connection.at[j, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                                                text_k=int(temp_ext_k),
                                                name=str(df_connection.at[j,'Name'])+'_supply')
            
    # Ericsson special case: Ericsson has only return connections;
    # Ericsson set as a slack node in the network.

    # Create auxiliary junction to connect to Ericsson
    Ericsson_row = df_nodetype.loc[df_nodetype['Name']=='Ericsson']
    Ericsson_geodata = (Ericsson_row.loc[:,'X-Coordinate'].values[0],Ericsson_row.loc[:,'Y-Coordinate'].values[0])
    g['Ericsson_connection'] = pp.create_junction(
                                        net, pn_bar=net_return_p_bar,
                                        tfluid_k=t_net_return_init_k,
                                        geodata=Ericsson_geodata,
                                        name='Ericsson_connection')

    # Tracker for Ericsson auxiliary junction connections
    e_pipe_tracker = 0

    for i in range(len(df_connection)):

        if str(df_connection.at[i, 'Start Node']) == 'Ericsson':
                    
            connection_name = g[str(df_connection.at[i, 'End Node'])
                                            .replace("Junction-", "Junction_") + 
                                            '_return']

            pp.create_pipe_from_parameters(net,
                from_junction=connection_name,
                to_junction=g['Ericsson_connection'],
                length_km=float(str(df_connection.at[i, 'Length [m]']))/1000,
                diameter_m=float(str(df_connection.at[i, 'Diameter [mm]']))/1000,
                alpha_w_per_m2k=float(str(df_connection.at[i, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                text_k=int(temp_ext_k),
                name='Pipe_E_' + str(e_pipe_tracker)
                )
            
            e_pipe_tracker += 1
            
        elif str(df_connection.at[i, 'End Node']) == 'Ericsson':

            connection_name = g[str(df_connection.at[i, 'Start Node'])
                                            .replace("Junction-", "Junction_") + 
                                            '_return']

            pp.create_pipe_from_parameters(net,
                from_junction=connection_name,
                to_junction=g['Ericsson_connection'],
                length_km=float(str(df_connection.at[i, 'Length [m]']))/1000,
                diameter_m=float(str(df_connection.at[i, 'Diameter [mm]']))/1000,
                k_mm=.05,
                alpha_w_per_m2k=float(str(df_connection.at[i, 'Heat Transfer Coefficient [W/mK]'])), # W/mK from raw data
                text_k=int(temp_ext_k),
                name='Pipe_E_' + str(i)
                )
            
            e_pipe_tracker += 1

    # Create Ericsson slack node

    Ericsson = pp.create_ext_grid(net,
                                junction=g['Ericsson_connection'],
                                p_bar=net_return_p_bar,
                                t_k=t_net_return_init_k,
                                name="Ericsson Ext. Grid")
