import pymel.core as pm

def get_blendshape_target_names(blendshape_name):
    b = pm.PyNode(blendshape_name)
    target_names = []
    for x, i in enumerate(b.weight.get()):
        target_names.append(pm.listAttr(b.weight[x], sn=True)[0])
    
    return target_names

def get_blendshape_incoming_connections(blendshape_name):
    incoming_connections = {}

    b = pm.PyNode(blendshape_name)
    for x, i in enumerate(b.weight.get()):
        incoming_connections.update({blendshape_name+".weight[%s]" %str(x):pm.listConnections(b.weight[x], plugs=True, source=True, destination=False)[0]})
    

    return incoming_connections

def get_blendshape_outgoing_connections(blendshape_name):
    outgoing_connections = {}

    b = pm.PyNode(blendshape_name)
    for x, i in enumerate(b.weight.get()):
        outgoing_connections.update({blendshape_name+".weight[%s]" %str(x):pm.listConnections(b.weight[x], plugs=True, source=False, destination=True)})
    

    return outgoing_connections
