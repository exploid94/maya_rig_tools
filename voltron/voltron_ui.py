from shiboken2 import wrapInstance
from PySide2 import QtGui, QtCore, QtWidgets
from maya import OpenMayaUI as OpenMayaUI
from maya import cmds
import pymel.core as pm
import maya.mel as mel
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil
import os
from voltron import skin_merge_utils
import maya.OpenMaya as om
from rigging_utils import space_switch
from rigging_utils import attribute as rig_utils_attr
from mgear.core import transform, primitive, icon

# create an indent for printing tabs
row_format = "{:>3}" 
indent = row_format.format("")

class VoltronWindow(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    toolName = 'Voltron'
    toolVersion = '0.0.1'
    warning_color = "{ background-color: darkRed; color: rgba(250, 250, 250, 250);}"
    passed_color = "{ background-color: darkGreen; color: rgba(250, 250, 250, 250);}"



    def __init__(self, parent = None):
        # delete self first
        self.deleteInstances()

        # set variables
        self.face_namespace = "face_rig"
        self.body_namespace = "body_rig"

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
        self.import_face_tab = QtWidgets.QWidget()
        self.import_body_tab = QtWidgets.QWidget()
        self.combine_tab = QtWidgets.QWidget()
        self.tab_bar.addTab(self.import_face_tab, 'Import Face')
        self.tab_bar.addTab(self.import_body_tab, 'Import Body')
        self.tab_bar.addTab(self.combine_tab, 'Combine')


        # Create main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_layout.addWidget(self.tab_bar)

        self.import_face_layout = QtWidgets.QGridLayout()
        self.import_body_layout = QtWidgets.QGridLayout()
        self.combine_layout = QtWidgets.QGridLayout()

        self.import_face_tab.setLayout(self.import_face_layout)
        self.import_body_tab.setLayout(self.import_body_layout)
        self.combine_tab.setLayout(self.combine_layout)

        self.setLayout(self.main_layout)


        # Import face rig
        self.import_face_button = QtWidgets.QPushButton("Import Face Rig")
        self.face_geo_label = QtWidgets.QLabel("Load Face Rig Body Geo")
        self.face_geo_load = QtWidgets.QPushButton(" >> ")
        self.face_geo_name = QtWidgets.QLabel("None")
        self.create_face_hlp_joints_button = QtWidgets.QPushButton("Create Face hlp Joints")

        # Import body rig
        self.import_body_button = QtWidgets.QPushButton("Import Body Rig")
        self.body_geo_label = QtWidgets.QLabel("Load Body Rig Body Geo")
        self.body_geo_load = QtWidgets.QPushButton(" >> ")
        self.body_geo_name = QtWidgets.QLabel("None")
        self.transfer_shader_sets_button = QtWidgets.QPushButton("Transfer Shader Sets From Face")

        # Combine rigs
        self.root_list_label = QtWidgets.QLabel("The list below are the face groups that will be constrained to the body rig.\n"
                                                "To add to the list, just type in the text box above the add and remove buttons and click add.\n"
                                                "You do NOT need to add the namespace in the name added.\n"
                                                "Remove and rename any objects that need it.")
        face_root_list = ['lips_C0_root', 
                          'jawWorld_C0_root', 
                          'jawReverse_C0_root', 
                          'lipTopTweak_L0_root', 
                          'lipBottomTweak_L0_root', 
                          'LipBottomSide_L0_root', 
                          'LipBottomSide_R0_root', 
                          'lipTopTweak_R0_root', 
                          'lipBottomTweak_R0_root', 
                          'jawReverseTopDrv_C_000_adj', 
                          'jawWorldBottomDrv_C_000_adj', 
                          'jawWorldCornersDrv_C_000_adj']
        self.root_constraint_list = AddListWidget(namespace=self.face_namespace, init_items=face_root_list)
        self.combine_button = QtWidgets.QPushButton("Combine Rigs")

        self.geo_merge_label = QtWidgets.QLabel("The list below are the geos that we'll copy skins from face to body.\n"
                                                "Make sure the geos in the face rig and body rig are the same.")
        geo_merge_list = ['geo_body_000', 
                          'geo_hair_000']
        self.geo_merge_list = AddListWidget(namespace=None, init_items=geo_merge_list)

        # Add widgets for import face
        self.import_face_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.import_face_layout.addWidget(self.import_face_button, 0, 0, 1, 0)
        self.import_face_layout.addWidget(self.face_geo_label, 1, 0, 1, 1)
        self.import_face_layout.addWidget(self.face_geo_load, 1, 1, 1, 1)
        self.import_face_layout.addWidget(self.face_geo_name, 1, 2, 1, 1)
        self.import_face_layout.addWidget(self.create_face_hlp_joints_button, 2, 0, 1, 0)

        # Add widgets for import body
        self.import_body_layout.addWidget(self.import_body_button, 0, 0, 1, 0)
        self.import_body_layout.addWidget(self.body_geo_label, 1, 0, 1, 1)
        self.import_body_layout.addWidget(self.body_geo_load, 1, 1, 1, 1)
        self.import_body_layout.addWidget(self.body_geo_name, 1, 2, 1, 1)
        self.import_body_layout.addWidget(self.transfer_shader_sets_button, 2, 0, 1, 0)

        # Add widgets to edit layout
        self.combine_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.combine_layout.addWidget(self.root_list_label, 0, 0, 1, 0)
        self.combine_layout.addWidget(self.root_constraint_list, 1, 0, 1, 0)
        self.combine_layout.addWidget(self.geo_merge_label, 2, 0, 1, 0)
        self.combine_layout.addWidget(self.geo_merge_list, 3, 0, 1, 0)
        self.combine_layout.addWidget(self.combine_button, 4, 0, 1, 0)

        # Connect buttons to scripts
        self.import_face_button.clicked.connect(self.import_face_rig)
        self.face_geo_load.clicked.connect(self.load_face_geo)
        self.create_face_hlp_joints_button.clicked.connect(self.create_face_hlp_joints)

        self.import_body_button.clicked.connect(self.import_body_rig)
        self.body_geo_load.clicked.connect(self.load_body_geo)
        self.import_body_button.clicked.connect(self.transfer_shader_sets)

        self.combine_button.clicked.connect(self.combine_rigs)


    # helper functions
    def get_skin_cluster(self, obj):
        return pm.PyNode(mel.eval('findRelatedSkinCluster '+obj))

    def hide_face_objects(self):
        for i in ["geo_grp", "controlVis_grp"]:
            if pm.objExists(i):
                pm.hide(self.face_namespace+":"+i)

    def delete_face_display_layers(self):
        for obj in pm.ls(self.face_namespace+":*", type="displayLayer"):
            pm.delete(obj)
    
    def transfer_shader_sets(self):
        for i in pm.ls(self.face_namespace+":geo*"):
            try:
                pm.select(i, i.replace(self.face_namespace, self.body_namespace))
                pm.transferShadingSets()
            except:
                pass

    def perform_skin_merge(self):
        print "Merging Skin Clusters..."
        '''
        Applying the skinMerge process to specified  
        '''

        skin_merge = skin_merge_utils.skin_merge()

        # Select face and then body target geo for the following:
        geo_list = self.geo_merge_list.get_items()
                    
        for item in geo_list:
            face_geo = self.face_namespace+":"+item
            body_geo = self.body_namespace+":"+item
            if cmds.objExists(face_geo) and cmds.objExists(body_geo):
                cmds.select(face_geo, body_geo)
                
                # Run Charles' skinMerge
                items = pm.ls(sl=True)
                
                try:
                    if len(items) == 2:
                        skin_merge.move_skin( items[0], items[1] )
                
                        skin_merge.log(
                            '+ SkinMerge: Complete. Merged skin from {} onto {}.'
                            .format( *items )
                        )
                
                    else:
                        skin_merge.log( "-- Please select a skinned mesh and a target mesh.", error=True )
                except:
                    raise
    
    def replace_body_geo(self):
        # don't use the body rig geo since we don't need those weights
        # we'll just replace the body rig geo with the face rig geo and delete the body rig version
        pm.parent(pm.PyNode(self.face_namespace+":lin_eyes_grp"), self.body_namespace+":geo_grp")
        pm.parent(pm.PyNode(self.body_namespace+":lin_eyes_grp"), self.face_namespace+":geo_grp")

        pm.parent(pm.PyNode(self.face_namespace+":lin_face_grp"), self.body_namespace+":geo_grp")
        pm.parent(pm.PyNode(self.body_namespace+":lin_face_grp"), self.face_namespace+":geo_grp")

    def constrain_face_rig(self):
        face_root_list = self.root_constraint_list.get_items()

        try:
            for face_root in face_root_list:
                cmds.parentConstraint(self.body_namespace+':head_C0_001_def', face_root, mo=True)
                cmds.scaleConstraint(self.body_namespace+':head_C0_001_def', face_root, mo=True)
        except:
            pass

        # Parent face rig into body rig hierarchy
        try:
            cmds.parent(self.face_namespace+":rig_face", self.body_namespace+":rig_grp")
        except:
            pass

        try:
            pm.parentConstraint(self.body_namespace+':head_C0_001_def', self.bpm_grp, mo=True)
            pm.scaleConstraint(self.body_namespace+':head_C0_001_def', self.bpm_grp, mo=True)
        except:
            pass
    
    def add_eye_lookat_space(self):

        # get the eye nodes
        face_root = pm.PyNode("rig_face")
        eyes_ctl = pm.PyNode("eyes_C0_001_ctl")
        eyes_root = pm.PyNode("eyes_C0_root")
        god_ctl = pm.PyNode("godSub_C0_002_ctl")
        head_ctl = pm.PyNode("headSub_C0_001_ctl")

        # unlock the eyes_root transforms
        attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        for attr in attrs:
            pm.setAttr(eyes_root.attr(attr), lock=False)
            
        # make setup for god aim
        t = transform.getTransform(eyes_ctl)
        nul = primitive.addTransform(face_root, "eyesAim_C0_001_nul", t)
        ref = primitive.addTransform(head_ctl, "eyesAim_C0_001_ref", t)

        # move the ref object towards the head control
        t = pm.xform(nul, ws=True, t=True, q=True)
        v1 = om.MVector(t[0], t[1], t[2])
        t = pm.xform(head_ctl, ws=True, t=True, q=True)
        v2 = om.MVector(t[0], t[1], t[2])
        mid_point = (v1+v2) / 2
        new_point = (v2 - mid_point) * 1.5
        pm.move(ref, new_point, r=True, os=True)

        # need to create a control above the main eye control for the aim space switch
        t = transform.getTransform(eyes_ctl)
        adj = primitive.addTransform(eyes_root.getParent(), "eyesAim_C0_001_adj", t)
        ctl = icon.cube(adj, "eyesAim_C0_001_ctl", color=[1, 1, 0], m=t)
        pm.parent(eyes_root, ctl)

        # constrain the nul by aiming
        pm.parentConstraint(god_ctl, adj, mo=True)
        pm.pointConstraint(ctl, nul, mo=True)
        pm.aimConstraint(ref, nul, mo=True, wut=2, wuo=ref, aim=[0, 0, -1])


        space_switch.connectSpace( [god_ctl, head_ctl, nul], 
                                    eyes_root, 
                                    ctl=eyes_ctl,
                                    space_attr_type="float")

        pm.connectAttr(eyes_ctl+".eyesAim_C0_001_nul_parent", ctl.getShape().visibility)

    def remove_namespaces(self):
        pm.namespace(rm=self.body_namespace, mnr=True)
        pm.namespace(rm=self.face_namespace, mnr=True)
    
    def lock_hide_transforms(self):
        for t in pm.ls("rig_grp", dag=True, type="transform"):
            if not t.endswith("_ctl"):
                rig_utils_attr.set_keyable(t, keyable=False)
    
    def set_default_attrs():
        '''
        Script sets the vis_C0_001_ctl's visibility attributes default value. 
        House cleaning utility to help automate rig finaling for rig submission and publishing.
        '''

        # Clean up - Set the default visibility attributes
        visAttrDict = {
                    # All
                    'allControls':1, 
                    'allSubs':1,
                    'allBends':1,
                    'allTweaks':1,
                    # Face
                    'faceControls':1,
                    'browTweaks':0,
                    'eyeCreaseTweaks':0,
                    'eyelidTweaks':0,
                    'lipIkTweaks':0,
                    'lipFkTweaks':0,
                    'teeth':0,
                    'teethSubs':0,
                    'tongue':0,
                    'tongueTweaks':0,
                    # Body
                    'bodyControls':1,
                    'neckSubs':0,
                    'neckBends':0,
                    'neckTweaks':0,
                    'spineSubs':0,
                    'spineTweaks':0,
                    'armSubs':0,
                    'armBends':0,
                    'armTweaks':0,
                    'fingerSubs':0,
                    'fingerTweaks':0,
                    'legSubs':0,
                    'legBends':0,
                    'legTweaks':0,
                    'tailSubs':0,
                    'tailTweaks':0,
                    # Geo
                    'allGeo':1,
                    'bodyGeo':1,
                    'hairGeo':1,
                    'clothesGeo':1, 
                    }
                    
        visCtl = 'vis_C0_001_ctl'

        for attribute, value in visAttrDict.items():
            if cmds.objExists('{0}.{1}'.format(visCtl, attribute)):
                cmds.setAttr('{0}.{1}'.format(visCtl, attribute), value)
            else:
                print('The {0} visibility attribute not on the {1} '.format(attribute, visCtl))
        
    def set_reveal_rotate_orders(self, ctl_list, rotate_order):
            for ctl in ctl_list:
                if cmds.objExists(ctl+'.rotateOrder'):
                    cmds.setAttr(ctl+'.rotateOrder', rotate_order)

    def set_rotate_orders(self):
        #set rotate orders

        all_ctl = cmds.ls('*_ctl', type='transform')
        for ctl in all_ctl:
            cmds.setAttr(ctl+'.rotateOrder', keyable=True, channelBox=True)

        #xzy = 3
        #centered
        xzy_ordered = ['god_C0_001_ctl',
        'godSub_C0_001_ctl',
        'godSub_C0_002_ctl',
        'root_C0_001_ctl',
        'rootSub_C0_001_ctl',
        'pelvis_C0_001_ctl',
        'pelvisSub_C0_001_ctl']
        
        xzy_sided = ['shoulderFk_*0_001_ctl',
        'shoulderFkSub_*0_001_ctl']
        
        #sided list append into larger list
        for side_token in ['L', 'R']:
            for item in xzy_sided:
                xzy_item = item.replace("*", side_token)
                xzy_ordered.append(xzy_item)

        self.set_reveal_rotate_orders(xzy_ordered, 3)
        
        #yzx = 1
        yzx_ordered = []
        #sided hands
        yzx_sided = ['wristFk_*0_001_ctl',
        'wristFkSub_*0_001_ctl',
        'thumbBaseSub_*0_001_ctl',
        'thumbBaseTweak_*0_001_ctl',
        'thumbBaseTweak_*0_002_ctl',
        'thumbBase_*0_001_ctl',
        'thumbKnuckle_*0_001_ctl',
        'thumbKnuckle_*0_002_ctl',
        'thumbKnuckle_*0_003_ctl',
        'thumbMidSub_*0_001_ctl',
        'thumbMidTweak_*0_001_ctl',
        'thumbMidTweak_*0_002_ctl',
        'thumbMid_*0_001_ctl',
        'thumbSwingSub_*0_001_ctl',
        'thumbSwing_*0_001_ctl',
        'thumbTipSub_*0_001_ctl',
        'thumbTipTweak_*0_001_ctl',
        'thumbTipTweak_*0_002_ctl',
        'thumbTip_*0_001_ctl',
        'indexBaseSub_*0_001_ctl',
        'indexBaseTweak_*0_001_ctl',
        'indexBaseTweak_*0_002_ctl',
        'indexBase_*0_001_ctl',
        'indexHandSub_*0_001_ctl',
        'indexHandTweak_*0_001_ctl',
        'indexHand_*0_001_ctl',
        'indexKnuckle_*0_001_ctl',
        'indexKnuckle_*0_002_ctl',
        'indexKnuckle_*0_003_ctl',
        'indexMidSub_*0_001_ctl',
        'indexMidTweak_*0_001_ctl',
        'indexMidTweak_*0_002_ctl',
        'indexMid_*0_001_ctl',
        'indexPalmSub_*0_001_ctl',
        'indexPalmTweak_*0_001_ctl',
        'indexPalm_*0_001_ctl',
        'indexTipSub_*0_001_ctl',
        'indexTipTweak_*0_001_ctl',
        'indexTipTweak_*0_002_ctl',
        'indexTip_*0_001_ctl',
        'indexToeKnuckle_*0_001_ctl',
        'indexToeKnuckle_*0_002_ctl',
        'indexToeKnuckle_*0_003_ctl',
        'indexToeKnuckle_*0_004_ctl',
        'indexToeKnuckle_*0_005_ctl',
        'indexToeSub_*0_001_ctl',
        'indexToeSub_*0_002_ctl',
        'indexToeSub_*0_003_ctl',
        'indexToeSub_*0_004_ctl',
        'indexToeSub_*0_005_ctl',
        'indexToeTweak_*0_001_ctl',
        'indexToeTweak_*0_002_ctl',
        'indexToeTweak_*0_003_ctl',
        'indexToeTweak_*0_004_ctl',
        'indexToeTweak_*0_005_ctl',
        'indexToeTweak_*0_006_ctl',
        'indexToeTweak_*0_007_ctl',
        'indexToeTweak_*0_008_ctl',
        'indexToeTweak_*0_009_ctl',
        'indexToe_*0_001_ctl',
        'indexToe_*0_002_ctl',
        'indexToe_*0_003_ctl',
        'indexToe_*0_004_ctl',
        'indexToe_*0_005_ctl',
        'middleBaseSub_*0_001_ctl',
        'middleBaseTweak_*0_001_ctl',
        'middleBaseTweak_*0_002_ctl',
        'middleBase_*0_001_ctl',
        'middleHandSub_*0_001_ctl',
        'middleHandTweak_*0_001_ctl',
        'middleHand_*0_001_ctl',
        'middleKnuckle_*0_001_ctl',
        'middleKnuckle_*0_002_ctl',
        'middleKnuckle_*0_003_ctl',
        'middleMidSub_*0_001_ctl',
        'middleMidTweak_*0_001_ctl',
        'middleMidTweak_*0_002_ctl',
        'middleMid_*0_001_ctl',
        'middlePalmSub_*0_001_ctl',
        'middlePalmTweak_*0_001_ctl',
        'middlePalm_*0_001_ctl',
        'middleTipSub_*0_001_ctl',
        'middleTipTweak_*0_001_ctl',
        'middleTipTweak_*0_002_ctl',
        'middleTip_*0_001_ctl',
        'middleToeKnuckle_*0_001_ctl',
        'middleToeKnuckle_*0_002_ctl',
        'middleToeKnuckle_*0_003_ctl',
        'middleToeKnuckle_*0_004_ctl',
        'middleToeKnuckle_*0_005_ctl',
        'middleToeSub_*0_001_ctl',
        'middleToeSub_*0_002_ctl',
        'middleToeSub_*0_003_ctl',
        'middleToeSub_*0_004_ctl',
        'middleToeSub_*0_005_ctl',
        'middleToeTweak_*0_001_ctl',
        'middleToeTweak_*0_002_ctl',
        'middleToeTweak_*0_003_ctl',
        'middleToeTweak_*0_004_ctl',
        'middleToeTweak_*0_005_ctl',
        'middleToeTweak_*0_006_ctl',
        'middleToeTweak_*0_007_ctl',
        'middleToeTweak_*0_008_ctl',
        'middleToeTweak_*0_009_ctl',
        'middleToe_*0_001_ctl',
        'middleToe_*0_002_ctl',
        'middleToe_*0_003_ctl',
        'middleToe_*0_004_ctl',
        'middleToe_*0_005_ctl',
        'ringBaseSub_*0_001_ctl',
        'ringBaseTweak_*0_001_ctl',
        'ringBaseTweak_*0_002_ctl',
        'ringBase_*0_001_ctl',
        'ringHandSub_*0_001_ctl',
        'ringHandTweak_*0_001_ctl',
        'ringHand_*0_001_ctl',
        'ringKnuckle_*0_001_ctl',
        'ringKnuckle_*0_002_ctl',
        'ringKnuckle_*0_003_ctl',
        'ringMidSub_*0_001_ctl',
        'ringMidTweak_*0_001_ctl',
        'ringMidTweak_*0_002_ctl',
        'ringMid_*0_001_ctl',
        'ringPalmSub_*0_001_ctl',
        'ringPalmTweak_*0_001_ctl',
        'ringPalm_*0_001_ctl',
        'ringTipSub_*0_001_ctl',
        'ringTipTweak_*0_001_ctl',
        'ringTipTweak_*0_002_ctl',
        'ringTip_*0_001_ctl',
        'ringToeKnuckle_*0_001_ctl',
        'ringToeKnuckle_*0_002_ctl',
        'ringToeKnuckle_*0_003_ctl',
        'ringToeKnuckle_*0_004_ctl',
        'ringToeKnuckle_*0_005_ctl',
        'ringToeSub_*0_001_ctl',
        'ringToeSub_*0_002_ctl',
        'ringToeSub_*0_003_ctl',
        'ringToeSub_*0_004_ctl',
        'ringToeSub_*0_005_ctl',
        'ringToeTweak_*0_001_ctl',
        'ringToeTweak_*0_002_ctl',
        'ringToeTweak_*0_003_ctl',
        'ringToeTweak_*0_004_ctl',
        'ringToeTweak_*0_005_ctl',
        'ringToeTweak_*0_006_ctl',
        'ringToeTweak_*0_007_ctl',
        'ringToeTweak_*0_008_ctl',
        'ringToeTweak_*0_009_ctl',
        'ringToe_*0_001_ctl',
        'ringToe_*0_002_ctl',
        'ringToe_*0_003_ctl',
        'ringToe_*0_004_ctl',
        'ringToe_*0_005_ctl',
        'pinkyBaseSub_*0_001_ctl',
        'pinkyBaseTweak_*0_001_ctl',
        'pinkyBaseTweak_*0_002_ctl',
        'pinkyBase_*0_001_ctl',
        'pinkyHandSub_*0_001_ctl',
        'pinkyHandTweak_*0_001_ctl',
        'pinkyHand_*0_001_ctl',
        'pinkyKnuckle_*0_001_ctl',
        'pinkyKnuckle_*0_002_ctl',
        'pinkyKnuckle_*0_003_ctl',
        'pinkyMidSub_*0_001_ctl',
        'pinkyMidTweak_*0_001_ctl',
        'pinkyMidTweak_*0_002_ctl',
        'pinkyMid_*0_001_ctl',
        'pinkyPalmSub_*0_001_ctl',
        'pinkyPalmTweak_*0_001_ctl',
        'pinkyPalm_*0_001_ctl',
        'pinkyTipSub_*0_001_ctl',
        'pinkyTipTweak_*0_001_ctl',
        'pinkyTipTweak_*0_002_ctl',
        'pinkyTip_*0_001_ctl',
        'pinkyToeKnuckle_*0_001_ctl',
        'pinkyToeKnuckle_*0_002_ctl',
        'pinkyToeKnuckle_*0_003_ctl',
        'pinkyToeKnuckle_*0_004_ctl',
        'pinkyToeKnuckle_*0_005_ctl',
        'pinkyToeSub_*0_001_ctl',
        'pinkyToeSub_*0_002_ctl',
        'pinkyToeSub_*0_003_ctl',
        'pinkyToeSub_*0_004_ctl',
        'pinkyToeSub_*0_005_ctl',
        'pinkyToeTweak_*0_001_ctl',
        'pinkyToeTweak_*0_002_ctl',
        'pinkyToeTweak_*0_003_ctl',
        'pinkyToeTweak_*0_004_ctl',
        'pinkyToeTweak_*0_005_ctl',
        'pinkyToeTweak_*0_006_ctl',
        'pinkyToeTweak_*0_007_ctl',
        'pinkyToeTweak_*0_008_ctl',
        'pinkyToeTweak_*0_009_ctl',
        'pinkyToe_*0_001_ctl',
        'pinkyToe_*0_002_ctl',
        'pinkyToe_*0_003_ctl',
        'pinkyToe_*0_004_ctl',
        'pinkyToe_*0_005_ctl']
        

        #sided list append into larger list
        for side_token in ['L', 'R']:
            for item in yzx_sided:
                yzx_item = item.replace("*", side_token)
                yzx_ordered.append(yzx_item)

        self.set_reveal_rotate_orders(yzx_ordered, 1)

        #zxy = 2
        #centered
        zxy_ordered = ['spineFkSub_C0_001_ctl',
        'spineFkSub_C0_002_ctl',
        'spineFk_C0_001_ctl',
        'spineFk_C0_002_ctl',
        'spineIkSub_C0_001_ctl',
        'spineIkSub_C0_002_ctl',
        'spineIkSub_C0_003_ctl',
        'spineIkSub_C0_004_ctl',
        'spineIkSub_C0_005_ctl',
        'spineIk_C0_001_ctl',
        'spineIk_C0_002_ctl',
        'spineIk_C0_003_ctl',
        'spineIk_C0_004_ctl',
        'spineIk_C0_005_ctl',
        'loSpineTweak_C0_001_ctl',
        'loSpineTweak_C0_002_ctl',
        'loSpineTweak_C0_003_ctl',
        'midSpineTweak_C0_001_ctl',
        'upSpineTweak_C0_001_ctl',
        'upSpineTweak_C0_002_ctl',
        'chestFkSub_C0_001_ctl',
        'chestFk_C0_001_ctl',
        'neckBend_C0_001_ctl',
        'neckBend_C0_002_ctl',
        'neckBend_C0_003_ctl',
        'neckBend_C0_004_ctl',
        'neckBend_C0_005_ctl',
        'neckFkSub_C0_001_ctl',
        'neckFkSub_C0_002_ctl',
        'neckFk_C0_001_ctl',
        'neckFk_C0_002_ctl',
        'neckTweak_C0_001_ctl',
        'neckTweak_C0_002_ctl',
        'neckTweak_C0_003_ctl',
        'neckTweak_C0_004_ctl',
        'headSub_C0_001_ctl',
        'headTweak_C0_001_ctl',
        'head_C0_001_ctl'] 
        
        zxy_sided = ['handIk_*0_001_ctl',
        'handIkSub_*0_001_ctl',
        'footIk_*0_001_ctl',
        'footIkSub_*0_001_ctl']
        
        #sided list append into larger list
        for side_token in ['L', 'R']:
            for item in zxy_sided:
                zxy_item = item.replace("*", side_token)
                zxy_ordered.append(zxy_item)

        self.set_reveal_rotate_orders(zxy_ordered, 2)


        #zyx = 5
        #centered
        zyx_ordered = []
        
        zyx_sided = ['armIk_*0_001_ctl', 
        'armIkSub_*0_001_ctl',
        'elbowFk_*0_001_ctl', 
        'elbowFkSub_*0_001_ctl',
        'kneeFkSub_*0_001_ctl',
        'kneeFk_*0_001_ctl',
        'legFkSub_*0_005_ctl',
        'legFk_*0_005_ctl',
        'ankleFkSub_*0_001_ctl',
        'ankleFk_*0_001_ctl',
        'hipFkSub_*0_001_ctl',
        'hipFk_*0_001_ctl']
        
        #sided list append into larger list
        for side_token in ['L', 'R']:
            for item in zyx_sided:
                zyx_item = item.replace("*", side_token)
                zyx_ordered.append(zyx_item)

        self.set_reveal_rotate_orders(zyx_ordered, 5)

        print "Rotate orders set"

    def misc_cleanup():
        print('[[[ running scene housecleaning module ]]]')

        # Remove unused objects

        # Find the assembly root group, if it exists, parent the rig under it
        assembly_search = cmds.ls("*assembly")
        if len(assembly_search)>0:
            assembly_root_group = assembly_search[0]
            try:
                cmds.parent('rig_grp', assembly_root_group)
            except:
                pass

        # Set Default Attributes 
        #set ik space switch to god sub:
        ik_controls = ['handIk_L0_001_ctl', 'handIk_R0_001_ctl','footIk_L0_001_ctl', 'footIk_R0_001_ctl']
        for ik_control in ik_controls:
            if cmds.objExists(ik_control+".spaceSwitch"):
                try:
                    cmds.setAttr(ik_control+".spaceSwitch", 3)
                except:
                    pass
            # Visibility, 
            # Space-switching

        #visibility cleanups
        try:
            cmds.setAttr("bodyComponent_grp.jnt_vis", 0)
            cmds.setAttr("bodyGuide_grp.visibility", 0)
        except:
            pass

        try:
            pm.delete("global_C0_ctl")
        except:
            pass
        try:
            pm.hide("TEMP_hold_weights")
        except:
            pass
                
        print('[[[ scene housecleaning complete ]]]')

        print('----- BUILD COMPLETE -----')

    # ui functions
    def load_face_geo(self, text=None):
        if not text:
            text = cmds.ls(sl=True)[0]
            self.face_geo_name.setText(text)
        else:
            self.face_geo_name.setText(text)

        if text:
            obj = pm.PyNode(text)
            skin = self.get_skin_cluster(obj)
            if skin:
                if pm.listConnections(skin.bindPreMatrix):
                    self.create_face_hlp_joints_button.setDisabled(True)
                else:
                    self.create_face_hlp_joints_button.setDisabled(False)
            else:
                self.create_face_hlp_joints_button.setDisabled(False)
                
    def load_body_geo(self, text=None):
        if not text:
            sel = cmds.ls(sl=True)[0]
            self.body_geo_name.setText(sel)
        else:
            self.body_geo_name.setText(text)

    def import_face_rig(self):
        file_path = cmds.fileDialog2(fm=1)
        if file_path:
            cmds.file(file_path[0], i=True, ignoreVersion=True, ns=self.face_namespace, type='mayaAscii')

        self.delete_face_display_layers()
        self.hide_face_objects()

        if pm.objExists(self.face_namespace+":geo_body_000"):
            self.load_face_geo(text=self.face_namespace+":geo_body_000")
    
    def import_body_rig(self):
        file_path = cmds.fileDialog2(fm=1)[0]
        if file_path:
            cmds.file(file_path, i=True, ignoreVersion=True, ns=self.body_namespace, type='mayaAscii')

        self.transfer_shader_sets()

        if pm.objExists(self.body_namespace+":geo_body_000"):
            self.load_body_geo(text=self.body_namespace+":geo_body_000")
        else:
            print "couldn't find face rig body geo"

    def create_face_hlp_joints(self):
        face_body_geo = pm.PyNode(self.face_geo_name.text())
        skin = self.get_skin_cluster(face_body_geo)

        try:
            print "Creating hlp joints and attaching bindPreMatrix..."

            self.bpm_grp = pm.group(name="face_bindPreMatrix_grp", empty=True)
            pm.parent(self.bpm_grp, self.face_namespace+":rig_face")
            pm.hide(self.bpm_grp)

            # create a duplicate joint and connect it to the preBindMatrix to counter body head movement
            for jnt in skin.influenceObjects():
                if "TEMP" not in str(jnt):
                    # duplicate joint
                    hlp = pm.duplicate(jnt, name=jnt.replace("_jnt", "_hlp").replace("_def", "_hlp"), parentOnly=True)[0]
                    pm.parent(hlp, self.bpm_grp)
                    
                    # only want to get the skins that will be merged
                    skins_connected = [skin]
                    
                    for s in skins_connected:
                        # get index of joint in skin cluster
                        connections = pm.listConnections(jnt.worldMatrix, d=True, source=False, plugs=True)
                        for con in connections:
                            if str(s) in str(con):
                                index = con.index()
                        
                        # attach hlp joint to index of preBindMatrix
                        pm.connectAttr(hlp.worldInverseMatrix[0], s.node().bindPreMatrix[index], f=True)

            self.create_face_hlp_joints_button.setDisabled(True)

        except:
            raise

    def combine_rigs(self):
        
        self.constrain_face_rig()
        self.perform_skin_merge()
        self.replace_body_geo()

        pm.delete(self.face_namespace+":*assembly")

        self.remove_namespaces()

        try:
            self.add_eye_lookat_space()
        except:
            pm.warning("Couldn't add eye lookat space switch. Naming or something must be off.")
        
        self.set_default_attrs()
        self.set_rotate_orders()
        self.misc_cleanup()
    


    # Delete any instances of this class
    def deleteInstances(self):
        if cmds.workspaceControl(self.__class__.toolName+'WorkspaceControl', exists=True, q=True) == True:
            cmds.deleteUI(self.__class__.toolName+'WorkspaceControl', control=True)

    # Show window with docking ability
    def run(self):
        self.show(dockable = True)

class AddListWidget(QtWidgets.QListWidget):

    def __init__(self, parent=None, namespace=None, init_items=None):
        QtWidgets.QListWidget.__init__(self, parent)

        self.list_widget = QtWidgets.QListWidget()
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.namespace = namespace

        self.init_items(init_items)

        self.line = QtWidgets.QLineEdit()
        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        self.add_button.clicked.connect(self.add_item)
        self.remove_button.clicked.connect(self.remove_item)

        self.layout.addWidget(self.list_widget, 0, 0, 1, 0)
        self.layout.addWidget(self.line, 1, 0, 1, 0)
        self.layout.addWidget(self.add_button, 2, 0)
        self.layout.addWidget(self.remove_button, 2, 1)
    
    def init_items(self, items):
        if self.namespace:
            if items:
                objs = [self.namespace+":"+x for x in items]
            else:
                objs = None
        else:
            objs = items
        if objs:
            for obj in objs:
                self.list_widget.addItem(obj)

    def add_item(self):
        if self.namespace:
            obj = self.namespace+":"+self.line.text()
        else:
            obj = self.line.text()
        self.list_widget.addItem(obj) 
        self.line.clear()

    def remove_item(self):
        current = self.list_widget.currentRow()
        self.list_widget.takeItem(current) 

    def get_items(self):
        item_list = []
        for x in range(self.list_widget.count()):
            item_list.append(self.list_widget.item(x).text())

        return item_list

class RemoveListWidget(QtWidgets.QListWidget):

    def __init__(self, parent=None, namespace=None, init_items=None):
        QtWidgets.QListWidget.__init__(self, parent)

        self.list_widget = QtWidgets.QListWidget()
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.namespace = namespace

        self.init_items(init_items)

        self.remove_button = QtWidgets.QPushButton("Remove")

        self.remove_button.clicked.connect(self.remove_item)

        self.layout.addWidget(self.list_widget, 0, 0, 1, 0)
        self.layout.addWidget(self.remove_button, 1, 0)
    
    def init_items(self, items):
        if self.namespace:
            if items:
                objs = [self.namespace+":"+x for x in items]
            else:
                objs = None
        else:
            objs = items
        if objs:
            for obj in objs:
                self.list_widget.addItem(obj)

    def remove_item(self):
        current = self.list_widget.currentRow()
        current_text = self.list_widget.item(current).text()
        if cmds.objExists(current_text):
            try:
                cmds.delete(current_text)
                self.list_widget.takeItem(current) 
            except:
                raise
    
    def get_items(self):
        item_list = []
        for x in range(self.list_widget.count()):
            item_list.append(self.list_widget.item(x).text())

        return item_list

    def refresh(self):
        self.list_widget.clear()
        self.init_items(items)