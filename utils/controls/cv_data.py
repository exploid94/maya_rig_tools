import os
import pymel.core as pm
from rigging_utils import json_utils
reload(json_utils)

def get_cv_list(curve_name, world_space=True):
    """
    Stores the cv's translation values in a list

    curve_name : str
        
        Name of curve's transform to get a list of

    world_space : bool

        Get's the world space values of each cv. 
        default=True
    
    returns : list

        List of each cv's translation values
    """
    crv = pm.PyNode(curve_name)
    cv_list = []
    if crv.type() == "transform" and crv.getShape().type() == "nurbsCurve":
        obj_trans = pm.xform(crv, piv=True, ws=True, q=True)
        obj_trans = [obj_trans[0], obj_trans[1], obj_trans[2]]
        for cv in crv.cv:
            cv_index = cv.index()
            cv_trans = pm.xform(cv, worldSpace=world_space, translation=True, q=True)
            cv_trans = [cv_trans[0]-obj_trans[0], cv_trans[1]-obj_trans[1], cv_trans[2]-obj_trans[2]]
            cv_trans = [round(num, 3) for num in cv_trans]
            cv_list.append(cv_trans)
    return cv_list

def export_curve_to_cvx(curve_name, world_space=True, path=None):
    """
    Exports the given curve's cv list to a .cvx file based on the name of the object

    curve_name : str 
        
        Name of curve's transform to get a list of

    world_space : bool

        Get's the world space values of each cv. 
        default=True

    path : str

        Directory to save the file to, overwrites the default script path. 
        default=None
    
    returns : str

        File path of the .cvx file saved
    """
    cv_list = get_cv_list(curve_name, world_space=world_space)
    save_path = "%s/shapes" % (os.path.dirname(__file__))
    saved_file = json_utils.save_json(save_path, curve_name+".cvx", cv_list)

    return saved_file

def get_control_dict():
    """
    Returns a dictionary of all the .cvx files as keys and all their cv positions as the values. 
    """

    control_dict = {}

    shapes_path = "%s/shapes" %os.path.dirname(__file__)

    for shape_file in os.listdir(shapes_path):
        shape_name = os.path.splitext(shape_file)[0]
        shape_data = json_utils.load_json("%s/%s" % (shapes_path, shape_file))
        control_dict.update({shape_name:shape_data})
    
    return control_dict