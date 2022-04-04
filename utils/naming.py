# Written by Justin Phillips
# Repurposing some code from mgear version 3.7.0 and adding custom functions
# setting department naming conventions to be used in other code

import pymel.core as pm
import string 

NAMING_RULE_TOKENS = ["component", "side", "componentIndex", "index", "extension"]
DEFAULT_NAMING_RULE = r"{component}_{side}{componentIndex}_{index}_{extension}"
DEFAULT_SIDE_L_NAME = "L"
DEFAULT_SIDE_R_NAME = "R"
DEFAULT_SIDE_C_NAME = "C"
DEFAULT_COMPONENT_INDEX = "0"
DEFAULT_INDEX = "001"
DEFAULT_JOINT_EXT_NAME = "def"
DEFAULT_CONTROL_EXT_NAME = "ctl"
DEFAULT_DISPLAY_LAYERS = ["controls", "geo"]
DEFAULT_SHADING_NODE_EXT_NAME = {
    "addDoubleLinear":["adl"],
    "addMatrix":["amx"],
    "angleBetween":["abw"],
    "arrayMapper":["amp"],
    "axisAngleToQuat":["aaq"],
    "blendColors":["blc"],
    "blendTwoAttr":["b2a"],
    "bump2d":["b2d"],
    "bump3d":["b3d"],
    "choice":["cho"],
    "chooser":["chs"],
    "clamp":["clp"],
    "colorProfile":["cop"],
    "condition":["cnd"],
    "contrast":["cot"],
    "curveInfo":["cvi"],
    "distanceBetween":["dtb"],
    "doubleSwitch":["dsw"],
    "eulerToQuat":["etq"],
    "fourByFourMatrix":["ffm"],
    "frameCahche":["fch"],
    "gammaCorrect":["gmc"],
    "heightField":["hfd"],
    "HsvToRgb":["htr"],
    "inverseMatrix":["imx"],
    "lightInfo":["lgi"],
    "luminance":["lum"],
    "multDoubleLinear":["mln"],
    "multMatrix":["mmx"],
    "multiplyDivide":["mdv"],
    "particleSampler":["psm"],
    "2dPlacement":["d2p"],
    "3dPlacement":["d3p"],
    "plusMinusAverage":["pma"],
    "projection":["prj"],
    "quatSwitch":["qsw"],
    "quatAdd":["qad"],
    "quatConjugate":["qcj"],
    "quatInvert":["qin"],
    "quatNegate":["qng"],
    "quatNormalize":["qnm"],
    "quatProd":["qpd"],
    "quatSlerp":["qsp"],
    "quatSub":["qsb"],
    "quatToAxisAngle":["qaa"],
    "remapColor":["rmc"],
    "remapHsv":["rmh"],
    "remapValue":["rmv"],
    "reverse":["rev"],
    "rgbToHsv":["rgh"],
    "samplerInfo":["sfi"],
    "setRange":["srg"],
    "singleSwitch":["ssw"],
    "stencil":["stn"],
    "surfLuminanace":["sfl"],
    "transposeMatrix":["tmx"],
    "tripleSwitch":["tsw"],
    "unitConversion":["unc"],
    "uvChooser":["uvc"],
    "vectorProduct":["vpt"],
    "weightedAddMatrix":["wam"]
}
ALLOWED_JOINT_NAMES = ["def", "con", "prt", "ikm", "fkm", "hlp", "ctl", "wgt", "pos", "mst", "jnt"]
ALLOWED_SIDE_NAMES = ["L", "R", "C"]


def validate_name(name, rule=DEFAULT_NAMING_RULE, rule_validate=True):
    """
    Checks the passed name against the given rule

    name : str
        
        Name of passed object

    rule : str
        
        Rule to validate against
        default={component}_{side}{componentIndex}_{index}_{extension}

    rule_validate : bool
        
        Validates the rule before validating name
        default=True
    
    returns : bool
        returns True if name matches the rule
    """
    validate_rule(rule)

    rule_split = rule.split("_")
    name_split = name.split("_")

    name_good = True

    # check if number of parts is the same as the rule
    if len(name_split) == len(rule_split):
        name_good = True
    else:
        print (name, "Does NOT match rule:", rule)
        name_good = False

    # TODO need to fix this up to not be restricted code
    # check if the side is in allowed sides and if the componentIndex is a digit
    for i in rule_split:
        if i == r"{side}{componentIndex}":
            # get the split index of where the side and component index live within the rule
            split_index = rule_split.index(i)
            if len(name_split[split_index]) < 2:
                print (name, "Does NOT match rule:", rule)
                name_good = False
            if name_split[split_index][0] in ALLOWED_SIDE_NAMES:
                name_good = True
            else:
                print (split_index[0], "is NOT in ALLOWED_SIDE_NAMES:", ALLOWED_SIDE_NAMES)
                name_good = False
            # check if the rest of the numbers here are actually digits
            for i in name_split[split_index][1:]:
                if i.isdigit():
                    name_good = True
                else:
                    print (name, "Does NOT match rule:", rule)
                    name_good = False

    return name_good


def validate_rule(rule, valid_tokens=NAMING_RULE_TOKENS, log=True):
    """
    Checks if the rule contains parts from the NAMING_RULE_TOKENS

    rule : str
        
        Rule to validate

    valid_tokens : list
        
        Valid tokens for the rule
        default=["component", "side", "componentIndex", "index", "extension"]

    log : bool

        if True will display warnings
        default=True

    returns : bool
        
        returns True if the rule is valid
    """
    invalid_tokens = []
    for token in string.Formatter().parse(rule):

        if token[1] and token[1] in valid_tokens:
            continue
        # compare to None to avoid errors with empty token
        elif token[1] is None and token[0]:
            continue
        else:
            invalid_tokens.append(token[1])

    if invalid_tokens:
        if log:
            pm.displayWarning(
                "{} not valid token".format(invalid_tokens))
            pm.displayInfo("Valid tokens are: {}".format(NAMING_RULE_TOKENS))
        return
    else:
        return True