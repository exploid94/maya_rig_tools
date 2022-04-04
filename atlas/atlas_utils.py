import os
import json
import pymel.core as pm
from maya import mel

mGear_folders = [
                 "mGear/guide_templates", 
                 "mGear/skin_weights", 
                 "mGear/anim_picker", 
                 "mGear/pre_scripts", 
                 "mGear/post_scripts",
                ]

atlas_folders = [
                 "atlas/guide_template", 
                 "atlas/model", 
                 "atlas/structure",
                 "atlas/control_cvs",
                 "atlas/skin_weights",
                 "atlas/deformer_weights",
                 "atlas/blendshapes",
                 "atlas/maya_scene"
                ]

nxt_folders = [
                 "nxt"
                ]

###############################################################################
#  project management
###############################################################################

def set_project(directory):

    maya_dir = directory
    if not os.path.exists(directory):
        os.makedirs(directory)

    mel.eval('setProject \"' + maya_dir + '\"')

    for file_rule in pm.workspace(query=True, fileRuleList=True):
        file_rule_dir = pm.workspace(fileRuleEntry=file_rule)
        maya_file_rule_dir = os.path.join(maya_dir, file_rule_dir)
        if not os.path.exists(maya_file_rule_dir):
            os.makedirs(maya_file_rule_dir)

###############################################################################
#  get file/folder versioning
###############################################################################

def get_current_folder_version(directory):

    sub_dir = [os.path.join(directory, o) for o in os.listdir(directory) if os.path.isdir(os.path.join(directory, o))]

    if sub_dir:
        sub_dir = max(sub_dir)
        return sub_dir
    else:
        return None

def get_next_folder_version(directory):
    
    current_version = get_current_folder_version(directory)

    if isinstance(current_version, list):
        current_version = current_version[-1]

    if current_version:
        folder_name = os.path.basename(current_version)

        if "version" in folder_name:
            current_version = int(folder_name.replace("version_", ""))
            next_version = current_version + 1
        
        elif folder_name == "latest":
            next_version = 1

        return  next_version
    
    else:
        return 1

def get_latest_folder(directory):

    sub_dir = os.path.exists(directory+"/latest")
    if sub_dir:
        return sub_dir
    else:
        return None

###############################################################################
#  manifest library management
###############################################################################

def filter_files(file_name, file_list):
    if file_list in file_name:
        return True 
    else:
        return False

def build_asset_directory(asset_directory):
    print ("\nBuilding Asset Directory at:", asset_directory)
    # build mgear dir in asset dir of the manifest
    for folder in mGear_folders:
        try:
            if not os.path.exists(asset_directory+"/"+folder):
                print (asset_directory+"/"+folder)
                os.makedirs(asset_directory+"/"+folder)
        except:
            raise

    # build atlas dir in asset dir of the manifest
    for folder in atlas_folders:
        try:
            if not os.path.exists(asset_directory+"/"+folder):
                print (asset_directory+"/"+folder)
                os.makedirs(asset_directory+"/"+folder)
        except:
            raise
    
    # build nxt dir in asset dir of the manifest
    for folder in nxt_folders:
        try:
            if not os.path.exists(asset_directory+"/"+folder):
                print (asset_directory+"/"+folder)
                os.makedirs(asset_directory+"/"+folder)
        except:
            raise
    
    print ("Asset Directory Built.")

###############################################################################
#  JSON data
###############################################################################

def save_json(directory, file_name, data):

    # saves a new file by iteration
    path = "%s/%s" %(directory, file_name)

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write the json file with the list of dictionaries
    if path:
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent=4)
            return outfile

def load_json(filepath):

    # Load the selected file
    if filepath:
        data = json.load(open(filepath, "r"))

    return data

def save_as_json(directory, data):

    # Get the path to save to and build the json data of the dictionaries as a list.
    path = pm.fileDialog2(dir=directory, fileFilter='*.json', fileMode=0, dialogStyle=2)[0]

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write the json file with the list of dictionaries
    if path:
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent=4)

def load_as_json(directory):
    # Get the file path to read 
    path = pm.fileDialog2(dir=directory, fileFilter='*.json', fileMode=1, dialogStyle=2)

    # Load the selected file
    if path:
        data = json.load(open(path[0], "r"))

    return data

