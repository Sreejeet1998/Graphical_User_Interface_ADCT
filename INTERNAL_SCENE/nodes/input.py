from PyQt5.QtWidgets import QLabel
from qtpy.QtWidgets import QLineEdit
from qtpy.QtCore import Qt
from INTERNAL_SCENE.calc_conf import register_node, OP_NODE_INPUT, OP_NODE_FIELD
from INTERNAL_SCENE.calc_node_base import CalcNode, CalcGraphicsNode
from GUIWINDOW.node_content_widget import QDMNodeContentWidget
from GUIWINDOW.utils import dumpException

class FieldNameContent(QDMNodeContentWidget):
    def initUI(self):
        self.FNbox = QLabel("FieldName",self)
        self.FNbox.setAlignment(Qt.AlignHCenter)
        self.FNbox.setObjectName(self.node.content_label_objname)

    def serialize(self):
        res = super().serialized()
        res['FieldName'] = self.edit.text()
        return res

    @register_node(OP_NODE_FIELD)
    class CalcNode_Input(CalcNode):
        icon = "icons/in.png"
        op_code = OP_NODE_FIELD
        op_title = "Field Name"
        content_label_objname = "calc_node_field"

        def __init__(self, scene):
            super().__init__(scene, inputs=[], outputs=[3])
class calcInputContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setObjectName(self.node.content_label_objname)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
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

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcInputContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        u_value = self.content.edit.text()
        s_value = int(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        return self.value