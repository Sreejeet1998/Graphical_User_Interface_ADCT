# -*- coding: utf-8 -*-
"""
A module containing ``NodeEditorWidget`` class
"""
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPen, QFont, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout,QLineEdit, QApplication, QMessageBox, QLabel, QGraphicsItem, QTextEdit, QPushButton

from GUIWINDOW.node_scene import Scene, InvalidFile, fields
from GUIWINDOW.node_node import Node
from GUIWINDOW.node_edge import Edge, EDGE_TYPE_BEZIER
from GUIWINDOW.node_graphics_view import QDMGraphicsView
from GUIWINDOW.utils import dumpException

class NodeEditorWidget(QWidget):
    Scene_class = Scene
    GraphicsView_class = QDMGraphicsView

    """The ``NodeEditorWidget`` class"""
    def __init__(self, parent:QWidget=None):
        """
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance Attributes:

        - **filename** - currently graph's filename or ``None``
        """
        super().__init__(parent)

        self.filename = None

        self.initUI()


    def initUI(self):
        """Set up this ``NodeEditorWidget`` with its layout,  :class:`~GUIWINDOW.node_scene.Scene` and
        :class:`~GUIWINDOW.node_graphics_view.QDMGraphicsView`"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # crate graphics scene
        self.scene = self.__class__.Scene_class()

        # create graphics view
        self.view = self.__class__.GraphicsView_class(self.scene.grScene, self)
        self.layout.addWidget(self.view)


    def isModified(self) -> bool:
        """Has the `Scene` been modified?

        :return: ``True`` if the `Scene` has been modified
        :rtype: ``bool``
        """
        return self.scene.isModified()

    def isFilenameSet(self) -> bool:
        """Do we have a graph loaded from file or are we creating a new one?

        :return: ``True`` if filename is set. ``False`` if it is a new graph not yet saved to a file
        :rtype: ''bool''
        """
        return self.filename is not None

    def getSelectedItems(self) -> list:
        """Shortcut returning `Scene`'s currently selected items

        :return: list of ``QGraphicsItems``
        :rtype: list[QGraphicsItem]
        """
        return self.scene.getSelectedItems()

    def hasSelectedItems(self) -> bool:
        """Is there something selected in the :class:`GUIWINDOW.node_scene.Scene`?

        :return: ``True`` if there is something selected in the `Scene`
        :rtype: ``bool``
        """
        return self.getSelectedItems() != []

    def canUndo(self) -> bool:
        """Can Undo be performed right now?

        :return: ``True`` if we can undo
        :rtype: ``bool``
        """
        return self.scene.history.canUndo()

    def canRedo(self) -> bool:
        """Can Redo be performed right now?

        :return: ``True`` if we can redo
        :rtype: ``bool``
        """
        return self.scene.history.canRedo()

    def getUserFriendlyFilename(self) -> str:
        """Get user friendly filename. Used in the window title

        :return: just a base name of the file or `'New Graph'`
        :rtype: ``str``
        """
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "")

    def fileNew(self):
        """Empty the scene (create new file)"""
        from INTERNAL_SCENE.calc_sub_window import variableManager
        print("on new d", variableManager.lb2)
        variableManager.lb2 = ""

        #######################################
        variableManager.lulb2 = ""
        variableManager.lulb2_txt = ""
        variableManager.lulb4 = ""

        variableManager.mflb2 = ""
        variableManager.mflb2_txt = ""
        variableManager.mflb4 = ""

        variableManager.umlb2 = ""
        variableManager.umlb2_txt = ""
        variableManager.umlb4 = ""

        variableManager.cdlabel_txt = ""
        variableManager.cdtxt = ""
        variableManager.last_name_lu = ""
        variableManager.last_name_mf = ""
        variableManager.last_name_um = ""
        variableManager.cdlb2 = ""
        variableManager.cdlb4 = ""
        variableManager.cdlb6 = ""
        variableManager.cdlb4_txt = ""
        variableManager.cdlb6_txt = ""
        #outlist = []
        variableManager.cdselected_items = []
        variableManager.cdselected_items_list = ''
        #######################################
        print("on new d", variableManager.lb2)
       # print("on new lastname", variableManager.last_name)
        variableManager.last_name_lu = ""
        variableManager.last_name_mf = ""
        variableManager.last_name_um = ""
        #print("Nammmmmmm", variableManager.last_name)
        variableManager.opcode.clear()
        print("clearing")
        fields.clear()
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()

    def fileLoad(self, filename:str):
        """Load serialized graph from JSON file

        :param filename: file to load
        :type filename: ``str``
        """
        from INTERNAL_SCENE.calc_sub_window import variableManager
        variableManager.opcode.clear()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            self.scene.history.clear()
            self.scene.history.storeInitialHistoryStamp()
            return True
        except FileNotFoundError as e:
            dumpException(e)
            QMessageBox.warning(self, "Error loading %s" % os.path.basename(filename), str(e).replace('[Errno 2]',''))
            return False
        except InvalidFile as e:
            dumpException(e)
            # QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Error loading %s" % os.path.basename(filename), str(e))
            return False
        finally:
            QApplication.restoreOverrideCursor()


    def fileSave(self, filename:str=None):
        """Save serialized graph to JSON file. When called with an empty parameter, we won't store/remember the filename.

        :param filename: file to store the graph
        :type filename: ``str``
        """
        if filename is not None: self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()
        return True
    def fileCompile(self, filename:str=None):
        """Save serialized graph to JSON file. When called with an empty parameter, we won't store/remember the filename.

        :param filename: file to store the graph
        :type filename: ``str``
        """
        if filename is not None: self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.dumpJson(self.filename)
        QApplication.restoreOverrideCursor()
        return True


