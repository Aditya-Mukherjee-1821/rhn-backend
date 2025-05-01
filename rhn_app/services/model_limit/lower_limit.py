"""
    1. Create tree from excel data (graph with no loops)
    2. Each node of tree (unless its a sink) should hold the following data : 
        a.  Required temperate 
        b.  Max capacity from that node to leaves
        c.  Diameter and loss coefficient of pipe connecting to this node and its child nodes   
        d.  Energy requirement at child nodes
""" 
import pandas as pd
from rhn_app import pandapipes as pp
import numpy as np
import math
import os
from rhn_app.services.time.obtain_col import obtain_time_and_col

# Import data
def import_data(sourcefile):
    df_heater = pd.read_excel(sourcefile, sheet_name=0)
    df_sink = pd.read_excel(sourcefile, sheet_name=1)
    df_connection = pd.read_excel(sourcefile, sheet_name=2)
    df_nodetype = pd.read_excel(sourcefile, sheet_name=3)
    return df_heater,df_sink,df_connection,df_nodetype
# Prepare blank network for elements

#Creation of a tree structure from excel data.

def createTree(df_heater,df_sink,df_connection,df_nodetype):
    #roots of tree are the heaters except Ericsson
    global nodesQM
    starts=[]
    for i in range(len(df_heater)):
        if df_heater.at[i,'Name']!='Ericsson':
            starts.append(df_heater.at[i,'Name'])

    #Goes through the df_nodetypr to store all nodes in a dict which will have their corresponding parent & children
    nodes = {x: {'parent': '', 'children': {}} for x in df_nodetype['Name']}
    nodesQM={x:{'Q':0,'m':0} for x in df_nodetype['Name']}
    nodes['Sarfvik']['parent']='-1'
    nodes['Kirkkonummi']['parent']='-1'
    vis={x: {x:-1} for x in df_nodetype['Name']}
    vis['Sarfvik']=1
    vis['Kirkkonummi']=1

    #Here we add connections to a dictionary so as to create tree by assigning parents and children. 
        #If a connection has 'Ericsson' has one end then atleast one of 'Supply' or 'Return' should be 'True'
        #If its a connection between two nodes where none of them is 'Ericsson' then both 'Supply' and 'Return' should be 'True'.
    filtered_df_connection = df_connection[
        ((df_connection['Start Node'] == 'Ericsson') | (df_connection['End Node'] == 'Ericsson')) &
        ((df_connection['Has Supply Line'] == True) | (df_connection['Has Return Line'] == True))
        |
        (~df_connection['Start Node'].eq('Ericsson') & ~df_connection['End Node'].eq('Ericsson') &
        (df_connection['Has Supply Line'] == True) & (df_connection['Has Return Line'] == True))
    ]

    #This dictionary 'connections' has all the connections between all valid nodes. Valid connections are filtered above
        #Ericssion cases handled properly
    connections = filtered_df_connection[['Start Node', 'End Node', 'Name']].values.tolist()

    ## Note : It has been assumed that no node has more than one parent. 
        #Since heaters are roots of the tree, two or more heaters cannot be connected to a single node (junction)
    ## Note : It is also assumed that there is one connection (one return and one supply) between any two nodes(junction)
    bfs=[x for x in starts]
    level=[0 for x in starts]
    i=0
    count=0
    while i<len(bfs):
        j=0
        if bfs[i]=='Ericsson':
            count+=1
            i+=1
            continue
        while j<len(connections):
            connection=connections[j]
            if bfs[i]==connection[0]:
                if connection[1] not in bfs:#vis[connection[1]]==0:
                    # print(f"loop found {connection[0]}   {connection[1]}")
                    bfs.append(connection[1])
                    vis[connection[1]]=1
                    level.append(level[i]+1)
                    nodes[bfs[i]]['children'][connection[1]]=connection[2]
                    nodes[connection[1]]['parent']=bfs[i]
                    connections.pop(j)
                    continue
                else:
                    j+=1
            elif bfs[i]==connection[1]:
                if connection[0] not in bfs:#vis[connection[0]]==0:
                    # print(f"loop found {connection[1]}   {connection[0]}")
                    bfs.append(connection[0])
                    vis[connection[0]]=1
                    level.append(level[i]+1)
                    nodes[bfs[i]]['children'][connection[0]]=connection[2]
                    nodes[connection[0]]['parent']=bfs[i]
                    connections.pop(j)
                    continue
                else:
                    j+=1
            else:
                j+=1
        i+=1
    #print(count)
    #Visualizing the tree
    # curr_level=0
    # idx=0
    # for ele in bfs:
    #     if curr_level==level[idx]:
    #         print(ele,end=" ")
    #     else:
    #         curr_level=level[idx]
    #         print()
    #         print(ele,end=" ")
    #     idx+=1

    return nodes

