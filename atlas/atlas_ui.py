# gui imports
from shiboken2 import wrapInstance
from PySide2 import QtGui, QtCore, QtWidgets
# maya imports
from maya import OpenMayaUI as OpenMayaUI
import pymel.core as pm
import pymel.util as pmutil
import maya.cmds as cmds
from maya import mel
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil
# system imports
import os
import sys
import subprocess
import datetime
# mgear imports
import mgear.shifter.io as io
import mgear.core.skin as skin
# rigging imports
import atlas_utils
reload(atlas_utils)
# Tangent Imports
from coreops.utilities import am_utils as coreutils



# This gets the list of assets published from the ta_coreops_usd package
print ("Configuring assets list...")
assets_list = coreutils.get_published_component_names_list()
print ("Asset list configured.")

# rigging environment variables
manifest_lib_path = os.environ["RIG_MANIFEST_LIBRARY_PATH"]
code_lib_path = os.environ["RIG_CODE_LIBRARY_PATH"]
current_project = os.environ["PROJECT_CODE"]
current_user = os.environ["USERNAME"]
if not os.getenv("USER_MANIFEST_PROJECT"):
    os.environ["USER_MANIFEST_PROJECT"] = ""
if not os.getenv("LIB_MANIFEST_PROJECT"):
    os.environ["LIB_MANIFEST_PROJECT"] = ""
if not os.getenv("ATLAS_ASSET"):
    os.environ["ATLAS_ASSET"] = ""

