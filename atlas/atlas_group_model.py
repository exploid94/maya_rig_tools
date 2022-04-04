from PySide2 import QtGui, QtCore, QtWidgets
###############################
# This is all for the file list and collapsable
###############################
datas = {
    "Category 1": [
        ("dsfg", "test", "tes1", "tejk"),
        ("sdfg", "asdf", "asdf", "asdf"),
    ],
    "Category 2": [
        ("dsfg", "asdf", "asdf", "asdf"),
        ("sdfg", "asdf", "asdf", "asdf"),
    ],
    "Category 3": [
        ("sdfg", "asdf", "asdf", "asdf"),
        ("sdfg", "asdf", "asdf", "asdf"),
    ],
    "Category 4": [
        ("sdfg", "sdf", "asdf", "asdf"),
        ("sdfg", "asdf", "asdf", "asdf"),
    ],
    "Category 5": [
        ("sdfg", "asdf", "asdf", "asdf"),
        ("sdfg", "asdf", "asdf", "asdf"),
    ],
}

class GroupDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(GroupDelegate, self).__init__(parent)
        style = QtGui.qApp.style()
        self._plus_icon = style.standardIcon(style.SP_ToolBarHorizontalExtensionButton)
        self._minus_icon = style.standardIcon(style.SP_ToolBarVerticalExtensionButton)

    def initStyleOption(self, option, index):
        super(GroupDelegate, self).initStyleOption(option, index)
        if not index.parent().isValid():
            is_open = bool(option.state & QtWidgets.QStyle.State_Open)
            option.features |= QtWidgets.QStyleOptionViewItem.HasDecoration
            option.icon = self._minus_icon if is_open else self._plus_icon

class GroupView(QtWidgets.QTreeView):
    def __init__(self, model, parent=None):
        super(GroupView, self).__init__(parent)
        self.setIndentation(0)
        self.setExpandsOnDoubleClick(False)
        self.clicked.connect(self.on_clicked)
        delegate = GroupDelegate(self)
        self.setItemDelegateForColumn(0, delegate)
        self.setModel(model)
        self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    #@QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_clicked(self, index):
        if not index.parent().isValid() and index.column() == 0:
            self.setExpanded(index, not self.isExpanded(index))

class GroupModel(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(GroupModel, self).__init__(parent)
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["", "Name", "Date", "Notes"])
        for i in range(self.columnCount()):
            it = self.horizontalHeaderItem(i)

    def add_group(self, group_name):
        item_root = QtGui.QStandardItem()
        item_root.setEditable(False)
        item = QtGui.QStandardItem(group_name)
        item.setEditable(False)
        ii = self.invisibleRootItem()
        i = ii.rowCount()
        for j, it in enumerate((item_root, item)):
            ii.setChild(i, j, it)
            ii.setEditable(False)
        for j in range(self.columnCount()):
            it = ii.child(i, j)
            if it is None:
                it = QtGui.QStandardItem()
                ii.setChild(i, j, it)
        return item_root

    def append_element_to_group(self, group_item, texts):
        j = group_item.rowCount()
        item_icon = QtGui.QStandardItem()
        item_icon.setEditable(False)
        item_icon.setIcon(QtGui.QIcon("game.png"))
        group_item.setChild(j, 0, item_icon)
        for i, text in enumerate(texts):
            item = QtGui.QStandardItem(text)
            item.setEditable(False)
            group_item.setChild(j, i+1, item)
