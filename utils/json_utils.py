import json, os
import pymel.core as pm

def save_json(directory, file_name, data):
    """
    Save JSON:
        save_json(directory, file_name, data) 
        Saves given data to a json file named the given file name to the given directory

    Args:
        directory (str): Path to the folder you want to save the json file
        file_name (str): The name of the json file being saved
        data: Saves this data to the json file
    
    Returns:
        str: File path
    """
    # saves a new file by iteration
    path = "%s/%s" %(directory, file_name)

    # Write the json file with the list of dictionaries
    try:
        with open(path, 'w') as outfile:
            json.dump(data, outfile)
        print ('File Saved:', path)
    except:
        raise
    return path

def load_json(filepath):
    """
    Load JSON:
        load_json(filepath)
        Loads the json file and returns the dat within

    Args:
        filepath (str): File path of the json file loaded
    
    Returns:
        data: Data within the json file
    """
    # Load the selected file
    if os.path.exists(filepath):
        data = json.load(open(filepath))
    else:
        data = None

    return data

def save_as_json(data):
    """
    Save JSON:
        save_as_json(data) 
        Saves given data to a json file named the given file name to the given directory

    Args:
        data: Saves this data to the json file
    
    Returns:
        str: File path
    """
    # saves a new file by iteration
    path = pm.fileDialog2()[0]

    # Write the json file with the list of dictionaries
    try:
        with open(path, 'w') as outfile:
            json.dump(data, outfile)
        print ('File Saved:', path)
    except:
        raise
    return path

def load_as_json():
    """
    Load JSON:
        load_json()
        Loads the json file and returns the data within
    
    Returns:
        data: Data within the json file
    """
    filepath = pm.fileDialog2()[0]
    
    # Load the selected file
    if os.path.exists(filepath):
        data = json.load(open(filepath))
    else:
        data = None

    return data