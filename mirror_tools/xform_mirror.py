import pymel.core as pm
import re

def mirror(transforms_dict):
    """ 
    Performs the mirror on the given dictionary
    """       
    for transform in transforms_dict:  
        pm.xform(transform, ws=True, m=transforms_dict[transform])

def get_mirror_transform(objects=[], axis='yz', behaviour=True, opposite=False):
    """ 
    Mirrors transform axis hyperplane. 
    
    objects : list
        
        list of Transform or string.

    axis : str
        
        plane which to mirror axis.
        default="yz"

    behaviour : bool 

        mirrors the behaviour just like joint mirror does. rotations with mirror, translates won't
    
    opposite : bool

        mirrors the opposite transform of the selected object by replacing "_L" with "_R" or vice versa
        default=False

    retruns : dict
    """  
    
    transforms_dict = {}


    # No specified transforms, so will get selection
    if not transforms:
        transforms = pm.selected(type='transform')
        
    # Check to see all provided objects is an instance of pymel transform node,
    elif not all(map(lambda x: isinstance(x, pm.nt.Transform), transforms)):
        raise ValueError("Passed node which wasn't of type: Transform")
    
    # Validate plane which to mirror axis,
    if not axis in ('xy', 'yz', 'xz'): 
        raise ValueError("Keyword Argument: 'axis' not of accepted value ('xy', 'yz', 'xz').")        
    
    for transform in transforms:
    
        # Get the worldspace matrix, as a list of 16 float values
        mtx = pm.xform(transform, q=True, ws=True, m=True)
    
        # Invert rotation columns,
        rx = [n * -1 for n in mtx[0:9:4]]
        ry = [n * -1 for n in mtx[1:10:4]]
        rz = [n * -1 for n in mtx[2:11:4]]
        
        # Invert translation row,
        t = [n * -1 for n in mtx[12:15]]
        
        # Set matrix based on given plane, and whether to include behaviour or not.
        if axis == 'xy':
            mtx[14] = t[2]    # set inverse of the Z translation
            
            # Set inverse of all rotation columns but for the one we've set translate to.
            if behaviour:
                mtx[0:9:4] = rx
                mtx[1:10:4] = ry
                
        elif axis == 'yz':
            mtx[12] = t[0]    # set inverse of the X translation
            
            if behaviour:
                mtx[1:10:4] = ry
                mtx[2:11:4] = rz
        elif axis == 'xz':
            mtx[13] = t[1]    # set inverse of the Y translation
            
            if behaviour:
                mtx[0:9:4] = rx
                mtx[2:11:4] = rz
        
        if opposite:
            if "_L" in str(transform):
                transform = re.sub("_L", "_R", str(transform))
            elif "_R" in str(transform):
                transform = re.sub("_R", "_L", str(transform))
        transforms_dict.update({transform:mtx})
    
    return transforms_dict

def get_symmetrical_transform(objects=[], axis="yz", opposite=False):
    """
    Get the symmetrical tranformation matrix from a define 2 axis mirror plane.

    objects : list
        
        List of objects to get the symmetrical xform of.

    axis : str
        
        The mirror plane.
        default="yz"
    
    opposite : bool

        mirrors the opposite transform of the selected object by replacing "_L" with "_R" or vice versa
        default=False

    returns : matrix

        The symmetrical tranformation matrix.
    """

    transforms_dict = {}

    # No specified transforms, so will get selection
    if not objects:
        objects = pm.selected(type='transform')

    for obj in objects:

        transform = obj.getMatrix(worldSpace=True)

        if axis == "yz":
            mirror = pm.datatypes.TransformationMatrix(-1, 0, 0, 0,
                                                    0, 1, 0, 0,
                                                    0, 0, 1, 0,
                                                    0, 0, 0, 1)

        if axis == "xy":
            mirror = pm.datatypes.TransformationMatrix(1, 0, 0, 0,
                                                    0, 1, 0, 0,
                                                    0, 0, -1, 0,
                                                    0, 0, 0, 1)
        if axis == "xz":
            mirror = pm.datatypes.TransformationMatrix(1, 0, 0, 0,
                                                    0, -1, 0, 0,
                                                    0, 0, 1, 0,
                                                    0, 0, 0, 1)
        mtx = transform * mirror

        if opposite:
            if "_L" in str(obj):
                obj = re.sub("_L", "_R", str(obj))
            elif "_R" in str(obj):
                obj = re.sub("_R", "_L", str(obj))
        transforms_dict.update({obj:mtx})

    return transforms_dict