def solveNode(nodes,name,parc,df_heater,df_sink,df_connection,df_nodetype,col):
    #print('solveNode:___')
    global nodesQM
    if len(nodes[name]['children'])==0:
        #leaf node
        #print(f'leaf: {name}')
        #print('\t',end="")
        FS=1
        m_all=FS*(df_sink.loc[name].iloc[5]+0.0001)#/(4.19*50)+0.001
        inp_temp=(df_sink.loc[name].iloc[col])/(4.19*m_all)+35.0
        #print(inp_temp,end=" ")
        #print(m_all)
        nodesQM[name]['Q']=(inp_temp+273)*4.190*m_all
        return [inp_temp,m_all]
    elif nodes[name]['parent']=='-1':
        #parent node
        maxT=0
        sumc=0
        T_arr=[]
        c_arr=[]
        for ele,val in nodes[name]['children'].items():
            [T,c]=solveNode(nodes,ele,df_connection.loc[val].iloc[8],df_heater,df_sink,df_connection,df_nodetype,col)
            if T>maxT:
                maxT=T
            T_arr.append(T)
            c_arr.append(c)
        for i in range(0,len(T_arr)):
            sumc+=c_arr[i]*(T_arr[i]+273)/(maxT+273.0)
        #print(f'root: {name}')
        #print('\t',end="")
        nodesQM[name]['Q']=(maxT+273)*4.19*sumc
        return [maxT,sumc]
    
    #normal junction
    maxT=0
    maxc=0
    sumc=0
    T_arr=[]
    c_arr=[]
    for ele,val in nodes[name]['children'].items():
        [T,c]=solveNode(nodes,ele,df_connection.loc[val].iloc[8],df_heater,df_sink,df_connection,df_nodetype,col)
        if T>maxT:
            maxT=T
            maxc=c
        T_arr.append(T)
        c_arr.append(c)
    for i in range(0,len(T_arr)):
        sumc+=c_arr[i]*(T_arr[i]+273)/(maxT+273.0)
    # if sumc>parc:
    #     maxQ=(maxT+273)*maxc
    #     multiplier=0
    #     for i in range(len(T_arr)):
    #         multiplier+=(T_arr[i]+273)*c_arr[i]/maxQ
    #     maxT=maxQ/(parc/multiplier)-273
    #     sumc=parc
    #print(f'junc: {name}')
    #print('\t',end="")
    #print(maxT,end=" ")
    #print(sumc)
    nodesQM[name]['Q']=(maxT+273)*4.19*maxc
    return [maxT,sumc]

#Creation of a refined tree where nodes will contain required data instead of junctionID only.

def createRefinedTree(df_heater,df_sink,df_connection,df_nodetype,nodes,col):
    #print('createRedinedTree:___')
    
    nodes_to_delete = []    
    for ele, data in nodes.items():  # Use list() to iterate safely
        #print(ele,end=" ")
        #print(data['children'])
        if ele == 'Ericsson':
            nodes_to_delete.append(ele)
    # Remove nodes after iteration
    for ele in nodes_to_delete:
        if ele in nodes and 'parent' in nodes[ele]:
            parent = nodes[ele]['parent']
            if parent in nodes:  # Check if parent exists before modifying
                del nodes[parent]['children'][ele]
        del nodes[ele]  # Delete the node itself
    
    for parent, data in nodes.items():
        if 'Ericsson' in data['children']:
            del data['children'][ele]
            break
    #delete nodes (not leaves) that have no child nodes
    prev_len=len(nodes)
    step=1
    while step<10:
        step+=1
        nodes_to_delete = []    
        for ele, data in nodes.items():  # Use list() to iterate safely
            #print(ele,end=" ")
            #print(data['children'])
            if len(data['children']) == 0 and ele not in df_sink.index:
                nodes_to_delete.append(ele)
        # Remove nodes after iteration
        for ele in nodes_to_delete:
            if ele in nodes and 'parent' in nodes[ele]:
                parent = nodes[ele]['parent']
                if parent in nodes:  # Check if parent exists before modifying
                    del nodes[parent]['children'][ele]
            del nodes[ele]  # Delete the node itself
        new_len=len(nodes)
        if(prev_len==new_len):
            break
        prev_len=new_len 
    # for ele,data in nodes.items():
    #     print(ele,end="\t\t")
    #     print(data)
    # T=0
    # c=0
    for ele,data in nodes.items():
        if ele=='Sarfvik':
            [T1,c1] = solveNode(nodes,ele,-1,df_heater,df_sink,df_connection,df_nodetype,col)
        elif ele=='Kirkkonummi':
            [T2,c2] = solveNode(nodes,ele,-1,df_heater,df_sink,df_connection,df_nodetype,col)

    #print(f'required temp and mdot: {T+5} and {c}')
    #
    return [nodes,T1,c1,T2,c2]

