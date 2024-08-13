from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import re

from GUIWINDOW.node_node import Node
from INTERNAL_SCENE.calc_conf import register_node, OP_NODE_OUTPUT, OP_NODE_INPUT, OP_NODE_DELETE, OP_NODE_LOOKUP, \
    OP_NODE_MOVEFIELD, OP_NODE_COPYDATA, OP_NODE_USEMAP, OP_NODE_ADD
from INTERNAL_SCENE.calc_node_base import CalcNode, CalcGraphicsNode, CalcContent
from GUIWINDOW.node_content_widget import QDMNodeContentWidget
from GUIWINDOW.utils import dumpException
#res = ''
field_name = ""
@register_node(OP_NODE_DELETE)
class CalcNode_delete(CalcNode):

    op_code = OP_NODE_DELETE
    op_title = "deleteField"
    content_label_objname = "calc_node_output"
    Nd_number = 1
    #Fname = CalculatorWindow.onOSFile.output[0]
    action_del = '"action":["deleteField"]},'
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])




# class CalcNode(Node):
#     #edit = QLineEdit("")
#     icon = ""
#     op_code = 0
#     op_title = "Undefined"
#     content_label = ""
#     content_label_objname = "calc_node_bg"
#
#     GraphicsNode_class = CalcGraphicsNode
#     NodeContent_class = CalcContent
#
#     def __init__(self, scene, inputs=[2], outputs=[1]):
#         super().__init__(scene, self.__class__.op_title, inputs, outputs)
@register_node(OP_NODE_LOOKUP)
class CalcNode_LookUp(CalcNode):
    op_code = OP_NODE_LOOKUP
    op_title = "lookUp"
    content_label_objname = "calc_node_lookup"
    Nd_number = 2
    action_lu = '"action": ["lookUp"]},'
    #UIComponents()

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])
        # self.Action_Descriptor = QMenu(self)
        # file_Chooser = self.Action_Descriptor.addAction("File Name")
        # delimiter = self.Action_Descriptor.addAction("Delimiter")
    # def contextMenuEvent(self,event):
    #     self.Action_Descriptor.exec_(self.mapToGlobal(event.pos()))
@register_node(OP_NODE_MOVEFIELD)
class CalcNode_MoveField(CalcNode):
    op_code = OP_NODE_MOVEFIELD
    op_title = "moveField"
    content_label_objname = "calc_node_movefield"
    Nd_number = 3
    action_mf = '"action": ["moveField"]},'
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])

@register_node(OP_NODE_COPYDATA)
class CalcNode_CopyData(CalcNode):
    op_code = OP_NODE_COPYDATA
    op_title = "copyData"
    content_label_objname = "calc_node_copydata"
    Nd_number = 4
    action_cd = '"action":["copyData"]},'
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])

@register_node(OP_NODE_USEMAP)
class CalcNode_UseMap(CalcNode):
    op_code = OP_NODE_USEMAP
    op_title = "useMap"
    content_label_objname = "calc_node_usemap"
    Nd_number = 5
    action_um = '"action": ["useMap"]},'
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])

@register_node(OP_NODE_ADD)
class CalcNode_add(CalcNode):
    op_code = OP_NODE_ADD
    op_title = "add"
    content_label_objname = "calc_node_add"
    Nd_number = 8
    action_add = ""
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])

#@register_node(OP_NODE_INPUT)
#class CalcNode_Input(CalcNode):
    #context_menu = QMenu()
    #markDirtyAct = context_menu.addAction("Mark Dirty")
#    op_code = OP_NODE_INPUT
#    op_title = "Input"
#    content_label_objname = "calc_node_output"
#    Nd_number = 6
    #Fname = CalculatorWindow.onOSFile.output[0]
