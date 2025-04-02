import math
import json
from sortedcontainers import SortedDict,SortedList

def time_delay(net):
    print("Running time delay!")
    #Single source longest path algorithm
    #Adjacency list creation
    # Create a mapping from junction index to junction name
    junction_mapping = net.junction['name'].to_dict()
    connections = net.pipe[['from_junction', 'to_junction', 'name','length_km','diameter_m']].copy()
    connections['from_junction'] = connections['from_junction'].map(junction_mapping)
    connections['to_junction'] = connections['to_junction'].map(junction_mapping)
    connections = connections.values.tolist()
    connections = [row for row in connections if row[2].endswith("_return")]
    connections = [[row[0].replace("_return", ""), row[1].replace("_return", ""), row[2]] for row in connections]
    connections = [[row[0].replace("Sink", "Junction"), row[1].replace("Sink", "Junction"), row[2]] for row in connections]

    net_connections = {
        row['name']: {'idx': i, 'length_km': row['length_km'], 'diameter_m': row['diameter_m']}
        for i, (_, row) in enumerate(net.pipe.iterrows()) if row['name'].endswith("_return")
    }
    net_res_connections = [abs(row['mdot_from_kg_per_s']) for _, row in net.res_pipe.iterrows()]
    
    adj_list={}
    adj_list.update({x: {} for x in net.junction['name']})
    adj_list.update({x.replace('Sink','Junction'): {} for x in net.heat_consumer['name']})
    adj_list.update({x:{} for x in list(net.circ_pump_pressure['name'])})
    adj_list = {k.replace("_return", ""): v for k, v in adj_list.items()}
    adj_list = {k.replace("Sink", "Junction"): v for k, v in adj_list.items()}
    
    for i in range(len(connections)):
        start=connections[i][0]
        end=connections[i][1]
        if net_res_connections[net_connections[connections[i][2]]['idx']]<0.00001:
            continue
        weight=net_connections[connections[i][2]]['length_km']*1000*math.pi*0.25*math.pow(net_connections[connections[i][2]]['diameter_m'],2)/net_res_connections[net_connections[connections[i][2]]['idx']]
        adj_list[start][end]=weight*-1.0
        adj_list[end][start]=weight*-1.0
    
    #Dijkstra algorithm
    starts=[x for x in list(net.circ_pump_pressure['name']) if x!='Ericsson']
    vis={x:0 for x in list(net.circ_pump_pressure['name'])}
    vis.update({x:0 for x in net.junction['name']})
    vis.update({x.replace('Sink','Junction'):0 for x in net.heat_consumer['name']})
    vis={k.replace("_return", ""): v for k, v in vis.items()}
    vis = {k.replace("Sink", "Junction"): v for k, v in vis.items()}

    for ele in net.circ_pump_pressure['name']:
        vis[ele]=1
    
    i=0
    bfs=SortedList()
    r_bfs={}
    while i<len(starts):
        for j,w in adj_list[starts[i]].items():
            if j not in r_bfs:
                r_bfs[j]=w
            else:
                r_bfs[j]=min(r_bfs[j],w)
        bfs.add((w,j))
        i+=1
    
    maxTime=0
    count=0
    while len(bfs)!=0:
        count+=1
        (w,ele)=bfs.pop(0)
        maxTime=min(w,maxTime)
        if vis[ele]==1:
            continue
        vis[ele]=1
        for child,child_w in adj_list[ele].items():
            if vis[child]==1:
                continue
            r_bfs[child]=min(r_bfs.get(child, float('inf')),child_w+w)
            bfs.add((r_bfs[child],child))
    #print(abs(maxTime/60.0))

    response = json.dumps({'time' : maxTime})

    return response