from shiboken2 import wrapInstance
from PySide2 import QtGui, QtCore, QtWidgets
from maya import OpenMayaUI as OpenMayaUI
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil
import pymel.core as pm

from mirror_tools import xform_mirror
reload(xform_mirror)
class MirrorWindow(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    toolName = "Mirmir Mirror"
    toolVersion = "1.0.0"
    info = "Mirmir: God in Greek mythology; Very knowledgable in all things in this universe. \nForced to use his knowledge to mirror objects for the riggers by Justin."

    red = "rgba(250, 0, 0, 250)"
    dark_red = "rgba(150, 0, 0, 250)"
    green = "rgba(0, 250, 0, 250)"
    dark_green = "rgba(0, 150, 0, 250)"
    yellow = "rgba(0, 0, 250, 250)"
    dark_yellow = "rgba(0, 0, 150, 250)"
    white = "rgba(250, 250, 250, 250)"

    darkRed_background_color = "{ background-color: %s; color: %s }" %(dark_red, white)
    darkGreen_background_color = "{ background-color: %s; color: %s }" %(dark_green, white)

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

        # Create a button and stuff it in a layout
        axis_list = ["xy", "yz", "xz"]
        self.axis_label = QtWidgets.QLabel("Axis:")
        self.xform_axis = QtWidgets.QComboBox()
        self.xform_axis.addItems(axis_list)

        self.xform_behaviour = QtWidgets.QCheckBox("Mirror Behaviour")

        self.xform_mirror_selected_button = QtWidgets.QPushButton('Xform Mirror Selected')
        self.xform_mirror_opposite_button = QtWidgets.QPushButton('Xform Mirror Opposite')
        self.symmetrical_mirror_selected_button = QtWidgets.QPushButton('Symmetrical Mirror Selected')
        self.symmetrical_mirror_opposite_button = QtWidgets.QPushButton('Symmetrical Mirror Opposite')

        self.xform_mirror_selected_button.clicked.connect(self.xform_mirror_selected)
        self.xform_mirror_opposite_button.clicked.connect(self.xform_mirror_opposite)
        self.symmetrical_mirror_selected_button.clicked.connect(self.symmetrical_mirror_selected)
        self.symmetrical_mirror_opposite_button.clicked.connect(self.symmetrical_mirror_opposite)

        ##################################################
        # Create the layout 
        ##################################################

        self.main_layout = QtWidgets.QVBoxLayout()
        self.option_layout = QtWidgets.QGridLayout()
        self.button_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.option_layout)
        self.main_layout.addLayout(self.button_layout)

        self.option_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.option_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.option_layout.setColumnStretch(2, 20)

        self.option_layout.addWidget(self.axis_label, 0, 0)
        self.option_layout.addWidget(self.xform_axis, 0, 1)
        self.option_layout.addWidget(self.xform_behaviour, 0, 2)

        self.button_layout.addWidget(self.xform_mirror_selected_button)
        self.button_layout.addWidget(self.xform_mirror_opposite_button)
        self.button_layout.addWidget(self.symmetrical_mirror_selected_button)
        self.button_layout.addWidget(self.symmetrical_mirror_opposite_button)

        self.setLayout(self.main_layout)

    
    def xform_mirror_selected(self):
        transforms_dict = xform_mirror.get_mirror_transform(axis=self.xform_axis.currentText(), 
                                                            behaviour=self.xform_behaviour.isChecked())
        xform_mirror.mirror(transforms_dict)

    def xform_mirror_opposite(self):
        transforms_dict = xform_mirror.get_mirror_transform(axis=self.xform_axis.currentText(), 
                                                            behaviour=self.xform_behaviour.isChecked(),
                                                            opposite=True)
        xform_mirror.mirror(transforms_dict)
    
    def symmetrical_mirror_selected(self):
        transforms_dict = xform_mirror.get_symmetrical_transform(axis=self.xform_axis.currentText())
        xform_mirror.mirror(transforms_dict)

    def symmetrical_mirror_opposite(self):
        transforms_dict = xform_mirror.get_symmetrical_transform(axis=self.xform_axis.currentText(),
                                                            opposite=True)
        xform_mirror.mirror(transforms_dict)


    # If it's floating or docked, this will run and delete it self when it closes.
    # You can choose not to delete it here so that you can still re-open it through the right-click menu, but do disable any callbacks/timers that will eat memory
    def dockCloseEventTriggered(self):
        self.deleteInstances()

    # Delete any instances of this class
    def deleteInstances(self):
        if pm.workspaceControl(self.__class__.toolName+'WorkspaceControl', exists=True, q=True) == True:
            pm.deleteUI(self.__class__.toolName+'WorkspaceControl', control=True)

    # Show window with docking ability
    def run(self):
        self.show(dockable = True)
