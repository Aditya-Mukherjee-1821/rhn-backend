from rhn_app.services.network_services.constants import *
from rhn_app.services.time.obtain_col import obtain_time_and_col
import pandapipes as pp
import pandas as pd
import os

def edit_sinks_from_df(net):
    col=obtain_time_and_col()+1-2
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sourcefile = os.path.join(BASE_DIR, "data", "Data.xlsx")
    df_sink=pd.read_excel(sourcefile,sheet_name=1)
    for i in range(len(net.heat_consumer)):
        net.heat_consumer.at[i,'qext_w']=float(str(df_sink.at[i,str(df_sink.columns[col])]))*1000
        #print(net.heat_consumer.at[i,'qext_w'])
    print(df_sink.columns[col])
