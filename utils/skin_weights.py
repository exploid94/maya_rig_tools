import pymel.core as pm
from rigging_utils import json_utils
import os 


def get_influences(skin):

    skin_influence_dict = {}

    skin = pm.PyNode(skin)

    # this will list the influences in order
    influence_list = skin.getInfluence()

    for index, inf in enumerate(influence_list):
        skin_influence_dict.update({inf.name():index})
    
    return skin_influence_dict

def get_weights(skin, shape):

    skin_weight_dict = {}

    skin = pm.PyNode(skin)

    # this will spit out each vert's weight list in order
    for index, weight_list in enumerate(skin.getWeights(shape)):
        skin_weight_dict.update({index:weight_list})
    
    return skin_weight_dict

def set_weights(skin, shape):
    pass

def set_influences(skin):
    pass