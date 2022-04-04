import pymel.core as pm

# TODO include gamma as an arg to change these values if needed in code
def hex_to_rgba(hex):
    """
    Converts HEX value to RGBA (0-1)

    hex : str 
        
        Hex value to convert
    
    returns : tuple

        Returns tuple as (R, G, B, A)
    """
    gamma = 2.2
    value = hex.lstrip('#')
    lv = len(value)
    fin = list(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    r = pow(float(fin[0]) / 255.0, gamma)
    g = pow(float(fin[1]) / 255.0, gamma)
    b = pow(float(fin[2]) / 255.0, gamma)
    a = pow(float(fin[3]) / 255.0, gamma)
    fin = []
    fin.append(r)
    fin.append(g)
    fin.append(b)
    fin.append(a)
    return tuple(fin)
    
# TODO include gamma as an arg to change these values if needed in code
def rgb_to_parametric(rgb):
    """
    Converts RGB (0-255) to RGB (0-1)

    rgb : tuple 
        
        Values of RGB color in a tuple (r, g, b, a) or (r, g, b)
    
    returns : tuple
        
        Returns tuple as (R, G, B, A)
    """
    parametric_rgb = []
    for value in rgb:
        parametric_rgb.append(float(value) / 255.0)
    return tuple(parametric_rgb)