def calcMassFlowRate(nodes,T1,c1,T2,c2):
    global nodesQM
    #bfs traversal
    bfs=[]
    i=0
    for ele,data in nodes.items():
        if ele=='Sarfvik':
            bfs.append(ele)
            nodesQM[ele]['m']=c1
        if ele=='Kirkkonummi':
            bfs.append(ele)
            nodesQM[ele]['m']=c2
        i+=1
    i=0
    while i<len(bfs):
        for ele,data in nodes[bfs[i]]['children'].items():
            if ele not in bfs:
                bfs.append(ele)
                nodesQM[ele]['m']=nodesQM[ele]['Q']/(4.19*nodesQM[bfs[i]]['Q']/(4.19*nodesQM[bfs[i]]['m']))
        i+=1
    print(nodesQM)

def calcTime(nodes,df_connection,source):
    global nodesQM
    nodesTime={key:0 for key in nodesQM}
    bfs=[]
    i=0
    for ele,data in nodes.items():
        if ele==source:
            bfs.append(ele)
            nodesTime[ele]=0
        i+=1
    i=0
    while i<len(bfs):
        for ele,data in nodes[bfs[i]]['children'].items():
            if ele not in bfs:
                bfs.append(ele)
                nodesTime[ele]=nodesTime[bfs[i]]+(1/60.0)*df_connection.loc[data].iloc[2]*math.pi*0.25*df_connection.loc[data].iloc[4]*pow(10,-6)*1000/nodesQM[ele]['m']
        i+=1
    return nodesTime

def returnLowerLimit():
    # Get the absolute path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sourcefile = os.path.join(BASE_DIR, "data", "Data.xlsx")
    df_heater,df_sink,df_connection,df_nodetype=import_data(sourcefile)
    nodes = createTree(df_heater,df_sink,df_connection,df_nodetype)
    # print("\n\n\nNodes:\nName\t\tparent\t\tChildren\n")
    # for node in nodes:
    #     print(node,nodes[node]['parent'],nodes[node]['children'],sep="          ")
    #sets the name column as indices for O(1) lookup
    col=obtain_time_and_col()+1
    
    df_heater.set_index('Name',inplace=True)
    df_sink.set_index('Name',inplace=True)
    df_connection.set_index('Name',inplace=True)
    df_nodetype.set_index('Name',inplace=True)
    columns=list(df_sink.columns)
    print(f'Target col from lower limit {columns[col-3]}')

    [nodes,T1,c1,T2,c2]=createRefinedTree(df_heater,df_sink,df_connection,df_nodetype,nodes,col-3)
    print(f'{T1}  {c1}\n{T2}  {c2}')
    return min(T1,T2)
    # calcMassFlowRate(nodes,T1,c1,T2,c2)

    # nodesTime=calcTime(nodes,df_connection,'Sarfvik')
    # print(nodesTime)
    # maxTime=0
    # maxEle=''
    # for ele,data in nodesTime.items():
    #     if nodesQM[ele]['m']>0.001:
    #         maxEle=ele
    #         maxTime=max(maxTime,data)
    # print(ele,maxTime,sep="  ")

    # nodesTime=calcTime(nodes,df_connection,'Kirkkonummi')
    # print(nodesTime)
    # maxTime=0
    # maxEle=''
    # for ele,data in nodesTime.items():
    #     if nodesQM[ele]['m']>0.001:
    #         maxEle=ele
    #         maxTime=max(maxTime,data)
    # print(ele,maxTime,sep="  ")
    # for col in range(7,31):
        # createRefinedTree(df_heater,df_sink,df_connection,df_nodetype,nodes,col)

