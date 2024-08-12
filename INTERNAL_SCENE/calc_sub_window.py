import json
from tkinter import filedialog

import PyQt5
from PyQt5.QtWidgets import QLabel, QCompleter, QListWidget, QGridLayout
#from PyQt5.QtWidgets.QMainWindow import statusBar
from PyQt5.QtGui import QIcon, QPixmap, QStandardItem
from PyQt5.QtCore import QDataStream, QIODevice, Qt, QStringListModel
from PyQt5.QtWidgets import QMessageBox, QAction,QDialog, QPushButton, QGraphicsProxyWidget, QMenu, QComboBox, QVBoxLayout, QWidget, QLineEdit

import GUIWINDOW.node_editor_window
from INTERNAL_SCENE.calc_conf import CALC_NODES, get_class_from_opcode, LISTBOX_MIMETYPE
from INTERNAL_SCENE.calc_node_base import CalcNode
from INTERNAL_SCENE.nodes.output import CalcNode_Input, CalcNode_LookUp
from GUIWINDOW.node_editor_widget import NodeEditorWidget
from GUIWINDOW.node_edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER, EDGE_TYPE_SQUARE
from GUIWINDOW.node_graphics_view import MODE_EDGE_DRAG
from GUIWINDOW.node_node import Node
from GUIWINDOW.utils import dumpException
#from INTERNAL_SCENE.calc_window import CalculatorWindow
DEBUG = True
DEBUG_CONTEXT = False
num = []
top = '{"Fields":{'
n = ""
lb6 = ""
class variableManager:
    lb2 = ""
    opcode = []

    lulb2 = ""
    lulb2_txt = ""
    lulb4 = ""

    mflb2 = ""
    mflb2_txt = ""
    mflb4 = ""

    umlb2 = ""
    umlb2_txt = ""
    umlb4 = ""

    cdlabel_txt = ""
    cdtxt = ""
    last_name_lu = ""
    last_name_mf = ""
    last_name_um = ""
    last_name_add = ""

    cdlb2 = ""
    cdlb4 = ""
    cdlb6 = ""
    cdlb4_txt = ""
    cdlb6_txt = ""

    addlb2 = ""
    addlb2_txt = ""
    update_addlabel2_text = ""
    addlb4 = ""
    addlb4_txt = ""
    update_addlabel4_text = ""

    outlist = []
    cdselected_items = []
    cdselected_items_list = ''

    input_box_name_list = []

    file_path = ""

variableManager = variableManager()