#    f1 = {"DefaultName":CalcNode_Delete.f2}
#    def __init__(self, scene):
#        super().__init__(scene, inputs=[], outputs=[2])
class calcInputContent(QDMNodeContentWidget):
    def initUI(self):
        from INTERNAL_SCENE.calc_sub_window import variableManager

        self.edit = QLineEdit(self)

        # Set up the completer with substring matching and case-insensitive mode
        completer = QCompleter(variableManager.outlist, self)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.edit.setCompleter(completer)

        popup = completer.popup()
        popup.setMinimumWidth(400)
        popup.setMinimumHeight(150)

        self.layout = QGridLayout()
        self.layout.addWidget(self.edit, 1, 1)
        self.Nd_number = 6

    def serialize(self):
        res = super().serialize()
        v = self.edit.text()
        from INTERNAL_SCENE.calc_sub_window import variableManager
        if v not in variableManager.input_box_name_list:
            variableManager.input_box_name_list.append(v)
        res['value'] = self.edit.text()
        print("Output-Serialize = VM.input_box_name_list = ", variableManager.input_box_name_list)
        return str(res)

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        print("Yes DEserialize - ", res)
        try:
            pattern = r'\w\S*@*.\w'
            value = re.findall(pattern, data)
            print("Value =", value)
            if value:
                value = value[-1]
                self.edit.setText(value)
                global field_name
                field_name = self.edit.text()  # Corrected this line to get the text
                return True & res
        except Exception as e:
            dumpException(e)
        return res

    # def initUI(self):
    #     from INTERNAL_SCENE.calc_sub_window import variableManager
    #     self.edit = QLineEdit(self)
    #     completer = QCompleter(variableManager.outlist,self)
    #     completer.setCaseSensitivity(True)
    #     self.edit.setCompleter(completer)
    #     self.layout = QGridLayout()
    #     self.layout.addWidget(self.edit,0,0)
    #     #self.edit.setAlignment(Qt.AlignRight)
    #     #self.edit.setObjectName(self.node.content_label_objname)
    #     self.Nd_number = 6
    #
    # def serialize(self):
    #     global n_list
    #     res = super().serialize()
    #     v = self.edit.text()
    #     n_list.append(v) if v not in n_list else n_list
    #     res['value'] = self.edit.text()
    #     print(n_list)
    #     return str(res)
    #
    # def deserialize(self, data, hashmap={}):
    #     res = super().deserialize(data, hashmap)
    #     print("Yes DEserialize - ",res)
    #     try:
    #         pattern = r'\w\S*@*.\w'
    #         value = re.findall(pattern, data)
    #         print("Value =", value)
    #         value = value[-1]
    #         #value = data.split()
    #         print("Value =",value)
    #         self.edit.setText(value)
    #         global field_name
    #         field_name = self.edit.setText(value)
    #         return True & res
    #     except Exception as e:
    #         dumpException(e)
    #     return res


@register_node(OP_NODE_INPUT)
class CalcNode_Input(CalcNode):
    icon = "icons/in.png"
    op_code = OP_NODE_INPUT
    op_title = "Input"
    content_label_objname = "calc_node_input"
    Nd_number = 6

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = calcInputContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        u_value = self.content.edit.text()
        #global field_name
        #field_name = u_value
        s_value = int(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        return self.value

class CalcOutputContent(QDMNodeContentWidget):
    def initUI(self):
        layout = QVBoxLayout()

        self.file_btn = QPushButton("Create script file", self)
        self.file_btn.clicked.connect(self.choosefile)
        layout.addWidget(self.file_btn)

        self.lbl = QLabel("",self)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setObjectName(self.node.content_label_objname)
        layout.addWidget(self.lbl)

        self.setLayout(layout)
        self.Nd_number = 7

    def choosefile(self):
        from INTERNAL_SCENE.calc_sub_window import variableManager
        variableManager.file_path = QFileDialog.getSaveFileName(self, "Create File","","JSON Files (*.json)"+";;"+"All Files(*)")
        variableManager.file_path = str(variableManager.file_path[0])
        if variableManager.file_path:
            pattern = r'\b\w+\b'
            filename = re.findall(pattern,variableManager.file_path)
            self.lbl.setText(filename[-1])

    def serialize(self):
        res = super().serialize()
        res['value'] = self.lbl.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.lbl.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res

@register_node(OP_NODE_OUTPUT)
class CalcNode_Output(CalcNode):
    op_code = OP_NODE_OUTPUT
    op_title = "Output"

    content_label_objname = "calc_node_output"
    Nd_number = 7
    #if Edge.remove_from_sockets.nei == 0:f = {"Fields": {}}

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])


    def initInnerClasses(self):
        self.content = CalcOutputContent(self)
        self.grNode = CalcGraphicsNode(self)
        #self.content.lbl.textChanged.connect(self.onOutputChanged)

    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        val = input_node.eval()

        if val is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return
        self.content.lbl.setText("%d" % val)
        self.markInvalid(False)
        self.markDirty(False)

        u_value = self.content.lbl.text()
        s_value = int(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        return val

