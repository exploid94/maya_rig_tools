from shiboken2 import wrapInstance
from PySide2 import QtGui, QtCore, QtWidgets
from maya import OpenMayaUI as OpenMayaUI
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil

class MyWindow(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    toolName = 'myToolWidget'

    def __init__(self, parent = None):
        # Delete any previous instances that is detected. Do this before parenting self to main window!
        self.deleteInstances()
        
        if cmds.workspaceControl(toolName+'WorkspaceControl', exists=True, q=True) == True:
            cmds.deleteUI(toolName+'WorkspaceControl', control=True)

        super(self.__class__, self).__init__(parent = parent)
        mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow() 
        self.mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtWidgets.QMainWindow)
        self.setObjectName(self.__class__.toolName) # Make this unique enough if using it to clear previous instance!

        # Setup window's properties
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('My tool')
        self.resize(200, 200)

        # Create a button and stuff it in a layout
        self.myButton = QtWidgets.QPushButton('My awesome button!!')
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(self.myButton)
        self.setLayout(self.mainLayout)

    # If it's floating or docked, this will run and delete it self when it closes.
    # You can choose not to delete it here so that you can still re-open it through the right-click menu, but do disable any callbacks/timers that will eat memory
    def dockCloseEventTriggered(self):
        self.deleteInstances()

    # Delete any instances of this class
    def deleteInstances(self):
        mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow() 
        mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtWidgets.QMainWindow) # Important that it's QMainWindow, and not QWidget/QDialog

        # Go through main window's children to find any previous instances
        for obj in mayaMainWindow.children():
            if type( obj ) == maya.app.general.mayaMixin.MayaQDockWidget:
                #if obj.widget().__class__ == self.__class__: # Alternatively we can check with this, but it will fail if we re-evaluate the class
                if obj.widget().objectName() == self.__class__.toolName: # Compare object names
                    # If they share the same name then remove it
                    print ('Deleting instance {0}'.format(obj))
                    mayaMainWindow.removeDockWidget(obj) # This will remove from right-click menu, but won't actually delete it! ( still under mainWindow.children() )
                    # Delete it for good
                    obj.setParent(None)
                    obj.deleteLater()        

    # Show window with docking ability
    def run(self):
        self.show(dockable = True)

myWin = MyWindow()
myWin.run()