import pandapipes as pp
import pandas as pd
import os

def best_mass_flow(net):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sourcefile = os.path.join(BASE_DIR, "data", "Data.xlsx")
    df_sink=pd.read_excel(sourcefile,sheet_name=1)
    
    max_total_demand=0
    max_col=''
    for col in range(7,len(df_sink.columns)):
        total_demand=0
        for j in range(len(df_sink)):
            total_demand+=float(str(df_sink.at[j,col]))
        if total_demand>max_total_demand:
            max_col=df_sink.columns[col]
            max_total_demand=total_demand

    for j in range(len(net.heat_consumer)):
        net.heat_consumer.at[j,'qext_w']=float(str(df_sink.at[j,max_col]))*1000
    
    for i in range(len(net.circ_pump_pressure)):
        net.circ_pump_pressure.at[i,'t_flow_k']=373
    
    pp.pipeflow(net,mode='sequential')
    for i in range(0,2):
        for i in range(len(net.res_junction)):
            net.junction.at[i,'tfluid_k']=float(str(net.res_junction.at[i,'t_k']))
            net.junction.at[i,'pn_bar']=float(str(net.res_junction.at[i,'p_bar']))
        pp.pipeflow(net,mode='sequential')
    
    req_mass_flow=[]
    for i in range(len(net.res_circ_pump_pressure)):
        req_mass_flow.append(net.res_circ_pump_pressure.at[i,'mdot_flow_kg_per_s'])

    print(req_mass_flow)
    return req_mass_flow