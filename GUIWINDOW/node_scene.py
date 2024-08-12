# -*- coding: utf-8 -*-
"""
A module containing the representation of the NodeEditor's Scene
"""
import os, sys, json
from array import array
from collections import OrderedDict

import INTERNAL_SCENE.nodes.output
from INTERNAL_SCENE import calc_node_base
from INTERNAL_SCENE.calc_node_base import CalcNode

from GUIWINDOW import node_node, node_graphics_node
from GUIWINDOW.utils_no_qt import dumpException, pp
from GUIWINDOW.node_serializable import Serializable
from GUIWINDOW.node_graphics_scene import QDMGraphicsScene
from GUIWINDOW.node_node import Node
from GUIWINDOW.node_edge import Edge
from GUIWINDOW.node_scene_history import SceneHistory
from GUIWINDOW.node_scene_clipboard import SceneClipboard

from INTERNAL_SCENE.nodes.output import calcInputContent
from INTERNAL_SCENE.calc_conf import CALC_NODES
DEBUG_REMOVE_WARNINGS = False
fields = {"Fields": {}}
d = ""
class InvalidFile(Exception): pass


class Scene(Serializable):
    """Class representing NodeEditor's `Scene`"""
    def __init__(self):
        """
        :Instance Attributes:

            - **nodes** - list of `Nodes` in this `Scene`
            - **edges** - list of `Edges` in this `Scene`
            - **history** - Instance of :class:`~GUIWINDOW.node_scene_history.SceneHistory`
            - **clipboard** - Instance of :class:`~GUIWINDOW.node_scene_clipboard.SceneClipboard`
            - **scene_width** - width of this `Scene` in pixels
            - **scene_height** - height of this `Scene` in pixels
        """
        super().__init__()
        self.flag = 0
        #self.node = None
        self.nodes = []
        self.edges = []

        # current filename assigned to this scene
        self.filename = None

        self.scene_width = 64000
        self.scene_height = 64000

        # custom flag used to suppress triggering onItemSelected which does a bunch of stuff
        self._silent_selection_events = False

        self._has_been_modified = False
        self._last_selected_items = None

        # initialize all listeners
        self._has_been_modified_listeners = []
        self._item_selected_listeners = []
        self._items_deselected_listeners = []

        # here we can store callback for retrieving the class for Nodes
        self.node_class_selector = None

        self.initUI()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)


    @property
    def has_been_modified(self):
        """
        Has this `Scene` been modified?

        :getter: ``True`` if the `Scene` has been modified
        :setter: set new state. Triggers `Has Been Modified` event
        :type: ``bool``
        """
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            # set it now, because we will be reading it soon
            self._has_been_modified = value

            # call all registered listeners
            for callback in self._has_been_modified_listeners: callback()

        self._has_been_modified = value

    def initUI(self):
        """Set up Graphics Scene Instance"""
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    def getNodeByID(self, node_id: int):
        """
        Find node in the scene according to provided `node_id`

        :param node_id: ID of the node we are looking for
        :type node_id: ``int``
        :return: Found ``Node`` or ``None``
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None


    def setSilentSelectionEvents(self, value: bool=True):
        """Calling this can suppress onItemSelected events to be triggered. This is useful when working with clipboard"""
        self._silent_selection_events = value

    def onItemSelected(self, silent: bool=False):
        """
        Handle Item selection and trigger event `Item Selected`

        :param silent: If ``True`` scene's onItemSelected won't be called and history stamp not stored
        :type silent: ``bool``
        """
        if self._silent_selection_events: return

        current_selected_items = self.getSelectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            if not silent:
                # we could create some kind of UI which could be serialized,
                # therefore first run all callbacks...
                for callback in self._item_selected_listeners: callback()
                # and store history as a last step always
                self.history.storeHistory("Selection Changed")

    def onItemsDeselected(self, silent: bool=False):
        """
        Handle Items deselection and trigger event `Items Deselected`

        :param silent: If ``True`` scene's onItemsDeselected won't be called and history stamp not stored
        :type silent: ``bool``
        """
        # somehow this event is being triggered when we start dragging file outside of our application
        # or we just loose focus on our app? -- which does not mean we've deselected item in the scene!
        # double check if the selection has actually changed, since
        current_selected_items = self.getSelectedItems()
        if current_selected_items == self._last_selected_items:
            # print("Qt itemsDeselected Invalid Event! Ignoring")
            return

        self.resetLastSelectedStates()
        if current_selected_items == []:
            self._last_selected_items = []
            if not silent:
                self.history.storeHistory("Deselected Everything")
                for callback in self._items_deselected_listeners: callback()


    def isModified(self) -> bool:
        """Is this `Scene` dirty aka `has been modified` ?

        :return: ``True`` if `Scene` has been modified
        :rtype: ``bool``
        """
        return self.has_been_modified

    def getSelectedItems(self) -> list:
        """
        Returns currently selected Graphics Items

        :return: list of ``QGraphicsItems``
        :rtype: list[QGraphicsItem]
        """
        return self.grScene.selectedItems()

    def doDeselectItems(self, silent: bool=False) -> None:
        """
        Deselects everything in scene

        :param silent: If ``True`` scene's onItemsDeselected won't be called
        :type silent: ``bool``
        """
        for item in self.getSelectedItems():
            item.setSelected(False)
        if not silent:
            self.onItemsDeselected()

    # our helper listener functions
    def addHasBeenModifiedListener(self, callback: 'function'):
        """
        Register callback for `Has Been Modified` event

        :param callback: callback function
        """
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback: 'function'):
        """
        Register callback for `Item Selected` event

        :param callback: callback function
        """
        self._item_selected_listeners.append(callback)

    def addItemsDeselectedListener(self, callback: 'function'):
        """
        Register callback for `Items Deselected` event

        :param callback: callback function
        """
        self._items_deselected_listeners.append(callback)

    def addDragEnterListener(self, callback: 'function'):
        """
        Register callback for `Drag Enter` event

        :param callback: callback function
        """
        self.getView().addDragEnterListener(callback)

    def addDropListener(self, callback: 'function'):
        """
        Register callback for `Drop` event

        :param callback: callback function
        """
        self.getView().addDropListener(callback)

    # custom flag to detect node or edge has been selected....
    def resetLastSelectedStates(self):
        """Resets internal `selected flags` in all `Nodes` and `Edges` in the `Scene`"""
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._last_selected_state = False

    def getView(self) -> 'QGraphicsView':
        """Shortcut for returning `Scene` ``QGraphicsView``

        :return: ``QGraphicsView`` attached to the `Scene`
        :rtype: ``QGraphicsView``
        """
        return self.grScene.views()[0]

    def getItemAt(self, pos: 'QPointF'):
        """Shortcut for retrieving item at provided `Scene` position

        :param pos: scene position
        :type pos: ``QPointF``
        :return: Qt Graphics Item at scene position
        :rtype: ``QGraphicsItem``
        """
        return self.getView().itemAt(pos)

    def addNode(self, node: Node):
        """Add :class:`~GUIWINDOW.node_node.Node` to this `Scene`

        :param node: :class:`~GUIWINDOW.node_node.Node` to be added to this `Scene`
        :type node: :class:`~nodeeditor.node_node.Node`
        """
        self.nodes.append(node)
        #self.flag = self.nodes.Nd_number

    def addEdge(self, edge: Edge):
        """Add :class:`~GUIWINDOW.node_edge.Edge` to this `Scene`

        :param edge: :class:`~GUIWINDOW.node_edge.Edge` to be added to this `Scene`
        :return: :class:`~GUIWINDOW.node_edge.Edge`
        """
        self.edges.append(edge)

    def removeNode(self, node: Node):
        """Remove :class:`~GUIWINDOW.node_node.Node` from this `Scene`

        :param node: :class:`~GUIWINDOW.node_node.Node` to be removed from this `Scene`
        :type node: :class:`~nodeeditor.node_node.Node`
        """
        if node in self.nodes: self.nodes.remove(node)
        else:
            if DEBUG_REMOVE_WARNINGS: print("!W:", "Scene::removeNode", "wanna remove GUIWINDOW", node,
                                            "from self.nodes but it's not in the list!")

    def removeEdge(self, edge: Edge):
        """Remove :class:`~GUIWINDOW.node_edge.Edge` from this `Scene`

        :param edge: :class:`~GUIWINDOW.node_edge.Edge` to be remove from this `Scene`
        :return: :class:`~GUIWINDOW.node_edge.Edge`
        """
        if edge in self.edges: self.edges.remove(edge)
        else:
            if DEBUG_REMOVE_WARNINGS: print("!W:", "Scene::removeEdge", "wanna remove edge", edge,
                                            "from self.edges but it's not in the list!")


    def clear(self):
        """Remove all `Nodes` from this `Scene`. This causes also to remove all `Edges`"""
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False


    def saveToFile(self, filename: str):
        """
        Save this `Scene` to the file on disk.

        :param filename: where to save this scene
        :type filename: ``str``
        """
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
            # print("saving to", filename, "was successfull.")

            self.has_been_modified = False
            self.filename = filename


    def dumpJson(self,filename:str):
        #from INTERNAL_SCENE.nodes.output import n_list
        from INTERNAL_SCENE.calc_sub_window import variableManager
        from INTERNAL_SCENE.calc_window import filepath
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        global fields,d
        fields = {"Fields": {}}
        act = {"action":[]}
        count = 0
        for i in range(len(variableManager.input_box_name_list)-1):
            if variableManager.input_box_name_list[i] == "":
                variableManager.input_box_name_list.pop(i)
                p_list = variableManager.input_box_name_list
            else:
                p_list = variableManager.input_box_name_list
        #print("yeah",outlist)
        if len(edges) > 1:
            for i in range(len(variableManager.opcode)):
                # global fields
                print("it is fiilepath:",filepath)
                #outlist = json.dumps(outlist)
                #print("Outlist",outlist)
                #finame = outlist[i]
                if variableManager.opcode[i] == 1:
                    count = count+1
                    #hold = outlist[i]
                    #f_name = {outlist[i]:{}}
                    act = {"action":[]}
                    j = p_list.pop(0)
                    hold = j
                    f_name = {j:{}}
                    fields["Fields"].update(f_name)
                    print(fields)
                    print("count",count)
                elif variableManager.opcode[i] == 2:
                    pass
                elif variableManager.opcode[i] == 3:
                    act["action"].append("lookUp")

                    from INTERNAL_SCENE.calc_sub_window import variableManager
                    print("Lastname ======== ",variableManager.last_name_lu)
                    print("lb2",variableManager.lulb2)
                    if variableManager.last_name_lu == "":
                        f_name[hold].update(act)
                    else:
                        act["lookUp"] = {"inputFile":variableManager.last_name_lu,"delimiter":variableManager.lulb2_txt}
                        f_name[hold].update(act)
                    print(fields)
                elif variableManager.opcode[i] == 4:
                    act["action"].append("moveField")

                    from INTERNAL_SCENE.calc_sub_window import variableManager
                    if variableManager.last_name_mf == "":
                        f_name[hold].update(act)
                    else:
                        act["moveField"] = {"inputFile":variableManager.last_name_mf,"delimiter":variableManager.mflb2_txt}
                        f_name[hold].update(act)
                    print(fields)
                elif variableManager.opcode[i] == 5:
                    act["action"].append("copyData")

                    from INTERNAL_SCENE.calc_sub_window import variableManager
                    if variableManager.cdlabel_txt == "":
                        f_name[hold].update(act)
                        print("yess cd")
                    else:
                        act["copyData"] = {"targetField": variableManager.cdlabel_txt,
                                            "targetValue": variableManager.cdlb4_txt,
                                           "delimiter": variableManager.cdlb6_txt}
                        f_name[hold].update(act)
                    #fields = "{}{}".format(fields, INTERNAL_SCENE.nodes.output.CalcNode_CopyData.action_cd)
                    print(fields)
                elif variableManager.opcode[i] == 6:
                    act["action"].append("useMap")
                    from INTERNAL_SCENE.calc_sub_window import variableManager

                    if variableManager.last_name_um == "":
                        f_name[hold].update(act)
                    else:
                        act["useMap"] = {"inputFile":variableManager.last_name_um,"delimiter":variableManager.umlb2_txt}
                        f_name[hold].update(act)

                    print(fields)
                elif variableManager.opcode[i] == 7:
                    act["action"].append("deleteField")
                    #action_del = {"action": ["deleteField"]}
                    f_name[hold].update(act)
                    #fields = '{}{}'.format(fields, INTERNAL_SCENE.nodes.output.CalcNode_delete.action_del)
                    print(fields)

            #print(f_name)
            #fields = fields.replace("\'", "\"")
            #fields = fields[:-1]

            # if count<=1: fields = fields+"}}"
            # elif count >1:
            #     for itr in range(count-1):fields = fields+"}"
            #
            # print("Before load", fields)
            #fields = json.loads(fields)
            with open(filename, "w") as file:
                file.write(json.dumps(fields, indent=4))

                print("saving to", filename, "was successfull.")
                self.has_been_modified = False
                self.filename = filename
        else:
            fields = '{"Fields":{}}'
            fields = json.loads(fields)
            print(fields)
            with open(filename, "w") as file:
                file.write(json.dumps(fields, indent=4))

                print("saving to", filename, "was successfull.")
                self.has_been_modified = False
                self.filename = filename


    #def compileToFile(self, filename: str):
        """
        Save this `Scene` to the file on disk.

        :param filename: where to save this scene
        :type filename: ``str``
        """
    #    with open(filename, "w") as file:
    #        file.write(json.dumps(self.serialized(), indent=4))
            # print("saving to", filename, "was successfull.")

    #        self.has_been_modified = False
    #        self.filename = filename
    def loadFromFile(self, filename: str):
        """
        Load `Scene` from a file on disk

        :param filename: from what file to load the `Scene`
        :type filename: ``str``
        :raises: :class:`~GUIWINDOW.node_scene.InvalidFile` if there was an error decoding JSON file
        """

        with open(filename, "r") as file:
            raw_data = file.read()
            try:
                if sys.version_info >= (3, 9):
                    data = json.loads(raw_data)
                else:
                    data = json.loads(raw_data, encoding='utf-8')
                self.filename = filename
                self.deserialize(data)
                self.has_been_modified = False
            except json.JSONDecodeError:
                raise InvalidFile("%s is not a valid JSON file" % os.path.basename(filename))
            except Exception as e:
                dumpException(e)

    def getEdgeClass(self):
        """Return the class representing Edge. Override me if needed"""
        return Edge

    def setNodeClassSelector(self, class_selecting_function: 'functon') -> 'Node class type':
        """
        Set the function which decides what `Node` class to instantiate when deserializing `Scene`.
        If not set, we will always instantiate :class:`~GUIWINDOW.node_node.Node` for each `Node` in the `Scene`

        :param class_selecting_function: function which returns `Node` class type (not instance) from `Node` serialized ``dict`` data
        :type class_selecting_function: ``function``
        :return: Class Type of `Node` to be instantiated during deserialization
        :rtype: `Node` class type
        """
        self.node_class_selector = class_selecting_function

    def getNodeClassFromData(self, data: dict) -> 'Node class instance':
        """
        Takes `Node` serialized data and determines which `Node Class` to instantiate according the description
        in the serialized Node

        :param data: serialized `Node` object data
        :type data: ``dict``
        :return: Instance of `Node` class to be used in this Scene
        :rtype: `Node` class instance
        """
        return Node if self.node_class_selector is None else self.node_class_selector(data)


    def serialize(self) -> OrderedDict:
        from INTERNAL_SCENE.calc_sub_window import variableManager
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        l = len(nodes)
        return OrderedDict([
            ("Node Number", l),
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges),
            ('outlist', variableManager.outlist)
        ])

    #def serialized(self) -> OrderedDict:
    #    nodes, edges = [], []
    #    for node in self.nodes: nodes.append(node.serialize())
    #    for edge in self.edges: edges.append(edge.serialize())
    #    return OrderedDict([
    #        (str(INTERNAL_SCENE.nodes.output.CalcNode_Output.f), {}),
                # ("action", [ "deleteField"])
    #    ])
   # def script(self):
   #     f = {"Fields":{}}

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, *args, **kwargs) -> bool:
        hashmap = {}

        if restore_id: self.id = data['id']

        # -- deserialize NODES

        ## Instead of recreating all the nodes, reuse existing ones...
        # get list of all current nodes:
        all_nodes = self.nodes.copy()
        print("node_scene-deserialize--Deserialized = ", all_nodes)

        # go through deserialized nodes:
        for node_data in data['nodes']:
            # can we find this node in the scene?
            found = False
            for node in all_nodes:
                if node.id == node_data['id']:
                    found = node
                    break

            if not found:
                try:
                    new_node = self.getNodeClassFromData(node_data)(self)
                    new_node.deserialize(node_data, hashmap, restore_id, *args, **kwargs)
                    new_node.onDeserialized(node_data)
                    from INTERNAL_SCENE.calc_sub_window import variableManager
                    variableManager.opcode.append(node_data['op_code'])
                    print('On load VM.op_code = ', variableManager.opcode)
                    # print("New node for", node_data['title'])
                except:
                    dumpException()
            else:
                try:
                    found.deserialize(node_data, hashmap, restore_id, *args, **kwargs)
                    found.onDeserialized(node_data)
                    all_nodes.remove(found)
                    # print("Reused", node_data['title'])
                except: dumpException()

        # remove nodes which are left in the scene and were NOT in the serialized data!
        # that means they were not in the graph before...
        while all_nodes != []:
            node = all_nodes.pop()
            node.remove()


        # -- deserialize EDGES


        ## Instead of recreating all the edges, reuse existing ones...
        # get list of all current edges:
        all_edges = self.edges.copy()
        variableManager.outlist = data['outlist']
        # go through deserialized edges:
        for edge_data in data['edges']:
            # can we find this node in the scene?
            found = False
            for edge in all_edges:
                if edge.id == edge_data['id']:
                    found = edge
                    break

            if not found:
                new_edge = self.getEdgeClass()(self).deserialize(edge_data, hashmap, restore_id, *args, **kwargs)
                # print("New edge for", edge_data)
            else:
                found.deserialize(edge_data, hashmap, restore_id, *args, **kwargs)
                all_edges.remove(found)

        # remove nodes which are left in the scene and were NOT in the serialized data!
        # that means they were not in the graph before...
        while all_edges != []:
            edge = all_edges.pop()
            edge.remove()


        return True