###############################################################################
#  control curves - charles code
###############################################################################

def get_safe_name_for_curve(curve):
    return curve.rpartition(":")[-1]

def export_curve(curve, export_folder):

    curve = pm.PyNode(curve)
    shape = curve.getShape() if curve.type() == "transform" else curve
    if not (shape and shape.type() == "nurbsCurve"):
        raise ValueError("export_curve expects a nurbsCurve object to be passed in.")

    degree = shape.degree()

    result = {
        ## doing a list conversion here because in python3 map
        ## returns a generator, which is useless here, and you'll
        ## be using python3 soon enough
        "points": list(map(lambda x:list(x), shape.getCVs(space="world"))),
        "degree": degree,
        "overrideEnabled": shape.overrideEnabled.get(),
        "overrideColor": shape.overrideColor.get(),
        "overrideRGBColors": shape.overrideRGBColors.get(),
        "overrideColorRGB": shape.overrideColorRGB.get(),
    }

    if not shape.degree() == 1:
        result["knots"] = shape.getKnots()


    safe_name = get_safe_name_for_curve(curve)
    
    file_path = os.sep.join((export_folder, safe_name+".json"))

    save_json(export_folder, safe_name+".json", result)

    return result

def import_curve(curve, import_folder):

    safe_name = get_safe_name_for_curve(curve)

    file_path = os.sep.join((import_folder, safe_name+".json"))

    if not os.path.exists(file_path):
        om2.MGlobal.displayWarning("-- Control {} has no saved curve file.".format(curve))
    else:
        data = load_json(file_path)

        degree = data["degree"]
        points = data["points"]
        knot   = data["knots"] if degree > 1 else None

        if degree == 1:
            new_curve = pm.curve(d=degree, p=points)
        else:
            new_curve = pm.curve(d=degree, p=points, k=knot)

        ## you have to do this first to make sure
        ## the curve has the right number of pointss
        new_curve.getShape().worldSpace[0] >> curve.create
        new_curve.getShape().worldSpace[0] // curve.create
        pm.delete(new_curve)

        ## now reset the points in worldspace
        curve.setCVs(points, space="world")
        curve.updateCurve()

        ## set the overrides
        curve.overrideEnabled.set(data["overrideEnabled"])
        curve.overrideColor.set(data["overrideColor"])
        curve.overrideRGBColors.set(data["overrideRGBColors"])
        curve.overrideColorRGB.set(data["overrideColorRGB"])



###############################################################################
#  deformer weights
###############################################################################

def get_blendshape_weights(shape_name, deformer_name):
    shape = pm.PyNode(shape_name)
    deformer = pm.PyNode(deformer_name)

    dict = {}
    # this dictionary will differ from normal deformer weights
    # will look like {target_index:[weight_list]}
    num_targets = deformer.numWeights()
    for target_index in range(num_targets):
        weight_list = pm.getAttr(deformer.inputTarget[target_index].inputTargetGroup[0].targetWeights)
        dict.update({int(target_index):weight_list})
    
    base_weight_list = pm.getAttr(deformer.inputTarget[0].baseWeights)
    dict.update({"base_weights":base_weight_list})
    
    return dict

def set_blendshape_weights(shape_name, deformer_name, data):
    shape = pm.PyNode(shape_name)
    deformer = pm.PyNode(deformer_name)

    for target_index in data:
        if target_index == "base_weights":
            for x, vert_index in enumerate(data[target_index]):
                pm.setAttr(deformer.inputTarget[0].baseWeights[x], data[target_index][x])
        else:
            for x, vert_index in enumerate(data[target_index]):
                pm.setAttr(deformer.inputTarget[int(target_index)].inputTargetGroup[0].targetWeights[x], data[target_index][x])
            
def get_deformer_weights(shape_name, deformer_name):
    shape = pm.PyNode(shape_name)
    deformer = pm.PyNode(deformer_name)

    dict = {}
    # get the weights per vertex
    for index, value in enumerate(pm.percent(deformer, shape.vtx, q=True, v=True)):
        dict.update({int(index):float(value)})
    
    return dict

def set_deformer_weights(shape_name, deformer_name, data):
    shape = pm.PyNode(shape_name)
    deformer = pm.PyNode(deformer_name)

    for index in data:
        pm.percent(deformer, shape.vtx[int(index)], v=data[index])