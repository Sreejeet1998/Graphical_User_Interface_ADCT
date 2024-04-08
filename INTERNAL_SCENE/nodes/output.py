from qtpy.QtWidgets import *
from qtpy.QtCore import Qt

import INTERNAL_SCENE.calc_window
import GUIWINDOW.node_scene
from INTERNAL_SCENE.calc_conf import register_node, OP_NODE_OUTPUT, OP_NODE_INPUT, OP_NODE_DELETE, OP_NODE_LOOKUP, \
    OP_NODE_MOVEFIELD, OP_NODE_COPYDATA, OP_NODE_USEMAP
from INTERNAL_SCENE.calc_node_base import CalcNode, CalcGraphicsNode
#from INTERNAL_SCENE.calc_window import CalculatorWindow
from GUIWINDOW.node_content_widget import QDMNodeContentWidget
from GUIWINDOW.node_edge import Edge
from GUIWINDOW.utils import dumpException

field_name = ""
@register_node(OP_NODE_DELETE)
class CalcNode_delete(CalcNode):
    op_code = OP_NODE_DELETE
    op_title = "deleteField"
    content_label_objname = "calc_node_output"
    Nd_number = 1
    #Fname = CalculatorWindow.onOSFile.output[0]
    f2 = {"name":{"action":["deleteField"]}}
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])



@register_node(OP_NODE_LOOKUP)
class CalcNode_LookUp(CalcNode):
    op_code = OP_NODE_LOOKUP
    op_title = "lookUp"
    content_label_objname = "calc_node_lookup"
    Nd_number = 2
    f2 = {"name":{"action": ["lookUp"]}}

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])

@register_node(OP_NODE_MOVEFIELD)
class CalcNode_MoveField(CalcNode):
    op_code = OP_NODE_MOVEFIELD
    op_title = "moveField"
    content_label_objname = "calc_node_movefield"
    Nd_number = 3
    f2 = {"name":{"action": ["moveField"]}}
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])

@register_node(OP_NODE_COPYDATA)
class CalcNode_CopyData(CalcNode):
    op_code = OP_NODE_COPYDATA
    op_title = "copyData"
    content_label_objname = "calc_node_copydata"
    Nd_number = 4
    f2 = {"name":{"action":["copyData"]}}
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2])

@register_node(OP_NODE_USEMAP)
class CalcNode_UseMap(CalcNode):
    op_code = OP_NODE_USEMAP
    op_title = "useMap"
    content_label_objname = "calc_node_usemap"
    Nd_number = 5
    f2 = {"name":{"action": ["useMap"]}}
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
        self.edit = QLineEdit("", self)
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setObjectName(self.node.content_label_objname)
        self.Nd_number = 6
        #field_name = self.edit
        print(self.edit)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return str(res)

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            global field_name
            field_name = self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res


@register_node(OP_NODE_INPUT)
class CalcNode_Input(CalcNode):
    icon = "icons/in.png"
    op_code = OP_NODE_INPUT
    op_title = "Input"
    content_label_objname = "calc_node_input"
    Nd_number = 6

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
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
    f1 = {"name":CalcNode_delete.f2}
    f = field_name

class CalcOutputContent(QDMNodeContentWidget):
    def initUI(self):
        self.lbl = QLabel("", self)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setObjectName(self.node.content_label_objname)
        self.Nd_number = 7
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