class SubstringCompleter(QCompleter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterMode(Qt.MatchContains)
        self.setCaseSensitivity(Qt.CaseSensitive)

    def splitPath(self, path):
        return [path]
class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        # self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()
        self.initNewNodeActions()

        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.history.addHistoryRestoredListener(self.onHistoryRestored)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)
        self._close_event_listeners = []

    def getNodeClassFromData(self, data):
        if 'op_code' not in data: return Node
        return get_class_from_opcode(data['op_code'])

    def doEvalOutputs(self):
        # eval all output nodes
        for node in self.scene.nodes:
            if node.__class__.__name__ == "CalcNode_Output":
                node.eval()

    def onHistoryRestored(self):
        self.doEvalOutputs()

    def fileLoad(self, filename):
        if super().fileLoad(filename):
            self.doEvalOutputs()
            return True

        return False

    def initNewNodeActions(self):
        self.node_actions = {}
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            node = CALC_NODES[key]
            self.node_actions[node.op_code] = QAction(QIcon(node.icon), node.op_title)
            self.node_actions[node.op_code].setData(node.op_code)

    def initNodesContextMenu(self):
        context_menu = QMenu(self)
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys: context_menu.addAction(self.node_actions[key])
        return context_menu

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listeners: callback(self, event)

    def onDragEnter(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            # print(" ... denied drag enter event")
            event.setAccepted(False)

    def onDrop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(LISTBOX_MIMETYPE)
            print("Event Data -", eventData)
            dataStream = QDataStream(eventData, QIODevice.ReadOnly)
            Id = id(dataStream)
            print(Id)
            print("datastrem =", dataStream)
            pixmap = QPixmap()
            dataStream >> pixmap
            op_code = dataStream.readInt()
            text = dataStream.readQString()
            print(text)
            global num
            num.append(Id)
            variableManager.opcode.append(op_code)

            # for i in range(len(opcode)):
            #     global top
            #     if opcode[i] == 1:
            #         list1 = '"ndl.SourceMeta.additionalInfo@note":{'
            #         top = "{} {}".format(top,list1)
            #     elif opcode[i] == 3:
            #         action = '"action": ["lookUp"]},'
            #         #top2 = "{}{}".format(list1,action)
            #         top = "{}{}".format(top,action)
            #     elif opcode[i] == 4:
            #         list1 = {"Fields":{"ndl.SourceMeta.additionalInfo@note": {"action": ["moveField"]}}}
            # close = '}}}'
            # top = "{}{}".format(top,close)
            #if op_code == CalcNode.op_code: num = CalcNode_Input.Nd_number
            #else: pass
            mouse_position = event.pos()
            scene_position = self.scene.grScene.views()[0].mapToScene(mouse_position)

            if DEBUG: print("GOT DROP: [%d] '%s'" % (op_code, text), variableManager.opcode, "mouse:", mouse_position, "scene:", scene_position, "Number", num)

            try:
                node = get_class_from_opcode(op_code)(self.scene)
                node.setPos(scene_position.x(), scene_position.y())
                self.scene.history.storeHistory("Created node %s" % node.__class__.__name__)
            except Exception as e: dumpException(e)


            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()
    def filechoose(self):
        fname, filter = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self, 'Open graph from file', self.getFileDialogDirectory(), self.getFileDialogFilter())
        print(fname, filter)
    def LuComboBox(self):
        global lb5,lb6
        self.window = PyQt5.QtWidgets.QMainWindow()
        self.window.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint)
        self.window.setWindowTitle("Action Descriptor")

        self.window.setGeometry(200,200,400,100)

        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        lb1 = QLabel("delimiter:")
        variableManager.lulb2 = QLineEdit("")
        variableManager.lulb2.setFrame(False)
        variableManager.lulb2.setText(variableManager.lulb2_txt)
        lb3 = QPushButton('Chose filename')
        variableManager.lulb4 = QLabel("inputFile:-")
        lb5 = QLabel("")
        lb5.setText(variableManager.last_name_lu)
        lb6 = QPushButton('Done')

        g_layout = PyQt5.QtWidgets.QGridLayout()
        g_layout.addWidget(lb1,0,0)
        g_layout.addWidget(variableManager.lulb2,0,1)
        g_layout.addWidget(lb3,1,1)
        g_layout.addWidget(variableManager.lulb4, 2, 0)
        g_layout.addWidget(lb5, 2, 1)
        g_layout.addWidget(lb6,3,1,1,1)
        central_widget.setLayout(g_layout)
        #lb2.clicked.connect(self.filechoose)
        lb3.clicked.connect(self.Luclicker)
        lb6.setDisabled(True)
        lb6.clicked.connect(self.window.close)
        self.window.setWindowModality(Qt.ApplicationModal)
        self.window.show()
        variableManager.lulb2.textChanged.connect(self.lulb2_textchanged)

    def lulb2_textchanged(self):
        variableManager.lulb2_txt = variableManager.lulb2.text()
    def Luclicker(self):
        global lb6
        lb6.setDisabled(False)
        fname = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self,"Choose File", "","CSV Files (*.csv)"+ ";;" +"xlsx Files (*.xlsx)")
        if fname:
            variableManager.lulb2_txt = variableManager.lulb2.text()
            variableManager.last_name_lu = fname[0].split('/')[-1]
            lb5.setText(variableManager.last_name_lu)

    def MfComboBox(self):
        global lb5,lb6
        self.window = PyQt5.QtWidgets.QMainWindow()
        self.window.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint)
        self.window.setWindowTitle("Action Descriptor")

        self.window.setGeometry(200,200,400,100)

        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        lb1 = QLabel("delimiter:")
        variableManager.mflb2 = QLineEdit("")
        variableManager.mflb2.setFrame(False)
        variableManager.mflb2.setText(variableManager.mflb2_txt)
        lb3 = QPushButton('Chose filename')
        variableManager.mflb4 = QLabel("inputFile:-")
        lb5 = QLabel("")
        lb5.setText(variableManager.last_name_mf)
        lb6 = QPushButton('Done')

        g_layout = PyQt5.QtWidgets.QGridLayout()
        g_layout.addWidget(lb1,0,0)
        g_layout.addWidget(variableManager.mflb2,0,1)
        g_layout.addWidget(lb3,1,1)
        g_layout.addWidget(variableManager.mflb4, 2, 0)
        g_layout.addWidget(lb5, 2, 1)
        g_layout.addWidget(lb6,3,1,1,1)
        central_widget.setLayout(g_layout)
        #lb2.clicked.connect(self.filechoose)
        lb3.clicked.connect(self.mfclicker)
        lb6.setDisabled(True)
        lb6.clicked.connect(self.window.close)
        self.window.setWindowModality(Qt.ApplicationModal)
        self.window.show()
        variableManager.mflb2.textChanged.connect(self.mflb2_textchanged)

    def mflb2_textchanged(self):
        variableManager.mflb2_txt = variableManager.mflb2.text()
    def mfclicker(self):
        global lb6
        lb6.setDisabled(False)
        fname = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self,"Choose File", "","CSV Files (*.csv)"+ ";;" +"xlsx Files (*.xlsx)")
        if fname:
            variableManager.mflb2_txt = variableManager.mflb2.text()
            variableManager.last_name_mf = fname[0].split('/')[-1]
            lb5.setText(variableManager.last_name_mf)

    def UmComboBox(self):
        global lb5,lb6
        self.window = PyQt5.QtWidgets.QMainWindow()
        self.window.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint)
        self.window.setWindowTitle("Action Descriptor")

        self.window.setGeometry(200,200,400,100)

        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        lb1 = QLabel("delimiter:")
        variableManager.umlb2 = QLineEdit("")
        variableManager.umlb2.setFrame(False)
        variableManager.umlb2.setText(variableManager.umlb2_txt)
        lb3 = QPushButton('Chose filename')
        lb4 = QLabel("inputFile:-")
        lb5 = QLabel("")
        lb5.setText(variableManager.last_name_um)
        lb6 = QPushButton('Done')

        g_layout = PyQt5.QtWidgets.QGridLayout()
        g_layout.addWidget(lb1,0,0)
        g_layout.addWidget(variableManager.umlb2,0,1)
        g_layout.addWidget(lb3,1,1)
        g_layout.addWidget(lb4, 2, 0)
        g_layout.addWidget(lb5, 2, 1)
        g_layout.addWidget(lb6,3,1,1,1)
        central_widget.setLayout(g_layout)
        #lb2.clicked.connect(self.filechoose)
        lb3.clicked.connect(self.umclicker)
        lb6.setDisabled(True)
        lb6.clicked.connect(self.window.close)
        self.window.setWindowModality(Qt.ApplicationModal)
        self.window.show()
        variableManager.umlb2.textChanged.connect(self.umlb2_textchanged)

    def umlb2_textchanged(self):
        variableManager.umlb2_txt = variableManager.umlb2.text()
    def umclicker(self):
        global lb6
        lb6.setDisabled(False)
        fname = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self,"Choose File", "","CSV Files (*.csv)"+ ";;" +"xlsx Files (*.xlsx)")
        if fname:
            variableManager.umlb2_txt = variableManager.umlb2.text()
            variableManager.last_name_um = fname[0].split('/')[-1]
            lb5.setText(variableManager.last_name_um)

    def CdComboBox(self):
        self.window = PyQt5.QtWidgets.QMainWindow()
        self.window.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint)
        self.window.setWindowTitle("Action Descriptor")
        self.window.setGeometry(200,200,400,100)

        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)

        lb1 = QLabel("targetField:")
        variableManager.cdlb2 = QLineEdit()
        model = QStringListModel(variableManager.outlist)
        completer = SubstringCompleter(variableManager.cdlb2)
        completer.setModel(model)
        variableManager.cdlb2.setCompleter(completer)
        variableManager.cdlb2.setFrame(True)
        variableManager.cdselected_items_list = QLabel()
        variableManager.cdselected_items_list.setText(variableManager.cdlabel_txt)

        lb3 = QLabel("targetValue:")
        variableManager.cdlb4 = QLineEdit("")
        variableManager.cdlb4.setText(variableManager.cdlb4_txt)
        variableManager.cdlb4.textChanged.connect(self.update_cdlabel4_text)

        lb5 = QLabel("delimiter:")
        variableManager.cdlb6 = QLineEdit("")
        variableManager.cdlb6.setText(variableManager.cdlb6_txt)
        variableManager.cdlb6.textChanged.connect(self.update_cdlabel6_text)
        variableManager.cdlb6.setFrame(False)

        done_button = QPushButton("Done")
        done_button.clicked.connect(self.window.close)

        g_layout = QGridLayout()
        g_layout.addWidget(lb1, 0, 0)
        g_layout.addWidget(variableManager.cdlb2, 0, 1)
        g_layout.addWidget(variableManager.cdselected_items_list, 1, 1, 1, 1)
        g_layout.addWidget(lb3, 2, 0)
        g_layout.addWidget(variableManager.cdlb4, 2, 1)
        g_layout.addWidget(lb5, 3, 0)
        g_layout.addWidget(variableManager.cdlb6, 3, 1)
        g_layout.addWidget(done_button, 4, 1, 1, 1)
        central_widget.setLayout(g_layout)

        self.window.setWindowModality(Qt.ApplicationModal)
        self.window.show()

        completer.activated.connect(self.on_completer_activated)

    def update_cdlabel4_text(self):
        variableManager.cdlb4_txt = variableManager.cdlb4.text()

    def update_cdlabel6_text(self):
        variableManager.cdlb6_txt = variableManager.cdlb6.text()

    def on_completer_activated(self, text):
        variableManager.cdselected_items.append(text)
        variableManager.cdselected_items_list.setText(', '.join(variableManager.cdselected_items))
        variableManager.cdlabel_txt = variableManager.cdselected_items_list.text()

    def addComboBox(self):
        self.window = PyQt5.QtWidgets.QMainWindow()
        self.window.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint)
        self.window.setWindowTitle("Action Descriptor")
        self.window.setGeometry(200,200,400,100)

        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)

        lb1 = QLabel("targetValue:")
        variableManager.addlb2 = QLineEdit("")
        variableManager.addlb2.setText(variableManager.addlb2_txt)