class AtlasWindow(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    toolName = "Atlas"
    toolVersion = "0.0.6"
    info = "Atlas: God in Greek mythology; Forced to carry the heavens on his shoulders by Zeus. Now forced to carry the rigging department's manifest by Justin."

    red = "rgba(250, 0, 0, 250)"
    dark_red = "rgba(150, 0, 0, 250)"
    green = "rgba(0, 250, 0, 250)"
    dark_green = "rgba(0, 150, 0, 250)"
    yellow = "rgba(0, 0, 250, 250)"
    dark_yellow = "rgba(0, 0, 150, 250)"
    white = "rgba(250, 250, 250, 250)"

    darkRed_background_color = "{ background-color: %s; color: %s }" %(dark_red, white)
    darkGreen_background_color = "{ background-color: %s; color: %s }" %(dark_green, white)

    def __init__(self, parent=None):
        # delete self first
        self.deleteInstances()

        super(self.__class__, self).__init__(parent = parent)
        mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow() 
        self.mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtWidgets.QMainWindow)
        self.setObjectName(self.__class__.toolName) # Make this unique enough if using it to clear previous instance!

        # Setup window's properties
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(self.toolName+' '+self.toolVersion)
        self.resize(400, 200)

        # Create tab widgets
        self.tab_bar = QtWidgets.QTabWidget(self)
        self.settings_tab = QtWidgets.QWidget()
        self.data_tab = QtWidgets.QWidget()
        self.tab_bar.addTab(self.settings_tab, 'Settings')
        self.tab_bar.addTab(self.data_tab, 'Data')

        self.current_data_type = ""

        #######################################################################
        # Create main layout and align the tabs to the top
        #######################################################################
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_layout.addWidget(self.tab_bar)
        #self.main_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)

        #######################################################################
        # Create settings layout and align the tabs to the top
        #######################################################################
        self.settings_tab_layout = QtWidgets.QGridLayout()
        self.settings_tab_layout.setAlignment(QtCore.Qt.AlignTop)

        # Add settings widgets
        self.asset_label = QtWidgets.QLabel("Asset:")
        self.asset_combo_box = QtWidgets.QComboBox()
        self.asset_combo_box.addItems(assets_list)
        self.init_asset_button = QtWidgets.QPushButton("Initialize Asset")
        self.user_project_label = QtWidgets.QLabel("User Project Path:\n\n%s/%s/%s/%s\n" %(manifest_lib_path, 
                                                                                                current_project, 
                                                                                                self.asset_combo_box.currentText(), 
                                                                                                current_user))
        self.user_project_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.lib_project_label = QtWidgets.QLabel("Lib Project Path:\n\n%s/%s/%s/%s\n" %(manifest_lib_path, 
                                                                                                current_project, 
                                                                                                self.asset_combo_box.currentText(), 
                                                                                                "lib"))
        self.lib_project_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.init_label = QtWidgets.QLabel("Asset Currently Initialized:\n\n%s\n" %os.getenv("ATLAS_ASSET"))
        if os.environ["ATLAS_ASSET"]:
            self.init_label.setStyleSheet("QLabel { color: %s }" %self.green)
        else:
            self.init_label.setStyleSheet("QLabel { color: %s }" %self.red)
        self.init_label.setAlignment(QtCore.Qt.Alignment(QtCore.Qt.AlignRight))

        # add signals to settings widgets
        self.asset_combo_box.currentIndexChanged.connect(self.asset_changed)
        self.init_asset_button.clicked.connect(self.init_asset)

        # add setting widgets to layout
        self.settings_tab_layout.addWidget(self.user_project_label, 0, 0, 1, 0)
        self.settings_tab_layout.addWidget(self.lib_project_label, 1, 0, 1, 0)
        self.settings_tab_layout.addWidget(self.init_label, 2, 0, 1, 0)
        self.settings_tab_layout.addWidget(self.asset_label, 3, 0)
        self.settings_tab_layout.addWidget(self.asset_combo_box, 3, 1, 1, 1)
        self.settings_tab_layout.addWidget(self.init_asset_button, 4, 0, 1, 2)

        #######################################################################
        # Create data layout and align the tabs to the top
        #######################################################################
        self.data_tab_layout = QtWidgets.QGridLayout()
        self.data_tab_layout.setAlignment(QtCore.Qt.AlignTop)
        #self.data_tab_layout.setRowStretch(0, 100)
        #self.data_tab_layout.setRowStretch(1, 100)
        #self.data_tab_layout.setRowStretch(2, 1)
        #self.data_tab_layout.setRowStretch(3, 1)
        #self.data_tab_layout.setRowStretch(4, 1)
        #self.data_tab_layout.setRowStretch(5, 1)
        #self.data_tab_layout.setRowStretch(6, 1)

        # sublayouts depending on which list selection is made
        self.scenes_widget = QtWidgets.QWidget()
        self.template_build_widget = QtWidgets.QWidget()
        self.control_cvs_widget = QtWidgets.QWidget()
        self.skin_weights_widget = QtWidgets.QWidget()
        self.deformer_weights_widget = QtWidgets.QWidget()
        self.model_widget = QtWidgets.QWidget()
        self.blendshapes_widget = QtWidgets.QWidget()
        self.notes_widget = QtWidgets.QWidget()
        self.scenes_layout = QtWidgets.QGridLayout(self.scenes_widget)
        self.template_build_layout = QtWidgets.QGridLayout(self.template_build_widget)
        self.control_cvs_layout = QtWidgets.QGridLayout(self.control_cvs_widget)
        self.skin_weights_layout = QtWidgets.QGridLayout(self.skin_weights_widget)
        self.deformer_weights_layout = QtWidgets.QGridLayout(self.deformer_weights_widget)
        self.model_layout = QtWidgets.QGridLayout(self.model_widget)
        self.blendshapes_layout = QtWidgets.QGridLayout(self.blendshapes_widget)
        self.notes_layout = QtWidgets.QGridLayout(self.notes_widget)

        # create the scenes widgets --------------------------------------------
        self.save_scene_button = QtWidgets.QPushButton("Save Maya Scene")
        self.load_scene_button = QtWidgets.QPushButton("Load Maya Scene")
        self.publish_scene_button = QtWidgets.QPushButton("Publish Maya Scene")
        # add the widgets to the layout
        self.scenes_layout.addWidget(self.save_scene_button)
        self.scenes_layout.addWidget(self.load_scene_button)
        self.scenes_layout.addWidget(self.publish_scene_button)
        # signal for the widgets
        self.save_scene_button.clicked.connect(lambda env_type="user": self.save_maya_scene(env_type="user"))
        self.load_scene_button.clicked.connect(self.load_maya_scene)
        self.publish_scene_button.clicked.connect(lambda env_type="lib": self.save_maya_scene(env_type="lib"))

        # create the template_build widgets --------------------------------------------
        self.export_guide_template_button = QtWidgets.QPushButton("Export Guide Template")
        self.import_guide_template_button = QtWidgets.QPushButton("Import Guide Template")
        self.publish_guide_template_button = QtWidgets.QPushButton("Publish Guide Template")
        # add the widgets to the layout
        self.template_build_layout.addWidget(self.export_guide_template_button)
        self.template_build_layout.addWidget(self.import_guide_template_button)
        self.template_build_layout.addWidget(self.publish_guide_template_button)
        # signal for the widgets
        self.export_guide_template_button.clicked.connect(lambda env_type="user": self.export_guide_template(env_type="user"))
        self.import_guide_template_button.clicked.connect(self.import_guide_template)
        self.publish_guide_template_button.clicked.connect(lambda env_type="lib": self.export_guide_template(env_type="lib"))

        # create the control_cvs widgets --------------------------------------------
        self.save_control_cvs_button = QtWidgets.QPushButton("Save Control CVs")
        self.load_control_cvs_button = QtWidgets.QPushButton("Load Control CVs")
        self.publish_control_cvs_button = QtWidgets.QPushButton("Publish Control CVs")
        # add the widgets to the layout
        self.control_cvs_layout.addWidget(self.save_control_cvs_button)
        self.control_cvs_layout.addWidget(self.load_control_cvs_button)
        self.control_cvs_layout.addWidget(self.publish_control_cvs_button)
        # signal for the widgets
        self.save_control_cvs_button.clicked.connect(lambda env_type="user": self.save_control_cvs(env_type="user"))
        self.load_control_cvs_button.clicked.connect(self.load_control_cvs)
        self.publish_control_cvs_button.clicked.connect(lambda env_type="lib": self.save_control_cvs(env_type="lib"))

        # create the skin_weights widgets --------------------------------------------
        self.save_skin_weights_button = QtWidgets.QPushButton("Save Skin Weights")
        self.load_skin_weights_button = QtWidgets.QPushButton("Load Skin Weights")
        self.publish_skin_weights_button = QtWidgets.QPushButton("Publish Skin Weights")
        # add the widgets to the layout
        self.skin_weights_layout.addWidget(self.save_skin_weights_button)
        self.skin_weights_layout.addWidget(self.load_skin_weights_button)
        self.skin_weights_layout.addWidget(self.publish_skin_weights_button)
        # signal for the widgets
        self.save_skin_weights_button.clicked.connect(lambda env_type="user": self.save_skin_weights(env_type="user"))
        self.load_skin_weights_button.clicked.connect(self.load_skin_weights)
        self.publish_skin_weights_button.clicked.connect(lambda env_type="lib": self.save_skin_weights(env_type="lib"))


        # create the deformer_weights widgets --------------------------------------------
        self.save_deformer_weights_button = QtWidgets.QPushButton("Save Deformer Weights")
        self.load_deformer_weights_button = QtWidgets.QPushButton("Load Deformer Weights")
        self.publish_deformer_weights_button = QtWidgets.QPushButton("Publish Deformer Weights")
        # add the widgets to the layout
        self.deformer_weights_layout.addWidget(self.save_deformer_weights_button)
        self.deformer_weights_layout.addWidget(self.load_deformer_weights_button)
        self.deformer_weights_layout.addWidget(self.publish_deformer_weights_button)
        # signal for the widgets
        self.save_deformer_weights_button.clicked.connect(lambda env_type="user": self.save_deformer_weights(env_type="user"))
        self.load_deformer_weights_button.clicked.connect(self.load_deformer_weights)
        self.publish_deformer_weights_button.clicked.connect(lambda env_type="lib": self.save_deformer_weights(env_type="lib"))


        # create the blendshapes widgets --------------------------------------------
        self.export_blendshapes_button = QtWidgets.QPushButton("Export Blendshapes")
        self.import_blendshapes_button = QtWidgets.QPushButton("Import Blendshapes")
        self.publish_blendshapes_button = QtWidgets.QPushButton("Publish Blendshapes")
        # add the widgets to the layout
        self.blendshapes_layout.addWidget(self.export_blendshapes_button)
        self.blendshapes_layout.addWidget(self.import_blendshapes_button)
        self.blendshapes_layout.addWidget(self.publish_blendshapes_button)
        # signal for the widgets
        self.export_blendshapes_button.clicked.connect(lambda env_type="user": self.export_blendshapes(env_type="user"))
        self.import_blendshapes_button.clicked.connect(self.import_blendshapes)
        self.publish_blendshapes_button.clicked.connect(lambda env_type="lib": self.export_blendshapes(env_type="lib"))


        # create the skin_weights widgets --------------------------------------------
        self.notes_message_box = QtWidgets.QTextEdit()
        self.notes_message_box.setText("")
        self.notes_message_box.setReadOnly(True)
        self.notes_message_box.resize(200, 25)
        self.notes_layout.addWidget(self.notes_message_box)
        

        # create a list view to select which data type to load/save 
        self.data_list_view = QtWidgets.QListWidget()
        list_items = ["maya_scene", "guide_template", "control_cvs", "skin_weights", "deformer_weights", "blendshapes", "model", "structure"]
        for i in list_items:
            self.data_list_view.addItem(i)
            self.data_list_view.item(list_items.index(i)).setSizeHint(QtCore.QSize(10, 30))
        self.data_tab_layout.addWidget(self.data_list_view)
        self.data_list_view.currentItemChanged.connect(self.data_list_change)
    
        # create a list view for a file browser 
        self.file_list_tree = QtWidgets.QTreeWidget()
        self.file_list_tree.setColumnCount(3)
        items = ["Version", "User", "Date"]
        self.file_list_tree.setHeaderLabels(items)
        self.data_tab_layout.addWidget(self.file_list_tree)
        self.file_list_tree.currentItemChanged.connect(self.update_notes_message)

        #######################################################################
        # set layouts to window
        #######################################################################
        # Set the main layout to the window
        self.setLayout(self.main_layout)
        self.settings_tab.setLayout(self.settings_tab_layout) 
        self.data_tab.setLayout(self.data_tab_layout)

        # add widgets to the data tab layout
        self.data_tab_layout.addWidget(self.scenes_widget)
        self.data_tab_layout.addWidget(self.template_build_widget)
        self.data_tab_layout.addWidget(self.control_cvs_widget)
        self.data_tab_layout.addWidget(self.skin_weights_widget)
        self.data_tab_layout.addWidget(self.deformer_weights_widget)
        self.data_tab_layout.addWidget(self.model_widget)
        self.data_tab_layout.addWidget(self.blendshapes_widget)
        self.data_tab_layout.addWidget(self.notes_widget)

        # set default state of widgets
        self.scenes_widget.setVisible(False)
        self.template_build_widget.setVisible(False)
        self.control_cvs_widget.setVisible(False)
        self.skin_weights_widget.setVisible(False)
        self.deformer_weights_widget.setVisible(False)
        self.model_widget.setVisible(False)
        self.blendshapes_widget.setVisible(False)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress = 0
        self.data_tab_layout.addWidget(self.progress_bar)

        # sets the asset selection to what's already initialized
        if os.getenv("ATLAS_ASSET"):
            set_index = self.asset_combo_box.findText(os.getenv("ATLAS_ASSET"))
            self.asset_combo_box.setCurrentIndex(set_index)
            self.asset_changed()
    

    ###############################################################################
    #  UI updates
    ###############################################################################

    def reset_progress(self):
        self.progress = 0
        self.progress_bar.reset()

    def update_file_list(self):
        self.file_list_tree.clear()

        # add all lib files to list view according to the selected data type
        lib_asset_folder = os.environ["LIB_MANIFEST_PROJECT"]
        if lib_asset_folder:
            lib_data_folder = "%s/atlas/%s" %(lib_asset_folder, self.data_list_view.currentItem().text())
            for item in self.list_directory(lib_data_folder):
                # get the time stamp
                date = os.path.getmtime(lib_data_folder+"/"+item)
                time = datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M')

                # assign the text to the file list view
                tree_item = QtWidgets.QTreeWidgetItem(item)
                tree_item.setText(0, item)
                tree_item.setText(1, "lib")
                tree_item.setText(2, str(time))

                self.file_list_tree.addTopLevelItem(tree_item)

        # add all user files to list view according to the selected data type
        user_asset_folder = os.environ["USER_MANIFEST_PROJECT"]
        if user_asset_folder:
            user_data_folder = "%s/atlas/%s" %(user_asset_folder, self.data_list_view.currentItem().text())
            for item in self.list_directory(user_data_folder):
                # get the time stamp
                date = os.path.getmtime(user_data_folder+"/"+item)
                time = datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M')

                # assign the text to the file list view
                tree_item = QtWidgets.QTreeWidgetItem(item)
                tree_item.setText(0, item)
                tree_item.setText(1, current_user)
                tree_item.setText(2, str(time))

                self.file_list_tree.addTopLevelItem(tree_item)
        
    def data_list_change(self):
        # refresh the file list
        self.update_file_list()

        # hide all first and unhide specific ones after
        self.scenes_widget.setVisible(False)
        self.template_build_widget.setVisible(False)
        self.control_cvs_widget.setVisible(False)
        self.skin_weights_widget.setVisible(False)
        self.deformer_weights_widget.setVisible(False)
        self.model_widget.setVisible(False)
        self.blendshapes_widget.setVisible(False)

        # shows and hides widgets depending on which data type is selected
        if self.data_list_view.currentItem().text() == "maya_scene":
            self.scenes_widget.setVisible(True)
            self.current_data_type = "maya_scene"
        if self.data_list_view.currentItem().text() == "guide_template":
            self.template_build_widget.setVisible(True)
            self.current_data_type = "guide_template"
        if self.data_list_view.currentItem().text() == "control_cvs":
            self.control_cvs_widget.setVisible(True)
            self.current_data_type = "control_cvs"
        if self.data_list_view.currentItem().text() == "skin_weights":
            self.skin_weights_widget.setVisible(True)
            self.current_data_type = "skin_weights"
        if self.data_list_view.currentItem().text() == "deformer_weights":
            self.deformer_weights_widget.setVisible(True)
            self.current_data_type = "deformer_weights"
        if self.data_list_view.currentItem().text() == "model":
            self.model_widget.setVisible(True)
            self.current_data_type = "model"
        if self.data_list_view.currentItem().text() == "blendshapes":
            self.blendshapes_widget.setVisible(True)
            self.current_data_type = "blendshapes"
        
        # update the notes message
        self.update_notes_message()

    def update_notes_message(self):
        
        if self.file_list_tree.currentItem():
            version = self.file_list_tree.currentItem().text(0)
            user = self.file_list_tree.currentItem().text(1)

            if user == "lib":
                manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
            else:
                manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

            if manifest_lib:
                directory = manifest_lib+"/atlas/"+self.current_data_type+"/"+version
                notes = self.get_note_info(directory)
                self.notes_message_box.setText(notes)
            else:
                self.notes_message_box.setText("")
        else:
            self.notes_message_box.setText("")


    ###############################################################################
    #  asset initialize
    ###############################################################################

    def asset_changed(self):
        # change current project label text
        self.user_project_label.setText("User Project Path:\n\n%s/%s/%s/%s\n" %(manifest_lib_path, 
                                                                                    current_project, 
                                                                                    self.asset_combo_box.currentText(), 
                                                                                    current_user))
        self.lib_project_label.setText("Lib Project Path:\n\n%s/%s/%s/%s\n" %(manifest_lib_path, 
                                                                                    current_project, 
                                                                                    self.asset_combo_box.currentText(), 
                                                                                    "lib"))                                                                            

        # Check if user directory exists in project label
        # if it does, then set it as the current project and change init button to green
        user_project_path = "%s/%s/%s/%s" %(manifest_lib_path, current_project, self.asset_combo_box.currentText(), current_user)
        if os.path.exists(user_project_path):
            self.user_project_label.setStyleSheet("QLabel { color: %s }" %self.green)
            os.environ["USER_MANIFEST_PROJECT"] = "%s/%s/%s/%s" %(manifest_lib_path, current_project, self.asset_combo_box.currentText(), current_user)
        else:
            self.user_project_label.setStyleSheet("QLabel { color: %s }" %self.red)
        
        # turn the lib text green if path exists
        # set the env variable if the path exists, do nothing if it doesn't
        lib_project_path = "%s/%s/%s/%s" %(manifest_lib_path, current_project, self.asset_combo_box.currentText(), "lib")
        if os.path.exists(lib_project_path):
            self.lib_project_label.setStyleSheet("QLabel { color: %s }" %self.green)
            os.environ["LIB_MANIFEST_PROJECT"] = "%s/%s/%s/%s" %(manifest_lib_path, current_project, self.asset_combo_box.currentText(), "lib")
        else:
            self.lib_project_label.setStyleSheet("QLabel { color: %s }" %self.red)

    def init_asset(self):
        os.environ["USER_MANIFEST_PROJECT"] = "%s/%s/%s/%s" %(manifest_lib_path, current_project, self.asset_combo_box.currentText(), current_user)
        os.environ["LIB_MANIFEST_PROJECT"] = "%s/%s/%s/%s" %(manifest_lib_path, current_project, self.asset_combo_box.currentText(), "lib")
        atlas_utils.build_asset_directory(os.environ["USER_MANIFEST_PROJECT"])
        atlas_utils.build_asset_directory(os.environ["LIB_MANIFEST_PROJECT"])

        # this will refresh the colors of the paths
        current_index = self.asset_combo_box.currentIndex()
        self.asset_combo_box.setCurrentIndex(0)
        self.asset_combo_box.setCurrentIndex(current_index)

        # set the user's project
        atlas_utils.set_project(os.environ["USER_MANIFEST_PROJECT"]+"/maya")

        os.environ["ATLAS_ASSET"] = self.asset_combo_box.currentText()

        self.init_label.setStyleSheet("QLabel { color: %s }" %self.green)

        self.init_label.setText("Asset Currently Initialized:\n\n%s" %os.getenv("ATLAS_ASSET"))  


    ###############################################################################
    #  extras
    ###############################################################################

    def open_input_dialog(self):

        input_dialog = QtWidgets.QInputDialog()
        input_dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
        input_dialog.setLabelText("Notes:")
        input_dialog.setWindowTitle("Save/Publish Notes")
        input_dialog.resize(300, 200)

        ok = input_dialog.exec_()
        text = input_dialog.textValue()
        if ok:
            return text
        else:
            return None

    def get_note(self, directory):

        if os.path.exists(directory+"/notes.txt"):
            return str(directory)+"/notes.txt"
        else:
            return None

    def get_note_info(self, directory):
        
        if self.get_note(directory):
            return atlas_utils.load_json(self.get_note(directory))
        else:
            return None

    def set_note(self, directory, data):
        data = data+"\n\n- "+current_user
        return atlas_utils.save_json(directory, "notes.txt", data)

    def build_version_directory(self, path):
        # get the latest folder
        if not atlas_utils.get_latest_folder(path):
            latest_directory = path + "/latest"
            os.makedirs(latest_directory) 

        # create the next version directory
        next_version = atlas_utils.get_next_folder_version(path)
        next_version_directory = path + "/version_" + str(next_version).zfill(4)
        os.makedirs(next_version_directory) 

        return next_version_directory

    def list_directory(self, directory, include_notes=False):
        if include_notes:
            return os.listdir(directory)
        else:
            try:
                list_dir = os.listdir(directory)
                list_dir.remove("notes.txt")
                return list_dir
            except:
                return os.listdir(directory)
    
    def clean_directory(self, directory):
        for f in self.list_directory(directory):
            try:
                os.remove(directory+"/"+f)
            except:
                raise

    ###############################################################################
    #  maya scenes
    ###############################################################################

    def save_maya_scene(self, env_type="user"):
        
        if env_type == "lib":
            manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
        else:
            manifest_lib = os.environ["USER_MANIFEST_PROJECT"]
        
        # get project path
        version_export_folder = manifest_lib+"/atlas/maya_scene"
        latest_export_folder = manifest_lib+"/atlas/maya_scene/latest"
        latest_version_path = latest_export_folder + "/latest.ma"

        # create the next version directory
        next_version_directory = self.build_version_directory(version_export_folder) 
        next_version_path = next_version_directory + "/" + os.path.basename(next_version_directory) + ".ma"

        if os.environ["ATLAS_ASSET"]:
            # set the note data from user input to both locations
            note_data = self.open_input_dialog()
            self.set_note(next_version_directory, note_data)
            self.set_note(latest_export_folder, note_data)

            # save next version
            cmds.file(rename=next_version_path)
            cmds.file(save=True, type="mayaAscii")

            # update the file list widget
            self.update_file_list()

            # save latest
            cmds.file(rename=latest_version_path)
            cmds.file(save=True, type="mayaAscii")

            # update the file list widget
            self.update_file_list()

            print("+ File Saved:", str(next_version_path), str(latest_version_path))
        
        else:
            cmds.warning("You need to initialize an asset with Atlas before using this save method.")

    def load_maya_scene(self):

        try:
            version = self.file_list_tree.currentItem().text(0)
            user = self.file_list_tree.currentItem().text(1)

            # determine whether to pull from lib or from user
            if user == "lib":
                manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
            else:
                manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

            if manifest_lib:
                # get project path
                folder = manifest_lib+"/atlas/maya_scene/"+version
                for f in os.listdir(folder):
                    if f.endswith(".ma"):
                        load_file = str(folder)+"/"+str(f)

                cmds.file(load_file, open=True, force=True)

            else:
                pm.warning("You need to either initialize the current asset or change the asset to a directory you already have.")
        except:
            raise
    

    ###############################################################################
    #  guide templates
    ###############################################################################

    def export_guide_template(self, env_type="user"):
        
        if env_type == "lib":
            manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
        else:
            manifest_lib = os.environ["USER_MANIFEST_PROJECT"]
        
        # get project path
        version_export_folder = manifest_lib+"/atlas/guide_template"
        latest_export_folder = manifest_lib+"/atlas/guide_template/latest"
        latest_version_path = latest_export_folder + "/latest.sgt"

        # create the next version directory
        next_version_directory = self.build_version_directory(version_export_folder) 
        next_version_path = next_version_directory + "/" + os.path.basename(next_version_directory) + ".sgt"

        # set the note data from user input to both locations
        note_data = self.open_input_dialog()
        self.set_note(next_version_directory, note_data)
        self.set_note(latest_export_folder, note_data)

        # export version
        io.export_guide_template(filePath=next_version_path)

        # update the file list widget
        self.update_file_list()

        # export latest
        self.clean_directory(latest_export_folder)
        io.export_guide_template(filePath=latest_version_path)

        # update the file list widget
        self.update_file_list()

        print("+ Exported guide template to:", str(next_version_path), str(latest_version_path))

    def import_guide_template(self):

        try:
            version = self.file_list_tree.currentItem().text(0)
            user = self.file_list_tree.currentItem().text(1)

            # determine whether to pull from lib or from user
            if user == "lib":
                manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
            else:
                manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

            if manifest_lib:
                # get project path
                import_folder = manifest_lib+"/atlas/guide_template/"+version
                for f in os.listdir(import_folder):
                    if f.endswith(".sgt"):
                        import_file = str(import_folder)+"/"+str(f)

                io.import_guide_template(filePath=import_file)

            else:
                pm.warning("You need to either initialize the current asset or change the asset to a directory you already have.")
        except:
            raise
    

    ###############################################################################
    #  control curves
    ###############################################################################

    def export_curves(self, curves, export_folder):
        
        # set the progress for the progress bar
        try:
            x = 100.0 / (float(len(curves)) * 2)
        except:
            x = 100.0 / 100.0

        for curve in curves:
            try:
                atlas_utils.export_curve(curve, export_folder)
            except:
                pm.warning("Something went wrong with curve: "+curve)

            # set the current progress
            self.progress = self.progress + x
            self.progress_bar.setValue(self.progress)
            QtWidgets.QApplication.processEvents()

    def import_curves(self, curves, import_folder):

        # set the progress for the progress bar
        try:
            x = 100.0 / float(len(curves))
        except:
            x = 100.0 / 100.0
        progress = 0

        for curve in curves:
            try:
                atlas_utils.import_curve(curve, import_folder)
            except:
                pm.warning("Error with curve file for control:", curve)

            # set the current progress
            progress = progress + x
            self.progress_bar.setValue(progress)
            QtWidgets.QApplication.processEvents()

    def save_control_cvs(self, env_type="user"):
        if env_type == "lib":
            manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
        else:
            manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

        if manifest_lib:
            # get project path
            version_export_folder = manifest_lib+"/atlas/control_cvs"
            latest_export_folder = manifest_lib+"/atlas/control_cvs/latest"

            # create the next version directory
            next_version_directory = self.build_version_directory(version_export_folder) 

            # set the note data from user input to both locations
            note_data = self.open_input_dialog()
            self.set_note(next_version_directory, note_data)
            self.set_note(latest_export_folder, note_data)

            # save new version
            curves = pm.ls("*_ctl")
            self.export_curves(curves, next_version_directory)

            # update the file list widget
            self.update_file_list()

            # save to latest
            curves = pm.ls("*_ctl")
            self.clean_directory(latest_export_folder)
            self.export_curves(curves, latest_export_folder)

            # update the file list widget
            self.update_file_list()

            # reset the progress bar
            self.reset_progress()

            print("+ Saved control cv's to:", str(version_export_folder), str(latest_export_folder))

        else:
            pm.warning("You need to either initialize the current asset or change the asset to a directory you already have.")
    
    def load_control_cvs(self):

        try:
            version = self.file_list_tree.currentItem().text(0)
            user = self.file_list_tree.currentItem().text(1)

            # determine whether to pull from lib or from user
            if user == "lib":
                manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
            else:
                manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

            if manifest_lib:
                # get project path
                import_folder = manifest_lib+"/atlas/control_cvs/"+version

                curves = pm.ls("*_ctl")
                self.import_curves(curves, import_folder)
                self.progress_bar.reset()

                print("+ Loaded control cv's from", import_folder)

            else:
                pm.warning("You need to either initialize the current asset or change the asset to a directory you already have.")
        except:
            raise


    ###############################################################################
    #  skin weights
    ###############################################################################

    def export_skin_weights(self, objects, export_folder):

        # set the progress for the progress bar
        try:
            x = 100.0 / (float(len(objects)) * 2)
        except:
            x = 100.0 / 100.0

        for obj in objects:
            if isinstance(obj.getShapes(), list):
                for shape in obj.getShapes():
                    if pm.listConnections(shape, type="skinCluster"):
                        skin.exportSkin(export_folder+"/"+str(obj)+".jSkin", [obj])
            else:
                if pm.listConnections(obj.getShapes(), type="skinCluster"):
                    skin.exportSkin(export_folder+"/"+str(obj)+".jSkin", [obj])

            # set the current progress
            self.progress = self.progress + x
            self.progress_bar.setValue(self.progress)
            QtWidgets.QApplication.processEvents()

    def import_skin_weights(self, import_folder):

        # set the progress for the progress bar
        try:
            x = 100.0 / (float(len(self.list_directory(import_folder))))
        except:
            x = 100.0 / 100.0

        for f in self.list_directory(import_folder):
            try:
                skin.importSkin(import_folder+"/"+f)
            except:
                pm.warning("Could not load in skin pack from:", f)

            # set the current progress
            self.progress = self.progress + x
            self.progress_bar.setValue(self.progress)
            QtWidgets.QApplication.processEvents()

    def save_skin_weights(self, env_type="user"):

        if env_type == "lib":
            manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
        else:
            manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

        if manifest_lib:
            # get project path
            version_export_folder = manifest_lib+"/atlas/skin_weights"
            latest_export_folder = manifest_lib+"/atlas/skin_weights/latest"

            # create the next version directory
            next_version_directory = self.build_version_directory(version_export_folder)  

            # set the note data from user input to both locations
            note_data = self.open_input_dialog()
            self.set_note(next_version_directory, note_data)
            self.set_note(latest_export_folder, note_data)

            # save the skin weights as a skin pack in the next version
            objects = pm.ls("geo_grp", dag=True, type="transform")
            self.export_skin_weights(objects, next_version_directory)
            
            # update the file list widget
            self.update_file_list()

            # save the skin weights as a skin pack in the latest folder
            objects = pm.ls("geo_grp", dag=True, type="transform")
            self.clean_directory(latest_export_folder)
            self.export_skin_weights(objects, latest_export_folder)
            
            # update the file list widget
            self.update_file_list()

            # reset the progress bar
            self.reset_progress()

            print("+ Saved skin weights to:", str(version_export_folder), str(latest_export_folder))
        
        else:
            pm.warning("You need to either initialize the current asset or change the asset to a directory you already have.")
    
    def load_skin_weights(self):

        try:
            version = self.file_list_tree.currentItem().text(0)
            user = self.file_list_tree.currentItem().text(1)

            # determine whether to pull from lib or from user
            if user == "lib":
                manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
            else:
                manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

            if manifest_lib:
                # get project path
                import_folder = manifest_lib+"/atlas/skin_weights/"+version

                self.import_skin_weights(import_folder)
                self.progress_bar.reset()

            else:
                pm.warning("You need to either initialize the current asset or change the asset to a directory you already have.")
        except:
            raise
    

    ###############################################################################
    #  deformer weights
    ###############################################################################

    def export_deformer_weights(self, objects, export_folder):

        empty = []
        for obj in objects:
            for shape in obj.getShapes():
                try:
                    for deformer in pm.findDeformers(shape):
                        empty.append(deformer)
                except:
                    pass
        # set the progress for the progress bar
        try:
            x = 100.0 / (float(len(empty)) * 1)
        except:
            x = 100.0 / 100.0

        for obj in objects:
            for shape in obj.getShapes():
                try:
                    for deformer in pm.findDeformers(shape):
                        try:
                            if isinstance(pm.PyNode(deformer), pm.nodetypes.Ffd):
                                file_name = shape+"__"+deformer+"__ffd"+".json"
                                data = atlas_utils.get_deformer_weights(shape, deformer)
                                atlas_utils.save_json(export_folder, file_name, data)

                            elif isinstance(pm.PyNode(deformer), pm.nodetypes.Cluster):
                                file_name = shape+"__"+deformer+"__cluster"+".json"
                                data = atlas_utils.get_deformer_weights(shape, deformer)
                                atlas_utils.save_json(export_folder, file_name, data)
                        
                            elif isinstance(pm.PyNode(deformer), pm.nodetypes.DeltaMush):
                                file_name = shape+"__"+deformer+"__deltaMush"+".json"
                                data = atlas_utils.get_deformer_weights(shape, deformer)
                                atlas_utils.save_json(export_folder, file_name, data)

                            elif isinstance(pm.PyNode(deformer), pm.nodetypes.BlendShape):
                                file_name = shape+"__"+deformer+"__blendShape"+".json"
                                data = atlas_utils.get_blendshape_weights(shape, deformer)
                                atlas_utils.save_json(export_folder, file_name, data)
                        except:
                            raise

                except:
                    pass

            # set the current progress
            self.progress = self.progress + x
            self.progress_bar.setValue(self.progress)
            QtWidgets.QApplication.processEvents()

    def import_deformer_weights(self, import_folder):

        # set the progress for the progress bar
        try:
            x = 100.0 / (float(len(self.list_directory(import_folder))))
        except:
            x = 100.0 / 100.0

        for f in self.list_directory(import_folder):
            try:
                shape_name = f.split("__")[0]
                deformer_name = f.split("__")[1]
                deformer_type = f.split("__")[2].replace(".json", "")

                if deformer_type == "blendShape":
                    data = atlas_utils.load_json(import_folder+"/"+f)
                    atlas_utils.set_blendshape_weights(shape_name, deformer_name, data)    
                else:
                    data = atlas_utils.load_json(import_folder+"/"+f)
                    atlas_utils.set_deformer_weights(shape_name, deformer_name, data)
            except:
                raise

            # set the current progress
            self.progress = self.progress + x
            self.progress_bar.setValue(self.progress)
            QtWidgets.QApplication.processEvents()

    def save_deformer_weights(self, env_type="user"):

        if env_type == "lib":
            manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
        else:
            manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

        if manifest_lib:
            # get project path
            version_export_folder = manifest_lib+"/atlas/deformer_weights"
            latest_export_folder = manifest_lib+"/atlas/deformer_weights/latest"

            # create the next version directory
            next_version_directory = self.build_version_directory(version_export_folder)  

            # set the note data from user input to both locations
            note_data = self.open_input_dialog()
            self.set_note(next_version_directory, note_data)
            self.set_note(latest_export_folder, note_data)

            # save the deformer weights in the next version
            objects = pm.ls(sl=True, type="transform")
            self.export_deformer_weights(objects, next_version_directory)
            
            # update the file list widget
            self.update_file_list()

            # save the deformer weights in the latest folder
            objects = pm.ls(sl=True, type="transform")
            self.clean_directory(latest_export_folder)
            self.export_deformer_weights(objects, latest_export_folder)
            
            # update the file list widget
            self.update_file_list()

            # reset the progress bar
            self.reset_progress()

            print("+ Saved skin weights to:", str(version_export_folder), str(latest_export_folder))
        
        else:
            pm.warning("You need to either initialize the current asset or change the asset to a directory you already have.")
    
    def load_deformer_weights(self):

        try:
            version = self.file_list_tree.currentItem().text(0)
            user = self.file_list_tree.currentItem().text(1)

            # determine whether to pull from lib or from user
            if user == "lib":
                manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
            else:
                manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

            if manifest_lib:
                # get project path
                import_folder = manifest_lib+"/atlas/deformer_weights/"+version

                self.import_deformer_weights(import_folder)
                self.progress_bar.reset()

            else:
                pm.warning("You need to either initialize the current asset or change the asset to a directory you already have.")
        except:
            raise
    
    
    ###############################################################################
    #  blendshapes
    ###############################################################################

    def export_blendshapes(self, curves, export_folder):
        
        # set the progress for the progress bar
        try:
            x = 100.0 / (float(len(curves)) * 2)
        except:
            x = 100.0 / 100.0

        for curve in curves:
            atlas_utils.export_curve(curve, export_folder)

            # set the current progress
            self.progress = self.progress + x
            self.progress_bar.setValue(self.progress)
            QtWidgets.QApplication.processEvents()

    def import_blendshapes(self, curves, import_folder):

        # set the progress for the progress bar
        try:
            x = 100.0 / float(len(curves))
        except:
            x = 100.0 / 100.0
        progress = 0

        for curve in curves:
            try:
                atlas_utils.import_curve(curve, import_folder)
            except:
                pm.warning("Error with curve file for control:", curve)

            # set the current progress
            progress = progress + x
            self.progress_bar.setValue(progress)
            QtWidgets.QApplication.processEvents()

    def save_blendshapes(self, env_type="user"):
        if env_type == "lib":
            manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
        else:
            manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

        if manifest_lib:
            # get project path
            version_export_folder = manifest_lib+"/atlas/control_cvs"
            latest_export_folder = manifest_lib+"/atlas/control_cvs/latest"

            # create the next version directory
            next_version_directory = self.build_version_directory(version_export_folder) 

            # set the note data from user input to both locations
            note_data = self.open_input_dialog()
            self.set_note(next_version_directory, note_data)
            self.set_note(latest_export_folder, note_data)

            # save new version
            curves = pm.ls("*_ctl")
            self.export_curves(curves, next_version_directory)

            # update the file list widget
            self.update_file_list()

            # save to latest
            curves = pm.ls("*_ctl")
            self.clean_directory(latest_export_folder)
            self.export_curves(curves, latest_export_folder)

            # update the file list widget
            self.update_file_list()

            # reset the progress bar
            self.reset_progress()

            print("+ Saved control cv's to:", str(version_export_folder), str(latest_export_folder))

        else:
            pm.warning("You need to either initialize the current asset or change the asset to a directory you already have.")
    
    def load_blendshapes(self):

        try:
            version = self.file_list_tree.currentItem().text(0)
            user = self.file_list_tree.currentItem().text(1)

            # determine whether to pull from lib or from user
            if user == "lib":
                manifest_lib = os.environ["LIB_MANIFEST_PROJECT"]
            else:
                manifest_lib = os.environ["USER_MANIFEST_PROJECT"]

            if manifest_lib:
                # get project path
                import_folder = manifest_lib+"/atlas/control_cvs/"+version

                curves = pm.ls("*_ctl")
                self.import_curves(curves, import_folder)
                self.progress_bar.reset()

                print("+ Loaded control cv's from", import_folder)

            else:
                pm.warning("You need to either initialize the current asset or change the asset to a directory you already have.")
        except:
            raise


    ###############################################################################
    #  rebuild UI
    ###############################################################################

    # Delete any instances of this class
    def deleteInstances(self):
        if pm.workspaceControl(self.__class__.toolName+'WorkspaceControl', exists=True, q=True) == True:
            pm.deleteUI(self.__class__.toolName+'WorkspaceControl', control=True)

    # Show window with docking ability
    def run(self):
        self.show(dockable = True)
