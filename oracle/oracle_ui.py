from shiboken2 import wrapInstance
from PySide2 import QtGui, QtCore, QtWidgets
from maya import OpenMayaUI as OpenMayaUI
from maya import cmds
import pymel.core as pm
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil
import os
from rigging_utils import naming
reload(naming)

# create an indent for printing tabs
row_format = "{:>3}" 
indent = row_format.format("")

def convert_name_data_to_string(data):
    string = ""
    for x in data:
        string = string + x + ";"
    return string

# get all the data of naming
name_rule = naming.DEFAULT_NAMING_RULE
joint_names_data = naming.ALLOWED_JOINT_NAMES
side_names_data = naming.ALLOWED_SIDE_NAMES
control_names_data = [naming.DEFAULT_CONTROL_EXT_NAME]
display_layers_data = naming.DEFAULT_DISPLAY_LAYERS

# need to convert the json files to strings for the pyside lineEdit, so user can change values at any time
joint_extension_string = convert_name_data_to_string(joint_names_data)
joint_side_string = convert_name_data_to_string(side_names_data)
control_extension_string = convert_name_data_to_string(control_names_data)
control_side_string = convert_name_data_to_string(side_names_data)
display_layers_string = convert_name_data_to_string(display_layers_data)

class OracleWindow(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    toolName = 'Oracle'
    toolVersion = '0.1.0'
    warning_color = "{ background-color: darkRed; color: rgba(250, 250, 250, 250);}"
    passed_color = "{ background-color: darkGreen; color: rgba(250, 250, 250, 250);}"

    def __init__(self, parent = None):
        # delete self first
        self.deleteInstances()

        super(self.__class__, self).__init__(parent = parent)
        mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow() 
        self.mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtWidgets.QMainWindow)
        self.setObjectName(self.__class__.toolName) # Make this unique enough if using it to clear previous instance!

        # Setup window's properties
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(self.toolName+' '+self.toolVersion)
        self.resize(200, 200)

        # Create tab widgets
        self.tab_bar = QtWidgets.QTabWidget(self)
        self.check_tab = QtWidgets.QWidget()
        self.edit_tab = QtWidgets.QWidget()
        self.tab_bar.addTab(self.check_tab, 'Check')
        self.tab_bar.addTab(self.edit_tab, 'Edit')

        # Create main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_layout.addWidget(self.tab_bar)
        self.check_layout = QtWidgets.QGridLayout()
        self.edit_layout = QtWidgets.QGridLayout()
        self.check_tab.setLayout(self.check_layout)
        self.edit_tab.setLayout(self.edit_layout)
        self.setLayout(self.main_layout)

        # Create check widgets
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setColumnCount(6)
        items = ["Check", "Status", "Type", "Help", "Select", "Fix"]
        self.tree_widget.setHeaderLabels(items)
        self.tree_widget.resizeColumnToContents(True)

        checks_list = ["test", "test2"]
        for check in checks_list:
            tree_item = QtWidgets.QTreeWidgetItem(check)
            child = QtWidgets.QTreeWidgetItem(tree_item)
            child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
            child.setCheckState(0, QtCore.Qt.Unchecked)
            self.tree_widget.addTopLevelItem(tree_item)

        self.check_layout.addWidget(self.tree_widget)
        


        '''
        self.assembly_transforms_button = QtWidgets.QPushButton("Check Assembly Transforms")
        self.duplicate_names_button = QtWidgets.QPushButton("Check Duplicate Names")
        self.joint_names_button = QtWidgets.QPushButton("Check Joint Names")
        self.control_names_button = QtWidgets.QPushButton("Check Control Names")
        self.control_transforms_button = QtWidgets.QPushButton("Check Control Transforms")
        self.control_keys_button = QtWidgets.QPushButton("Check For Control Keys")
        self.unknown_node_button = QtWidgets.QPushButton("Check For Unknown Nodes")
        self.ng_node_button = QtWidgets.QPushButton("Check For ngSkin Nodes")
        self.display_layers_button = QtWidgets.QPushButton("Check Display Layers")
        self.display_points_button = QtWidgets.QPushButton("Check Display Points Nodes")
        self.ikfk_snap_button = QtWidgets.QPushButton("Check Message Connections")

        # Add widgets to check layout
        self.check_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.check_layout.addWidget(self.assembly_transforms_button)
        self.check_layout.addWidget(self.duplicate_names_button)
        self.check_layout.addWidget(self.joint_names_button)
        self.check_layout.addWidget(self.control_names_button)
        self.check_layout.addWidget(self.control_transforms_button)
        self.check_layout.addWidget(self.control_keys_button)
        self.check_layout.addWidget(self.unknown_node_button)
        self.check_layout.addWidget(self.ng_node_button)
        self.check_layout.addWidget(self.display_layers_button)
        self.check_layout.addWidget(self.display_points_button)
        self.check_layout.addWidget(self.ikfk_snap_button)
        '''

        # Create edit widgets
        self.edit_name_rule = QtWidgets.QLabel("Naming Rule")
        self.edit_name_rule_line = QtWidgets.QLineEdit(name_rule)
        self.edit_name_rule_line.setEnabled(False)
        self.edit_joint_extension = QtWidgets.QLabel("Allowed Joint Extensions")
        self.edit_joint_extension_line = QtWidgets.QLineEdit(joint_extension_string)
        self.edit_joint_side = QtWidgets.QLabel("Allowed Joint Sides")
        self.edit_joint_side_line = QtWidgets.QLineEdit(joint_side_string)
        self.edit_control_extension = QtWidgets.QLabel("Allowed Control Extensions")
        self.edit_control_extension_line = QtWidgets.QLineEdit(control_extension_string)
        self.edit_control_side = QtWidgets.QLabel("Allowed Control Side")
        self.edit_control_side_line = QtWidgets.QLineEdit(control_side_string)
        self.edit_display_layers = QtWidgets.QLabel("Allowed Display Layers")
        self.edit_display_layers_line = QtWidgets.QLineEdit(display_layers_string)

        # Add widgets to edit layout
        self.edit_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.edit_layout.addWidget(self.edit_name_rule)
        self.edit_layout.addWidget(self.edit_name_rule_line)
        self.edit_layout.addWidget(self.edit_joint_extension)
        self.edit_layout.addWidget(self.edit_joint_extension_line)
        self.edit_layout.addWidget(self.edit_joint_side)
        self.edit_layout.addWidget(self.edit_joint_side_line)
        self.edit_layout.addWidget(self.edit_control_extension)
        self.edit_layout.addWidget(self.edit_control_extension_line)
        self.edit_layout.addWidget(self.edit_control_side)
        self.edit_layout.addWidget(self.edit_control_side_line)
        self.edit_layout.addWidget(self.edit_display_layers)
        self.edit_layout.addWidget(self.edit_display_layers_line)

        # Connect buttons to scripts
        '''
        self.assembly_transforms_button.clicked.connect(self.check_assembly_transforms)
        self.duplicate_names_button.clicked.connect(self.check_duplicate_names)
        self.joint_names_button.clicked.connect(self.check_all_joint_names)
        self.control_names_button.clicked.connect(self.check_all_control_names)
        self.control_transforms_button.clicked.connect(self.check_all_control_transforms)
        self.control_keys_button.clicked.connect(self.check_for_control_keys)
        self.unknown_node_button.clicked.connect(self.check_for_unknown_nodes)
        self.ng_node_button.clicked.connect(self.check_for_ng_nodes)
        self.display_layers_button.clicked.connect(self.check_display_layers)
        self.display_points_button.clicked.connect(self.check_for_displayPoints_nodes)
        self.ikfk_snap_button.clicked.connect(self.check_ikfk_snap)
        '''

    def check_all_joint_names(self):
        failed_list = []
        passed_list = []
        names_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating joint names tests...")
        print ("Checking number of parts in joint name")
        print ("Checking joint prefix against dictionary")
        print ("Checking joint side against dictionary")
        print ("Checking if joint has correct index values", "\n")

        rule_split = name_rule.split("_")

        for jnt in cmds.ls(type="joint"):
            # name starts good
            name_good = True

            # check if number of parts is the same as the rule
            if len(jnt.split("_")) != len(rule_split):
                print (jnt, "does NOT match rule:", name_rule)
                name_good = False

            if name_good:
                # split the name into parts to run the rest of the checks
                name_split = jnt.split("_")
                comp_name = name_split[0]
                side_name = name_split[1][0]
                compIdx_name = name_split[1][1:]
                idx_name = name_split[2]
                ext_name = name_split[3]

                # check if the side letter is within the allowed sides
                if side_name not in self.edit_joint_side_line.text():
                    print (jnt, "side letter is not in the allowed sides")
                    name_good = False
                # check if the component index values are all digits
                if not compIdx_name.isdigit():
                    print (jnt, "side index is not all numbers")
                    name_good = False
                # check if the index value is all digits
                if not idx_name.isdigit():
                    print (jnt, "index values are not all numbers")
                    name_good = False
                # check  if the total is 3 characters
                if len(idx_name) != 3:
                    print (jnt, "index number is not 3 characters")
                    name_good = False
                # check if the extension is within the allowed extensions
                if ext_name not in self.edit_joint_extension_line.text():
                    print (jnt, "extension is not in the allowed extensions")
                    name_good = False
            
            if not name_good:
                failed_list.append(jnt)
        
        if names_dict["FAILED"]:
            self.joint_names_button.setStyleSheet("QPushButton "+self.warning_color)
        else:
            self.joint_names_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nJOINTS NAMED CORRECTLY")

        return names_dict

    def check_all_control_names(self):
        failed_list = []
        passed_list = []
        names_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating control names tests...")
        print ("Only running on all tranform nodes that begin with 'ctl_'")
        print ("Checking number of parts in control name")
        print ("Checking control prefix against dictionary")
        print ("Checking control side against dictionary")
        print ("Checking if control has correct index values", "\n")

        rule_split = name_rule.split("_")

        for control in cmds.ls("*_ctl", type="transform"):
            # name starts good
            name_good = True

            # check if number of parts is the same as the rule
            if len(control.split("_")) != len(rule_split):
                print (control, "does NOT match rule:", name_rule)
                name_good = False

            if name_good:
                # split the name into parts to run the rest of the checks
                name_split = control.split("_")
                comp_name = name_split[0]
                side_name = name_split[1][0]
                compIdx_name = name_split[1][1:]
                idx_name = name_split[2]
                ext_name = name_split[3]

                # check if the side letter is within the allowed sides
                if side_name not in self.edit_control_side_line.text():
                    print (control, "side letter is not in the allowed sides")
                    name_good = False
                # check if the component index values are all digits
                if not compIdx_name.isdigit():
                    print (control, "side index is not all numbers")
                    name_good = False
                # check if the index value is all digits
                if not idx_name.isdigit():
                    print (control, "index values are not all numbers")
                    name_good = False
                # check  if the total is 3 characters
                if len(idx_name) != 3:
                    print (control, "index number is not 3 characters")
                    name_good = False
                # check if the extension is within the allowed extensions
                if ext_name not in self.edit_control_extension_line.text():
                    print (control, "extension is not in the allowed extensions")
                    name_good = False
                
            if not name_good:
                failed_list.append(control)
        
        if names_dict["FAILED"]:
            self.control_names_button.setStyleSheet("QPushButton "+self.warning_color)
        else:
            self.control_names_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nCONTROLS NAMED CORRECTLY")

        return names_dict

    def check_all_control_transforms(self):
        failed_list = []
        passed_list = []
        transforms_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating control transforms tests...")
        print ("Only running on all tranforms nodes that end with '_ctl'")
        print ("Checking if all translates and rotates are 0 and if all scales are 1", "\n")

        # This section checks for the main transforms of every control
        for con in cmds.ls("*_ctl", type="transform"):
            print ("Checking Control: ", con)
            if round(cmds.getAttr(con+'.translateX'), 5) != 0.0:
                print (indent, "Translate X is not set to 0")
                if con not in failed_list:
                    failed_list.append(con)
            if round(cmds.getAttr(con+'.translateY'), 5) != 0.0:
                print (indent, "Translate Y is not set to 0")
                if con not in failed_list:
                    failed_list.append(con)
            if round(cmds.getAttr(con+'.translateZ'), 5) != 0.0:
                print (indent, "Translate Z is not set to 0")
                if con not in failed_list:
                    failed_list.append(con)
            if round(cmds.getAttr(con+'.rotateX'), 5) != 0.0:
                print (indent, "Rotate X is not set to 0")
                if con not in failed_list:
                    failed_list.append(con)
            if round(cmds.getAttr(con+'.rotateY'), 5) != 0.0:
                print (indent, "Rotate Y is not set to 0")
                if con not in failed_list:
                    failed_list.append(con)
            if round(cmds.getAttr(con+'.rotateZ'), 5) != 0.0:
                print (indent, "Rotate Z is not set to 0")
                if con not in failed_list:
                    failed_list.append(con)
            if round(cmds.getAttr(con+'.scaleX'), 5) != 1.0:
                print (indent, "Scale X is not set to 1")
                if con not in failed_list:
                    failed_list.append(con)
            if round(cmds.getAttr(con+'.scaleY'), 5) != 1.0:
                print (indent, "Scale Y is not set to 1")
                if con not in failed_list:
                    failed_list.append(con)
            if round(cmds.getAttr(con+'.scaleZ'), 5) != 1.0:
                print (indent, "Scale Z is not set to 1")
                if con not in failed_list:
                    failed_list.append(con)

            if con not in failed_list:
                passed_list.append(con)

        if transforms_dict["FAILED"]:
            self.control_transforms_button.setStyleSheet("QPushButton "+self.warning_color)
        else:
            self.control_transforms_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nCONTROLS ZEROED")

        return transforms_dict
    
    def check_for_control_keys(self):
        failed_list = []
        passed_list = []
        control_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating control keys tests...")
        print ("Only running on all tranforms nodes that end with '_ctl'")
        print ("Checking if there are any keys on controls. Currently only attributes that are 'keyable=True'")

        # This way only works on keyable attributes
        for con in cmds.ls("*_ctl", type="transform"):
            if cmds.keyframe(con, q=True):
                failed_list.append(con)
                print ("\nKeyframe node:", cmds.keyframe(con, q=True, name=True), "on object:", con)
        
        if control_dict["FAILED"]:
            self.control_keys_button.setStyleSheet("QPushButton "+self.warning_color)
        else:
            self.control_keys_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nNO KEYS FOUND")

        return control_dict

    def check_for_unknown_nodes(self):
        failed_list = []
        passed_list = []
        unknown_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating unknown nodes tests...")
        print ("Lists all nodes of type 'unknown'")

        for i in cmds.ls(type="unknown"):
            failed_list.append(i)
            print (i)
        
        if unknown_dict["FAILED"]:
            self.unknown_node_button.setStyleSheet("QPushButton "+self.warning_color)
        else:
            self.unknown_node_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nNONE")

        return unknown_dict

    def check_for_ng_nodes(self):
        failed_list = []
        passed_list = []
        ng_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating ng nodes tests...")
        print ("Lists all nodes of type 'ngst2SkinLayerData'")

        for i in cmds.ls(type="ngst2SkinLayerData"):
            failed_list.append(i)
            print (i)
        
        if ng_dict["FAILED"]:
            self.ng_node_button.setStyleSheet("QPushButton "+self.warning_color)
        else:
            self.ng_node_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nNONE")

        return ng_dict

    def check_display_layers(self):
        failed_list = []
        passed_list = []
        display_layer_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating unknown nodes tests...")
        print ("Checking if display layer exists based on dictionary")
        print ("Checking if something is a member of each display layer")
        print ("Checking if 'geo' display layer is set to reference")

        # check if display layers exist and if they do, check if there are members within them
        for layer_name in self.edit_display_layers_line.text().split(";"):
            if layer_name:
                if cmds.ls(layer_name, type="displayLayer"):
                    if not cmds.editDisplayLayerMembers(layer_name, q=True):
                        print ("\nNothing is a member of display layer:", layer_name)
                        failed_list.append(layer_name)
                else:
                    print ("\nDisplay layer doesn't exist:", layer_name)
                    failed_list.append(layer_name)

                # check if "geo" displayLayer is set to reference
                if layer_name == "geo":
                    if cmds.ls(layer_name, type="displayLayer"):
                        if cmds.getAttr("geo.displayType") != 2:
                            print ("\n'geo' display layer is not set to reference")
                            failed_list.append(layer_name)
                    else:
                        failed_list.append(layer_name)
                
                # check if "controls" displayLayer is set to reference
                if layer_name == "controls":
                    if not cmds.ls(layer_name, type="displayLayer"):
                        failed_list.append(layer_name)
        
        if display_layer_dict["FAILED"]:
            self.display_layers_button.setStyleSheet("QPushButton "+self.warning_color)
        else:
            self.display_layers_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nDISPLAY LAYERS CORRECT")

        return display_layer_dict
    
    def check_ikfk_snap(self):
        failed_list = []
        passed_list = []
        connections_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating ikfk message connection tests...")
        print ("Checking if attributes exists based on dictionary")
        print ("Checking if the attribute has an incoming connection")

        L_arm_dict = {
                "fk_001":"shoulderFk_L0_001_ctl",
                "fk_002":"elbowFk_L0_001_ctl",
                "fk_003":"wristFk_L0_001_ctl",
                "fk_001_offset":"armFkOffset_L0_001_loc",
                "fk_002_offset":"armFkOffset_L0_002_loc",
                "fk_003_offset":"armFkOffset_L0_002_loc",
                "ik_base":"armIk_L0_001_ctl",
                "ik_handle":"handIk_L0_001_ctl",
                "ik_pole":"armPoleVectorIk_L0_001_ctl",
                "ik_offset":"ikHandOffset_arm_L0_loc",
                "ikm_001":"arm_L0_001_ikm",
                "ikm_002":"arm_L0_002_ikm",
                "ikm_003":"arm_L0_003_ikm",
             }

        R_arm_dict = {
                        "fk_001":"shoulderFk_R0_001_ctl",
                        "fk_002":"elbowFk_R0_001_ctl",
                        "fk_003":"wristFk_R0_001_ctl",
                        "fk_001_offset":"armFkOffset_R0_001_loc",
                        "fk_002_offset":"armFkOffset_R0_002_loc",
                        "fk_003_offset":"armFkOffset_R0_002_loc",
                        "ik_base":"armIk_R0_001_ctl",
                        "ik_handle":"handIk_R0_001_ctl",
                        "ik_pole":"armPoleVectorIk_R0_001_ctl",
                        "ik_offset":"ikHandOffset_arm_R0_loc",
                        "ikm_001":"arm_R0_001_ikm",
                        "ikm_002":"arm_R0_002_ikm",
                        "ikm_003":"arm_R0_003_ikm",
                    }

        L_leg_dict = {
                        "fk_001":"hipFk_L0_001_ctl",
                        "fk_002":"kneeFk_L0_001_ctl",
                        "fk_003":"ankleFk_L0_001_ctl",
                        "fk_005":"legFk_L0_005_ctl",
                        "fk_001_offset":"legFkOffset_L0_001_loc",
                        "fk_002_offset":"legFkOffset_L0_002_loc",
                        "fk_003_offset":"legFkOffset_L0_003_loc",
                        "ik_base":"legIk_L0_001_ctl",
                        "ik_handle":"footIk_L0_001_ctl",
                        "ik_pole":"legPoleVectorIk_L0_001_ctl",
                        "ik_offset":"ikFootOffset_leg_L0_loc",
                        "ik_ball":"legBallIk_L0_001_ctl",
                        "ikm_001":"leg_L0_001_ikm",
                        "ikm_002":"leg_L0_002_ikm",
                        "ikm_003":"leg_L0_003_ikm",
                        "ikm_006":"leg_L0_006_ikm",
                    }

        R_leg_dict = {
                        "fk_001":"hipFk_R0_001_ctl",
                        "fk_002":"kneeFk_R0_001_ctl",
                        "fk_003":"ankleFk_R0_001_ctl",
                        "fk_005":"legFk_R0_005_ctl",
                        "fk_001_offset":"legFkOffset_R0_001_loc",
                        "fk_002_offset":"legFkOffset_R0_002_loc",
                        "fk_003_offset":"legFkOffset_R0_003_loc",
                        "ik_base":"legIk_R0_001_ctl",
                        "ik_handle":"footIk_R0_001_ctl",
                        "ik_pole":"legPoleVectorIk_R0_001_ctl",
                        "ik_offset":"ikFootOffset_leg_R0_loc",
                        "ik_ball":"legBallIk_R0_001_ctl",
                        "ikm_001":"leg_R0_001_ikm",
                        "ikm_002":"leg_R0_002_ikm",
                        "ikm_003":"leg_R0_003_ikm",
                        "ikm_006":"leg_R0_006_ikm",
                    }


        controls = {"armSettings_L0_001_ctl":L_arm_dict, 
                    "armSettings_R0_001_ctl":R_arm_dict, 
                    "legSettings_L0_001_ctl":L_leg_dict, 
                    "legSettings_R0_001_ctl":R_leg_dict}

        for obj in controls:
            for attr in controls[obj]:

                # check if the attribute exists
                if not cmds.attributeQuery(attr, node=obj, exists=True):
                    print ("Attribute %s does NOT exist on object:" %attr, obj)
                    failed_list.append(obj+"."+attr)
                
                # check if the corrent connection is made to the attribute
                else:
                    if cmds.listConnections(obj+"."+attr):
                        connected = str(cmds.listConnections(obj+"."+attr)[0])
                        target = str(controls[obj][attr])
                        if connected == target:
                            pass
                        else:
                            print ("Attribute %s does NOT have the correct incoming connection:" %attr, connected, "should be", target)
                            failed_list.append(obj+"."+attr)
                    else:
                        print ("Attribute %s does NOT have an incoming connection:" %attr, target, "should be connected")
                        failed_list.append(obj+"."+attr)

        if connections_dict["FAILED"]:
            self.ikfk_snap_button.setStyleSheet("QPushButton "+self.warning_color)
        else:
            self.ikfk_snap_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nIKFK MESSAGE CONNECTIONS CORRECT")

        return connections_dict

    def check_for_displayPoints_nodes(self):
        failed_list = []
        passed_list = []
        node_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating displayPoints nodes tests...")
        print ("Checking if any displayPoints nodes exist in the scene")

        for i in cmds.ls(type="displayPoints"):
            failed_list.append(i)
            
        if node_dict["FAILED"]:
            self.display_points_button.setStyleSheet("QPushButton "+self.warning_color)
            print node_dict["FAILED"]
        else:
            self.display_points_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nDISPLAY POINTS CORRECT")

        return node_dict
    
    def check_assembly_transforms(self):
        failed_list = []
        passed_list = []
        node_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating assembly transforms tests...")
        print ("Checking if any geo under the assembly node has any dirty transforms")

        zero_attrs = ["tx", "ty", "tz", "rx", "ry", "rz"]
        one_attrs  = ["sx", "sy", "sz"]

        for i in cmds.ls("geo_grp", dag=True, type="transform"):
            for attr in zero_attrs:
                if cmds.getAttr(i+"."+attr) != 0.0:
                    failed_list.append(i+"."+attr)
            for attr in one_attrs:
                if cmds.getAttr(i+"."+attr) != 1.0:
                    failed_list.append(i+"."+attr)
        
        for i in cmds.ls("*_assembly", type="transform"):

            children = cmds.listRelatives(i, children=True)
            
            for attr in zero_attrs:

                if cmds.getAttr(i+"."+attr) != 0.0:
                    failed_list.append(i+"."+attr)

                for child in children:
                    if cmds.getAttr(child+"."+attr) != 0.0:
                        failed_list.append(child+"."+attr)

            for attr in one_attrs:

                if cmds.getAttr(i+"."+attr) != 1.0:
                    failed_list.append(i+"."+attr)

                for child in children:
                    if cmds.getAttr(child+"."+attr) != 1.0:
                        failed_list.append(child+"."+attr)
    
                
            
        if node_dict["FAILED"]:
            self.assembly_transforms_button.setStyleSheet("QPushButton "+self.warning_color)
            for i in node_dict["FAILED"]:
                print (i, "Has dirty values")
        else:
            self.assembly_transforms_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nASSEMBLY TRANSFORMS CORRECT")

        return node_dict

    def check_duplicate_names(self):
        failed_list = []
        passed_list = []
        node_dict = {"PASSED":passed_list, "FAILED":failed_list}
        print ("\n\nInitiating duplicate naming tests...")
        print ("Checking if anything in the scene contains '|' in its name, which will happen to duplicate name paths\n")

        list_all = pm.ls()
        for i in list_all:
            if "|" in i.name():
                failed_list.append(i)

        if node_dict["FAILED"]:
            self.duplicate_names_button.setStyleSheet("QPushButton "+self.warning_color)
            for i in node_dict["FAILED"]:
                print (i, "is not a unique name")
        else:
            self.duplicate_names_button.setStyleSheet("QPushButton "+self.passed_color)
            print ("\nASSEMBLY TRANSFORMS CORRECT")


    # Delete any instances of this class
    def deleteInstances(self):
        if cmds.workspaceControl(self.__class__.toolName+'WorkspaceControl', exists=True, q=True) == True:
            cmds.deleteUI(self.__class__.toolName+'WorkspaceControl', control=True)

    # Show window with docking ability
    def run(self):
        self.show(dockable = True)
