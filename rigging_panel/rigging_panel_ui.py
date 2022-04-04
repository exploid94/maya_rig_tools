from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets, QtGui
from maya import OpenMayaUI as OpenMayaUI
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil
from rigging_utils import json_utils
from rigging_utils.controls import cv_data
import rigging_panel_tools as rpt
reload(rpt)

class RiggingPanel(MayaQWidgetDockableMixin, QtWidgets.QDialog):   
    toolName = "Rigging Panel"
    toolVersion = "0.1.0"
    bcg_color = "darkCyan" 
    headerColor = "{ background-color: %s; color: rgba(250, 250, 250, 250);}" %bcg_color

    def __init__(self, parent = None):
        # delete self first
        self.deleteInstances()

        super(self.__class__, self).__init__(parent = parent)
        mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow() 
        self.mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtWidgets.QMainWindow)
        self.setObjectName(self.__class__.toolName) # Make this unique enough if using it to clear previous instance!

        # Setup window"s properties
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(self.toolName+" "+self.toolVersion)
        self.resize(200, 200)

        """
        # create menu bar to change ui color
        self.mainMenu = QtWidgets.QMenuBar(self)
        self.editMenu = self.mainMenu.addMenu("UI Color")
        for c in self.colors:
            item = QtWidgets.QAction(c, self)
            self.editMenu.addAction(item)
        """

        # Create tab widgets
        self.tab_bar = QtWidgets.QTabWidget(self)
        self.setup_tab = QtWidgets.QWidget()
        self.binding_tab = QtWidgets.QWidget()
        self.utils_tab = QtWidgets.QTabWidget()
        self.tab_bar.addTab(self.setup_tab, "Setup")
        self.tab_bar.addTab(self.binding_tab, "Binding")
        self.tab_bar.addTab(self.utils_tab, "Utilities")

        #######################################################################
        # Create main layout and align the tabs to the top
        #######################################################################

        self.main_layout = QtWidgets.QVBoxLayout()
        #self.main_layout.addWidget(self.mainMenu)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_layout.addWidget(self.tab_bar)

        #######################################################################
        # Create setup tab and widgets
        #######################################################################

        # Create joint widgets
        self.joints_label = QtWidgets.QLabel("JOINTS")
        self.joints_label.setStyleSheet("QLabel %s" %self.headerColor)
        self.joints_label.setAlignment(QtCore.Qt.AlignCenter)
        self.joint_size_label = QtWidgets.QLabel("Joint Size")
        self.joint_size_label.setAlignment(QtCore.Qt.AlignCenter)
        self.joint_size_number = QtWidgets.QDoubleSpinBox()
        self.joint_size_number.setSingleStep(0.1)
        self.joint_size_number.setRange(0.1, 10.0)
        self.joint_size_number.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.joint_size_number.setValue(1)
        self.joint_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.joint_size_slider.setSliderPosition(10)
        self.joint_size_slider.setRange(1, 100)
        self.split_joint_number = QtWidgets.QSpinBox()
        self.split_joint_number.setRange(1, 100)
        self.split_joint_button = QtWidgets.QPushButton("Split Joint")
        self.draw_joint_button = QtWidgets.QPushButton("Draw Joint Tool")
        self.sc_ik_button = QtWidgets.QPushButton("SC IK")
        self.rp_ik_button = QtWidgets.QPushButton("RP IK")
        self.joint_to_sel_button = QtWidgets.QPushButton("Joint To Selected")

        # Slots for joint widgets
        self.joint_size_slider.valueChanged.connect(self.joint_size_slider_changed)
        self.joint_size_number.editingFinished.connect(self.joint_size_number_changed)
        self.split_joint_button.clicked.connect(lambda: rpt.split_joint(self.split_joint_number.value()))
        self.draw_joint_button.clicked.connect(rpt.draw_joint)
        self.sc_ik_button.clicked.connect(rpt.sc_ik)
        self.rp_ik_button.clicked.connect(rpt.rp_ik)
        self.joint_to_sel_button.clicked.connect(rpt.joint_to_selected)

        # Create control widgets
        self.control_label = QtWidgets.QLabel("CONTROLS")
        self.control_label.setStyleSheet("QLabel %s" %self.headerColor)
        self.control_label.setAlignment(QtCore.Qt.AlignCenter)
        self.control_shape = QtWidgets.QComboBox()
        for s in sorted(cv_data.get_control_dict()):
            self.control_shape.addItem(s)
        self.control_color = QtWidgets.QComboBox()
        for c in QtGui.QColor.colorNames():
            self.control_color.addItem(c)
        self.current_color = QtGui.QColor.getRgb(QtGui.QColor(self.control_color.currentText()))
        self.create_control_button = QtWidgets.QPushButton("Create Control")
        self.update_color_button = QtWidgets.QPushButton("Update Color")

        # Slots for control widgets
        self.control_color.currentIndexChanged["QString"].connect(self.color_change)
        self.create_control_button.clicked.connect(lambda: rpt.create_control(self.control_shape.currentText(), self.current_color))
        self.update_color_button.clicked.connect(lambda: rpt.update_color(self.current_color))

        # Create renamer widgets
        self.rename_label = QtWidgets.QLabel("RENAMER")
        self.rename_label.setStyleSheet("QLabel %s" %self.headerColor)
        self.rename_label.setAlignment(QtCore.Qt.AlignCenter)
        self.rename_number_label = QtWidgets.QLabel("Use # in place of numbers when iterating.\narm_L0_001_jnt would be arm_L0_###_jnt")
        self.rename_dag_cb = QtWidgets.QCheckBox("Dag")
        self.rename_line = QtWidgets.QLineEdit()
        self.rename_button = QtWidgets.QPushButton("Rename")
        self.replace_line = QtWidgets.QLineEdit()
        self.replace_with_line = QtWidgets.QLineEdit()
        self.replace_button = QtWidgets.QPushButton("Replace")

        # slots for renamer widgets
        self.rename_button.clicked.connect(lambda: rpt.rename_with_pound(self.rename_line.text(), self.rename_dag_cb.isChecked()))
        self.replace_button.clicked.connect(lambda: rpt.replace(self.replace_line.text(), self.replace_with_line.text(), self.rename_dag_cb.isChecked()))

        # Create attributes widgets
        self.attr_label = QtWidgets.QLabel("ATTRIBUTES")
        self.attr_label.setStyleSheet("QLabel %s" %self.headerColor)
        self.attr_label.setAlignment(QtCore.Qt.AlignCenter)
        self.attr_name_line = QtWidgets.QLineEdit()
        self.attr_trans_cb = QtWidgets.QCheckBox("Translates")
        self.attr_rots_cb = QtWidgets.QCheckBox("Rotates")
        self.attr_scales_cb = QtWidgets.QCheckBox("Scales")
        self.attr_channelbox_cb = QtWidgets.QCheckBox("Channel Box")
        self.get_default_values_button = QtWidgets.QPushButton("Get Default Values")
        self.make_keyable_button = QtWidgets.QPushButton("Keyable / Displayable")
        self.make_lock_button = QtWidgets.QPushButton("Lock / Unlock")
        self.make_hidden_button = QtWidgets.QPushButton("Hide / Unhide")
        self.unhide_all_button = QtWidgets.QPushButton("Unhide All (T/R/S)")
        self.unhide_all_custom_button = QtWidgets.QPushButton("Unhide All (Custom)")
        self.zero_out_button = QtWidgets.QPushButton("Zero Out (T/R/S)")
        self.move_up_button = QtWidgets.QPushButton("Move Selected Attr Up")
        self.move_down_button = QtWidgets.QPushButton("Move Selected Attr Down")

        # Slots for attributes widgets
        self.get_default_values_button.clicked.connect(rpt.attr_defaults)
        self.make_keyable_button.clicked.connect(lambda: rpt.attr_keyable(self.attr_trans_cb.isChecked(),
                                                                        self.attr_rots_cb.isChecked(),
                                                                        self.attr_scales_cb.isChecked(), 
                                                                        self.attr_channelbox_cb.isChecked()))
        self.make_lock_button.clicked.connect(lambda: rpt.attr_lock(self.attr_trans_cb.isChecked(),
                                                                    self.attr_rots_cb.isChecked(),
                                                                    self.attr_scales_cb.isChecked(), 
                                                                    self.attr_channelbox_cb.isChecked()))
        self.make_hidden_button.clicked.connect(lambda: rpt.attr_hide(self.attr_trans_cb.isChecked(),
                                                                    self.attr_rots_cb.isChecked(),
                                                                    self.attr_scales_cb.isChecked(), 
                                                                    self.attr_channelbox_cb.isChecked()))
        self.unhide_all_button.clicked.connect(rpt.attr_unhide)
        self.unhide_all_custom_button.clicked.connect(rpt.attr_unhide_custom)
        self.zero_out_button.clicked.connect(rpt.zero_out)
        self.move_up_button.clicked.connect(rpt.move_attr_up)
        self.move_down_button.clicked.connect(rpt.move_attr_down)

        #######################################################################
        # Create the layout for the setup tab and align to the top
        #######################################################################

        self.setup_tab_layout = QtWidgets.QGridLayout()
        self.setup_tab_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setup_tab_sub_layout = QtWidgets.QGridLayout()
        self.setup_tab_sub_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setup_tab_sub_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

        self.joints_main_layout = QtWidgets.QGridLayout()
        self.joints_sub_layout = QtWidgets.QGridLayout()

        self.controls_main_layout = QtWidgets.QGridLayout()
        self.controls_sub_layout = QtWidgets.QGridLayout()

        self.renamer_main_layout = QtWidgets.QGridLayout()
        self.renamer_sub_layout = QtWidgets.QGridLayout()

        self.attributes_main_layout = QtWidgets.QGridLayout()
        self.attributes_sub_layout = QtWidgets.QGridLayout()

        # set the scroll area and the main layout
        self.setup_scroll_widget = QtWidgets.QWidget()
        self.setup_scroll_widget.setLayout(self.setup_tab_sub_layout)
        self.setup_scroll_area = QtWidgets.QScrollArea()
        self.setup_tab_layout.addWidget(self.setup_scroll_area)
        self.setup_scroll_area.setWidget(self.setup_scroll_widget)
        self.setup_scroll_area.setWidgetResizable(True)

        # spacing out the layouts
        self.setup_tab_layout.setVerticalSpacing(20)

        self.joints_main_layout.setVerticalSpacing(20)
        self.joints_sub_layout.setVerticalSpacing(3)

        self.controls_main_layout.setVerticalSpacing(20)
        self.controls_sub_layout.setVerticalSpacing(3)

        self.renamer_main_layout.setVerticalSpacing(20)
        self.renamer_sub_layout.setVerticalSpacing(5)

        self.attributes_main_layout.setVerticalSpacing(20)
        self.attributes_sub_layout.setVerticalSpacing(3)

        # adding all the main layouts to the setup tab layout
        self.setup_tab_sub_layout.addLayout(self.joints_main_layout, 0, 0, QtCore.Qt.AlignTop)
        self.setup_tab_sub_layout.addLayout(self.controls_main_layout, 1, 0, QtCore.Qt.AlignTop)
        self.setup_tab_sub_layout.addLayout(self.renamer_main_layout, 2, 0, QtCore.Qt.AlignTop)
        self.setup_tab_sub_layout.addLayout(self.attributes_main_layout, 3, 0, QtCore.Qt.AlignTop)

        # adding the sub layouts to the joints main layout
        self.joints_main_layout.addWidget(self.joints_label, 0, 0)
        self.joints_main_layout.addLayout(self.joints_sub_layout, 1, 0, QtCore.Qt.AlignTop)

        # adding sub layouts to the controls main layout
        self.controls_main_layout.addWidget(self.control_label, 0, 0)
        self.controls_main_layout.addLayout(self.controls_sub_layout, 1, 0, QtCore.Qt.AlignTop)

        # adding the sub layouts to the renamer main layout
        self.renamer_main_layout.addWidget(self.rename_label, 0, 0)
        self.renamer_main_layout.addLayout(self.renamer_sub_layout, 1, 0, QtCore.Qt.AlignTop)

        # adding the sub layouts to the attributes main layout
        self.attributes_main_layout.addWidget(self.attr_label, 0, 0)
        self.attributes_main_layout.addLayout(self.attributes_sub_layout, 1, 0, QtCore.Qt.AlignTop)

        # adding the widgets to the joints sub layout
        self.joints_sub_layout.addWidget(self.joint_size_label, 0, 0, 1, 2)
        self.joints_sub_layout.addWidget(self.joint_size_number, 1, 0)
        self.joints_sub_layout.addWidget(self.joint_size_slider, 1, 1)
        self.joints_sub_layout.addWidget(self.split_joint_number, 2, 0)
        self.joints_sub_layout.addWidget(self.split_joint_button, 2, 1)
        self.joints_sub_layout.addWidget(self.draw_joint_button, 3, 0, 1, 2)
        self.joints_sub_layout.addWidget(self.sc_ik_button, 4, 0, 1, 2)
        self.joints_sub_layout.addWidget(self.rp_ik_button, 5, 0, 1, 2)
        self.joints_sub_layout.addWidget(self.joint_to_sel_button, 6, 0, 1, 2)

        # adding the widgets to the control sub layout
        self.controls_sub_layout.addWidget(self.control_shape, 0, 0)
        self.controls_sub_layout.addWidget(self.control_color, 1, 0)
        self.controls_sub_layout.addWidget(self.create_control_button, 2, 0)
        self.controls_sub_layout.addWidget(self.update_color_button, 3, 0)

        # adding the widgets to the renamer sub layout
        self.renamer_sub_layout.addWidget(self.rename_number_label, 0, 0, 1, 2)
        self.renamer_sub_layout.addWidget(self.rename_dag_cb, 1, 0)
        self.renamer_sub_layout.addWidget(self.rename_line, 2, 0, 1, 2)
        self.renamer_sub_layout.addWidget(self.rename_button, 3, 0, 1, 2)
        self.renamer_sub_layout.addWidget(self.replace_line, 4, 0)
        self.renamer_sub_layout.addWidget(self.replace_with_line, 4, 1)
        self.renamer_sub_layout.addWidget(self.replace_button, 5, 0, 1, 2)

        # adding the widgets to the attributes sub layout 
        self.attributes_sub_layout.addWidget(self.attr_trans_cb, 0, 0)
        self.attributes_sub_layout.addWidget(self.attr_rots_cb, 0, 1)
        self.attributes_sub_layout.addWidget(self.attr_scales_cb, 0, 2)
        self.attributes_sub_layout.addWidget(self.attr_channelbox_cb, 1, 0)
        #self.attributes_sub_layout.addWidget(self.attr_name_line, 1, 1, 1, 2)
        self.attributes_sub_layout.addWidget(self.get_default_values_button, 2, 0, 1, 3)
        self.attributes_sub_layout.addWidget(self.make_keyable_button, 3, 0, 1, 3)
        self.attributes_sub_layout.addWidget(self.make_lock_button, 4, 0, 1, 3)
        self.attributes_sub_layout.addWidget(self.make_hidden_button, 5, 0, 1, 3)
        self.attributes_sub_layout.addWidget(self.unhide_all_button, 6, 0, 1, 3)
        self.attributes_sub_layout.addWidget(self.unhide_all_custom_button, 7, 0, 1, 3)
        self.attributes_sub_layout.addWidget(self.zero_out_button, 8, 0, 1, 3)
        self.attributes_sub_layout.addWidget(self.move_up_button, 9, 0, 1, 3)
        self.attributes_sub_layout.addWidget(self.move_down_button, 10, 0, 1, 3)

        #######################################################################
        # Create binding tab and widgets
        #######################################################################

        # Create binding widgets
        self.binding_label = QtWidgets.QLabel("SKINNING")
        self.binding_label.setStyleSheet("QLabel %s" %self.headerColor)
        self.binding_label.setAlignment(QtCore.Qt.AlignCenter)
        self.smooth_bind_button = QtWidgets.QPushButton("Smooth Bind")
        self.detach_skin_button = QtWidgets.QPushButton("Detach Skin")
        self.copy_skin_weights_button = QtWidgets.QPushButton("Copy Skin Weights")
        self.paint_skin_weights_button = QtWidgets.QPushButton("Paint Skin Weights")
        self.smooth_skin_weights_button = QtWidgets.QPushButton("Smooth Skin Weights")
        self.mirror_weights_button = QtWidgets.QPushButton("Mirror Weights")
        self.lock_sel_weights_button = QtWidgets.QPushButton("Lock Weights On Selected")
        self.unlock_sel_weights_button = QtWidgets.QPushButton("Unlock Weights On Selected")
        self.lock_all_weights_button = QtWidgets.QPushButton("Lock All Weights")
        self.unlock_all_weights_button = QtWidgets.QPushButton("Unlock All Weights")
        self.select_influences_button = QtWidgets.QPushButton("Select Influences")
        self.select_skin_cluster_button = QtWidgets.QPushButton("Select Skin Cluster")

        # slots for binding widgets
        self.smooth_bind_button.clicked.connect(rpt.smooth_bind)
        self.detach_skin_button.clicked.connect(rpt.detach_skin)
        self.copy_skin_weights_button.clicked.connect(rpt.copy_skin)
        self.paint_skin_weights_button.clicked.connect(rpt.paint_skin)
        self.smooth_skin_weights_button.clicked.connect(rpt.smooth_skin)
        self.mirror_weights_button.clicked.connect(rpt.mirror_skin)
        self.lock_sel_weights_button.clicked.connect(rpt.lock_weights)
        self.unlock_sel_weights_button.clicked.connect(rpt.unlock_weights)
        self.lock_all_weights_button.clicked.connect(rpt.lock_all_weights)
        self.unlock_all_weights_button.clicked.connect(rpt.unlock_all_weights)
        self.select_influences_button.clicked.connect(rpt.select_influences)
        self.select_skin_cluster_button.clicked.connect(rpt.select_skin_cluster)

        # Create constraint widgets
        self.constraint_label = QtWidgets.QLabel("CONSTRAINTS")
        self.constraint_label.setStyleSheet("QLabel %s" %self.headerColor)
        self.constraint_label.setAlignment(QtCore.Qt.AlignCenter)
        self.constraint_offset_cb = QtWidgets.QCheckBox("Maintain Offset")
        self.constraint_exclude_trans_cb = QtWidgets.QCheckBox("Exclude Translates")
        self.constraint_exclude_rots_cb = QtWidgets.QCheckBox("Exclude Rotates")
        self.constraint_combo_box = QtWidgets.QComboBox()
        for con in ['Parent', 'Orient', 'Scale', 'Point', 'Aim', 'Pole Vector']:
            self.constraint_combo_box.addItem(con)
        self.create_constraint_button = QtWidgets.QPushButton("Create Constraint")

        # slots for constraint widgets
        self.create_constraint_button.clicked.connect(lambda: rpt.create_constraint(self.constraint_offset_cb.isChecked(),
                                                                                    self.constraint_exclude_trans_cb.isChecked(),
                                                                                    self.constraint_exclude_rots_cb.isChecked(),
                                                                                    self.constraint_combo_box.currentText()))

        #######################################################################
        # Create the layout for the binding tab and align to the top
        #######################################################################
        self.binding_tab_layout = QtWidgets.QGridLayout()
        self.binding_tab_layout.setAlignment(QtCore.Qt.AlignTop)
        self.binding_tab_sub_layout = QtWidgets.QGridLayout()
        self.binding_tab_sub_layout.setAlignment(QtCore.Qt.AlignTop)
        self.binding_tab_sub_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

        self.skinning_main_layout = QtWidgets.QGridLayout()
        self.skinning_sub_layout = QtWidgets.QGridLayout()

        self.constraints_main_layout = QtWidgets.QGridLayout()
        self.constraints_sub_layout = QtWidgets.QGridLayout()

        # set the scroll area and the main layout
        self.binding_scroll_widget = QtWidgets.QWidget()
        self.binding_scroll_widget.setLayout(self.binding_tab_sub_layout)
        self.binding_scroll_area = QtWidgets.QScrollArea()
        self.binding_tab_layout.addWidget(self.binding_scroll_area)
        self.binding_scroll_area.setWidget(self.binding_scroll_widget)
        self.binding_scroll_area.setWidgetResizable(True)

        # spacing out the layouts
        self.binding_tab_layout.setVerticalSpacing(20)

        self.skinning_main_layout.setVerticalSpacing(20)
        self.skinning_sub_layout.setVerticalSpacing(3)

        self.constraints_main_layout.setVerticalSpacing(20)
        self.constraints_sub_layout.setVerticalSpacing(3)

        # adding all the main layouts to the skinning tab layout
        self.binding_tab_sub_layout.addLayout(self.skinning_main_layout, 0, 0, QtCore.Qt.AlignTop)
        self.binding_tab_sub_layout.addLayout(self.constraints_main_layout, 1, 0, QtCore.Qt.AlignTop)

        # adding sub layouts to the skinning main layout
        self.skinning_main_layout.addWidget(self.binding_label, 0, 0, QtCore.Qt.AlignTop)
        self.skinning_main_layout.addLayout(self.skinning_sub_layout, 1, 0, QtCore.Qt.AlignTop)

        # adding the sub layouts to the renamer main layout
        self.constraints_main_layout.addWidget(self.constraint_label, 0, 0)
        self.constraints_main_layout.addLayout(self.constraints_sub_layout, 1, 0, QtCore.Qt.AlignTop)

        # add the widgets to the skinning tab layout
        self.skinning_sub_layout.addWidget(self.smooth_bind_button, 0, 0)
        self.skinning_sub_layout.addWidget(self.detach_skin_button, 1, 0)
        self.skinning_sub_layout.addWidget(self.copy_skin_weights_button, 2, 0)
        self.skinning_sub_layout.addWidget(self.paint_skin_weights_button, 3, 0)
        self.skinning_sub_layout.addWidget(self.smooth_skin_weights_button, 4, 0)
        self.skinning_sub_layout.addWidget(self.mirror_weights_button, 5, 0)
        self.skinning_sub_layout.addWidget(self.lock_sel_weights_button, 6, 0)
        self.skinning_sub_layout.addWidget(self.unlock_sel_weights_button, 7, 0)
        self.skinning_sub_layout.addWidget(self.lock_all_weights_button, 8, 0)
        self.skinning_sub_layout.addWidget(self.unlock_all_weights_button, 9, 0)
        self.skinning_sub_layout.addWidget(self.select_influences_button, 10, 0)
        self.skinning_sub_layout.addWidget(self.select_skin_cluster_button, 11, 0)

        # adding the widgets to the constraints sub layout
        self.constraints_sub_layout.addWidget(self.constraint_offset_cb, 0, 0)
        self.constraints_sub_layout.addWidget(self.constraint_exclude_trans_cb, 1, 0)
        self.constraints_sub_layout.addWidget(self.constraint_exclude_rots_cb, 1, 1)
        self.constraints_sub_layout.addWidget(self.constraint_combo_box, 2, 0, 1, 2)
        self.constraints_sub_layout.addWidget(self.create_constraint_button, 3, 0, 1, 2)

        #######################################################################
        # Create utilities tab and widgets
        #######################################################################
        # Create MISC widgets
        self.misc_label = QtWidgets.QLabel("MISC")
        self.misc_label.setStyleSheet("QLabel %s" %self.headerColor)
        self.misc_label.setAlignment(QtCore.Qt.AlignCenter)
        self.freeze_transforms_button = QtWidgets.QPushButton("Freeze Transforms")
        self.delete_history_button = QtWidgets.QPushButton("Delete History")
        self.center_pivot_button = QtWidgets.QPushButton("Center Pivot")
        self.draw_curve_button = QtWidgets.QPushButton("Draw Curve")
        self.rivet_button = QtWidgets.QPushButton("Rivet")
        
        # Slots for misc widgets
        self.freeze_transforms_button.clicked.connect(rpt.freeze)
        self.delete_history_button.clicked.connect(rpt.delete_history)
        self.center_pivot_button.clicked.connect(rpt.center_pivot)
        self.draw_curve_button.clicked.connect(rpt.draw_curve)
        self.rivet_button.clicked.connect(rpt.create_rivet)

        # Create alembic widgets
        self.alembic_label = QtWidgets.QLabel("ALEMBIC")
        self.alembic_label.setStyleSheet("QLabel %s" %self.headerColor)
        self.alembic_label.setAlignment(QtCore.Qt.AlignCenter)
        self.export_hierarchy_button = QtWidgets.QPushButton("Export Hierarchy")
        self.export_selected_button = QtWidgets.QPushButton("Export Selected")
        self.import_alembic_button = QtWidgets.QPushButton("Import Alembic")

        # slots for alembic widgets

        #######################################################################
        # Create the layout for the utilities tab and align to the top
        #######################################################################

        self.utils_tab_layout = QtWidgets.QGridLayout()
        self.utils_tab_layout.setAlignment(QtCore.Qt.AlignTop)
        self.utils_tab_sub_layout = QtWidgets.QGridLayout()
        self.utils_tab_sub_layout.setAlignment(QtCore.Qt.AlignTop)
        self.utils_tab_sub_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

        self.misc_main_layout = QtWidgets.QGridLayout()
        self.misc_sub_layout = QtWidgets.QGridLayout()

        self.alembic_main_layout = QtWidgets.QGridLayout()
        self.alembic_sub_layout = QtWidgets.QGridLayout()

        # set the scroll area and the main layout
        self.utils_scroll_widget = QtWidgets.QWidget()
        self.utils_scroll_widget.setLayout(self.utils_tab_sub_layout)
        self.utils_scroll_area = QtWidgets.QScrollArea()
        self.utils_tab_layout.addWidget(self.utils_scroll_area)
        self.utils_scroll_area.setWidget(self.utils_scroll_widget)
        self.utils_scroll_area.setWidgetResizable(True)

        # spacing out the layouts
        self.utils_tab_layout.setVerticalSpacing(20)

        self.misc_main_layout.setVerticalSpacing(20)
        self.misc_sub_layout.setVerticalSpacing(3)

        self.alembic_main_layout.setVerticalSpacing(20)
        self.alembic_sub_layout.setVerticalSpacing(3)

        # adding all the main layouts to the utils tab layout
        self.utils_tab_sub_layout.addLayout(self.misc_main_layout, 1, 0, QtCore.Qt.AlignTop)
        self.utils_tab_sub_layout.addLayout(self.alembic_main_layout, 1, 0, QtCore.Qt.AlignTop)

        # adding sub layouts to the binding main layout
        self.misc_main_layout.addWidget(self.misc_label, 0, 0, QtCore.Qt.AlignTop)
        self.misc_main_layout.addLayout(self.misc_sub_layout, 1, 0, QtCore.Qt.AlignTop)

        # add the widgets to the misc button layout
        self.misc_sub_layout.addWidget(self.freeze_transforms_button, 0, 0)
        self.misc_sub_layout.addWidget(self.delete_history_button, 1, 0)
        self.misc_sub_layout.addWidget(self.center_pivot_button, 2, 0)
        self.misc_sub_layout.addWidget(self.draw_curve_button, 3, 0)
        self.misc_sub_layout.addWidget(self.rivet_button, 4, 0)

        #######################################################################
        # Set tab layouts and the main layout
        #######################################################################

        # Set the main layout to the window
        self.setLayout(self.main_layout) 
        self.setup_tab.setLayout(self.setup_tab_layout) 
        self.binding_tab.setLayout(self.binding_tab_layout) 
        self.utils_tab.setLayout(self.utils_tab_layout) 

    def color_change(self, text):
        self.control_color.setStyleSheet("QComboBox {background-color: %s;}" %text) 
        self.current_color = QtGui.QColor.getRgb(QtGui.QColor(self.control_color.currentText()))

    def joint_size_slider_changed(self):
        value = float(self.joint_size_slider.value()) / 10.0
        self.joint_size_number.setValue(value)
        rpt.joint_size_set(value)
    
    def joint_size_number_changed(self):
        value = self.joint_size_number.value()
        self.joint_size_slider.setValue(int(value*10))
        rpt.joint_size_set(value)

    # Delete any instances of this class
    def deleteInstances(self):
        if cmds.workspaceControl(self.__class__.toolName+"WorkspaceControl", exists=True, q=True) == True:
            cmds.deleteUI(self.__class__.toolName+"WorkspaceControl", control=True)

    # Show window with docking ability
    def run(self):
        self.show(dockable = True)