#        variableManager.addlb2.textChanged.connect(self.update_addlabel2_text)

        lb3 = QLabel("delimiter:")
        variableManager.addlb4 = QLineEdit("")
        variableManager.addlb4.setText(variableManager.addlb4_txt)
 #       variableManager.addlb4.textChanged.connect(self.update_addlabel4_text)
        variableManager.addlb4.setFrame(False)

        done_button = QPushButton("Done")
        done_button.clicked.connect(self.window.close)

        g_layout = QGridLayout()
        g_layout.addWidget(lb1, 0, 0)
        g_layout.addWidget(variableManager.addlb2, 0, 1)
        g_layout.addWidget(lb3, 2, 0)
        g_layout.addWidget(variableManager.addlb4, 2, 1)
        g_layout.addWidget(done_button, 4, 1, 1, 1)
        central_widget.setLayout(g_layout)

        self.window.setWindowModality(Qt.ApplicationModal)
        self.window.show()


    def contextMenuEvent(self, event):
        global n, lb5
        try:
            item = self.scene.getItemAt(event.pos())

            #title = item.title
            if DEBUG_CONTEXT: print(item)
            n = item.node
            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(n, 'action_lu'):
                self.LuADContextMenu(event)
                lookup_filename = variableManager.last_name_lu
                print(lookup_filename)
            elif hasattr(n, 'action_add'):
                self.addADContextMenu(event)
                lookup_filename = variableManager.last_name_add
                print(lookup_filename)
            elif hasattr(n, 'action_mf'):
                self.MfADContextMenu(event)
                movefield_filename = variableManager.last_name_mf
                print(movefield_filename)
            elif hasattr(n, 'action_um'):
                self.UmADContextMenu(event)
                usemap_filename = variableManager.last_name_um
                print(usemap_filename)
            elif hasattr(n, 'action_cd'):
                self.CdADContextMenu(event)
                # copydata_filename = variableManager.last_name_cd
                # print(copydata_filename)
            elif hasattr(item, 'node') and hasattr(item, 'title'):
                print(item)
                self.handleInputFieldContextMenu(event)
            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event)
            elif hasattr(item, 'node') and hasattr(item, 'action_lu'):
                self.handleLookUpContextMenu(event)
            #elif item is None:
            #else:
                 #self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e: dumpException(e)


    def handleInputFieldContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: InputField")
        context_menu = QMenu(self)
        first = context_menu.addAction("First")
        second = context_menu.addAction("Second")
        third = context_menu.addAction("Third")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
    def LuADContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: NODE")
        context_menu = QMenu(self)
        file_name = context_menu.addAction("Action Descriptor")
        #file_name.setCheckable(True)
        file_name.triggered.connect(self.LuComboBox)
        #delimiter = context_menu.addAction("Delimiter")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

    def MfADContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: NODE")
        context_menu = QMenu(self)
        file_name = context_menu.addAction("Action Descriptor")
        #file_name.setCheckable(True)
        file_name.triggered.connect(self.MfComboBox)
        #delimiter = context_menu.addAction("Delimiter")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

    def UmADContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: NODE")
        context_menu = QMenu(self)
        file_name = context_menu.addAction("Action Descriptor")
        #file_name.setCheckable(True)
        file_name.triggered.connect(self.UmComboBox)
        #delimiter = context_menu.addAction("Delimiter")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

    def addADContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: NODE")
        context_menu = QMenu(self)
        file_name = context_menu.addAction("Action Descriptor")
        #file_name.setCheckable(True)
        file_name.triggered.connect(self.addComboBox)
        #delimiter = context_menu.addAction("Delimiter")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

    def CdADContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: NODE")
        context_menu = QMenu(self)
        file_name = context_menu.addAction("Action Descriptor")
                #file_name.setCheckable(True)
        file_name.triggered.connect(self.CdComboBox)
        print("variable.lb2 =", type(variableManager.cdlb2))
                #delimiter = context_menu.addAction("Delimiter")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

    def pressed(self):
        print("clicked")

        selected = None
        # item = self.scene.getItemAt(event.pos())
        # if type(item) == QGraphicsProxyWidget:
        #     item = item.widget()
        #
        # if hasattr(item, 'node'):
        #     selected = item.node
        # # if hasattr(item, 'socket'):
        # #     selected = item.socket.node
        #
        # # if DEBUG_CONTEXT: print("got item:", selected)
        # # if selected and action == markDirtyAct: selected.markDirty()
        # # if selected and action == markDirtyDescendantsAct: selected.markDescendantsDirty()
        # # if selected and action == markInvalidAct: selected.markInvalid()
        # # if selected and action == unmarkInvalidAct: selected.markInvalid(False)
        # # if selected and action == evalAct:
        # #     val = selected.eval()
        # #     if DEBUG_CONTEXT: print("EVALUATED:", val)


    def handleEdgeContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: EDGE")
        context_menu = QMenu(self)
        bezierAct = context_menu.addAction("Bezier Edge")
        directAct = context_menu.addAction("Direct Edge")
        squareAct = context_menu.addAction("Square Edge")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())
        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezierAct: selected.edge_type = EDGE_TYPE_BEZIER
        if selected and action == directAct: selected.edge_type = EDGE_TYPE_DIRECT
        if selected and action == squareAct: selected.edge_type = EDGE_TYPE_SQUARE

    # helper functions
    def determine_target_socket_of_node(self, was_dragged_flag, new_calc_node):
        target_socket = None
        if was_dragged_flag:
            if len(new_calc_node.inputs) > 0: target_socket = new_calc_node.inputs[0]
        else:
            if len(new_calc_node.outputs) > 0: target_socket = new_calc_node.outputs[0]
        return target_socket

    def finish_new_node_state(self, new_calc_node):
        self.scene.doDeselectItems()
        new_calc_node.grNode.doSelect(True)
        new_calc_node.grNode.onSelected()


    def handleNewNodeContextMenu(self, event):

        if DEBUG_CONTEXT: print("CONTEXT: EMPTY SPACE")
        context_menu = self.initNodesContextMenu()
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            new_calc_node = get_class_from_opcode(action.data())(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            new_calc_node.setPos(scene_pos.x(), scene_pos.y())
            if DEBUG_CONTEXT: print("Selected node:", new_calc_node)

            if self.scene.getView().mode == MODE_EDGE_DRAG:
                # if we were dragging an edge...
                target_socket = self.determine_target_socket_of_node(self.scene.getView().dragging.drag_start_socket.is_output, new_calc_node)
                if target_socket is not None:
                    self.scene.getView().dragging.edgeDragEnd(target_socket.grSocket)
                    self.finish_new_node_state(new_calc_node)

            else:
                self.scene.history.storeHistory("Created %s" % new_calc_node.__class__.__name__)
