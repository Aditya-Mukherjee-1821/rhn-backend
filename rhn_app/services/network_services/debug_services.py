# while debugging remove any parameters from extract_and_modify_data
from calc_pipeflow import calc_pipeflow_from_df
from data_processor_next_hour import next_hour_prediction

df_heater, df_sink, df_connection, df_nodetype = next_hour_prediction()
calc_pipeflow_from_df(df_heater, df_sink, df_connection, df_nodetype)