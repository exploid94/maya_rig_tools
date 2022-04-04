import pymel.core as pm
from rigging_utils import json_utils

DEFAULT_TRANSFORMS = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
ROTATE_ORDERS = ["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"]


def set_keyable(node, attributes=DEFAULT_TRANSFORMS, keyable=True):
    """
    Sets the given attributes to be keyable and unlocked or not keyable and locked.

    node : dagNode 
        
        The node with the attributes to set.

    attributes : list of str 

        The list of the attributes to set. 
        default=["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
    
    keyable : bool

        Tells the attributes to be keyable or not. 
        default=True
    """
    if not isinstance(attributes, list):
        attributes = [attributes]

    for attr_name in attributes:
        node.setAttr(attr_name, lock=1-keyable, keyable=keyable)


def set_rotate_order(node, order="XYZ"):
    """
    Sets the rotate order on the given node.

    node : dagNode 
        
        The node to set the rotate order on.

    order : str 

        The rotate order to set. Accepted orders are "XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"
        default="XYZ"
    """

    # automatically adapt the angle values 
    rot = pm.datatypes.EulerRotation([pm.getAttr(node + ".rx"), pm.getAttr(node + ".ry"), pm.getAttr(node + ".rz")], unit="degrees")
    rot.reorderIt(order)

    pm.setAttr(node.ro, ROTATE_ORDERS.index(order), force=True)
    pm.setAttr(node.rx, rot.x, force=True)
    pm.setAttr(node.ry, rot.y, force=True)
    pm.setAttr(node.rz, rot.z, force=True)


def set_to_default(node, attributes=DEFAULT_TRANSFORMS):
    """
    Sets the given attributes on the given node to their defualt values.

    node : dagNode
        
        The node to set the rotate order on.

    attributes : list of str 

        The attributes to set to their default values
    """
    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)

    for attr in attributes:
        if pm.objExists(node.attr):
            default_value = get_default_value(node, attr)
            try:
                node.setAttr(attr, default_value)
            except RuntimeError:
                pass


def get_default_value(node, attribute):
    """
    Gets the default value of the given attribute.

    node : dagNode 
        
        The node to get the default value of the attribute on.

    attribute : str

        The attribute to get the default values
    """
    
    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)

    return pm.attributeQuery(attribute, node=node, listDefault=True)[0]


def set_default_value(node, attribute, value):
    """
    Sets the default value of the given attribute.

    node : dagNode 
        
        The node to set the default value of the attribute on.

    attribute : str

        The attribute to set the default value of
    """
    
    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)

    try:
        pm.addAttr(node+"."+attribute, dv=value, e=True)
    except:
        print ("Skipping attribute %s because it's not dynamic." %node.attribute)


def set_to_default_value(node, attribute):
    """
    Sets to the default value of the given attribute.

    node : dagNode 
        
        The node to set the default value of the attribute on.

    attribute : str

        The attribute to set the default value of
    """

    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)
    
    pm.setAttr(node+"."+attribute, get_default_value(node, attribute))


def set_to_dict(node, dictionary):
    """
    Sets the values of all attributes in the dictionary to the dictionary's values.
    The dictionary should read = {"attribute_name":value}

    node : dagNode 
        
        The node to set the values on.

    dictionary : dict

        The given dictionary that contains the attributes as keys and the values as values.
    """

    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)

    for attr in dictionary:
        try:
            pm.setAttr(node+"."+attribute, dictionary[attr])
        except:
            raise



# TODO add a proxy add attr from source to targets

####################################################
# I/O
####################################################


def save_config(node, userDefined=True, keyable=True, locked=False):
    """
    Saves a config file of the given node. The config file contains all attributes states and values. This includes keyable and locked.
    The config file will be saved at a specified folder and named the name of the node given.
    The contents of the config file will be that of : [value_dict, locked_dict, keyable_dict].
    locked_dict and keyable_dict values are only True or False. 

    node : dagNode

        The node to save the config file of.
    
    userDefined : bool

        Save user-defined attributes
    
    keyable : bool

        Save keyable attributes only
    
    locked : bool

        Save locked attributes only
    """

    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)
    
    value_dict = {}
    locked_dict = {}
    keyable_dict = {}

    for attr in pm.listAttr(node, ud=userDefined, keyable=keyable, locked=locked, sa=True):
        try:
            value_dict.update({attr:pm.getAttr(node+"."+attr)})
        except:
            pass

        if attr in pm.listAttr(node, locked=True):
            locked_dict.update({attr:True})
        else:
            locked_dict.update({attr:False})
        
        if attr in pm.listAttr(node, keyable=True):
            keyable_dict.update({attr:True})
        else:
            keyable_dict.update({attr:False})
    
    main_dict = [value_dict, locked_dict, keyable_dict]

    # get the save location for the folder
    dir = pm.fileDialog2(cap="Folder Save Location For Config File", fm=3, ff="*.config")[0]

    # save using json file
    json_utils.save_json(dir, node.name()+"_attributes.config", main_dict)


def load_config(directory, node):
    """
    Loads a config file of the given node. The config file contains all attributes states and values. This includes keyable and locked.
    The config file will be loaded as a list of contents : [value_dict, locked_dict, keyable_dict]

    node : dagNode

        The node to load the config file of.
    
    return : list

        Returns a list of the given dictionaries [value_dict, locked_dict, keyable_dict]
    """

    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)

    data = json_utils.load_json(directory+"\\"+node.name()+"_attributes.config")

    return data
