import pymel.core as pm
from rigging_utils import json_utils
reload(json_utils)
import os 


def get(shape_name, deformer_name):
    shape = pm.PyNode(shape_name)
    deformer = pm.PyNode(deformer_name)

    dict = {}
    # get the weights per vertex
    for index, value in enumerate(pm.percent(deformer, shape.vtx, q=True, v=True)):
        dict.update({int(index):float(value)})
    
    return dict

def set(shape_name, deformer_name, data):
    shape = pm.PyNode(shape_name)
    deformer = pm.PyNode(deformer_name)

    for index in data:
        pm.percent(deformer, shape.vtx[int(index)], v=data[index])

def save(shape_name, deformer_name, directory, file_name):
    data = get(shape_name, deformer_name)
    json_utils.save_json(directory, file_name, data)

def load(shape_name, deformer_name, file_path):
    data = json_utils.load_json(file_path)
    set(shape_name, deformer_name, data)

def save_as(shape_name, deformer_name):
    data = get(shape_name, deformer_name)
    json_utils.save_as_json(data)

def load_as(shape_name, deformer_name):
    data = json_utils.load_as_json()
    set(shape_name, deformer_name, data)
