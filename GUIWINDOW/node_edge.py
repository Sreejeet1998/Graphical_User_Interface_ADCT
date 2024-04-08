# -*- coding: utf-8 -*-
"""
A module containing NodeEditor's class for representing Edge and Edge Type Constants.
"""
from collections import OrderedDict

from GUIWINDOW.node_graphics_edge import QDMGraphicsEdgeBezier, QDMGraphicsEdgeDirect
from GUIWINDOW.node_graphics_edge import QDMGraphicsEdge
from GUIWINDOW.node_serializable import Serializable
from GUIWINDOW.utils_no_qt import dumpException


EDGE_TYPE_DIRECT = 1        #:
EDGE_TYPE_BEZIER = 2        #:
EDGE_TYPE_SQUARE = 3        #:
EDGE_TYPE_DEFAULT = EDGE_TYPE_BEZIER

DEBUG = False


class Edge(Serializable):


    edge_validators = []        #: class variable containing list of registered edge validators

    def __init__(self, scene:'Scene', start_socket:'Socket'=None, end_socket:'Socket'=None, edge_type=EDGE_TYPE_DIRECT):

        super().__init__()
        self.scene = scene

        # default init
        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket
        self._edge_type = edge_type

        # create Graphics Edge instance
        self.grEdge = self.createEdgeClassInstance()

        self.scene.addEdge(self)

    def __str__(self):
        return "<Edge %s..%s -- S:%s E:%s>" % (
            hex(id(self))[2:5], hex(id(self))[-3:],
            self.start_socket, self.end_socket
        )
    @property
    def start_socket(self):

        return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        # if we were assigned to some socket before, delete us from the socket
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)

        # assign new start socket
        self._start_socket = value
        # addEdge to the Socket class
        if self.start_socket is not None:
            self.start_socket.addEdge(self)

    @property
    def end_socket(self):

        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        # if we were assigned to some socket before, delete us from the socket
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)

        # assign new end socket
        self._end_socket= value
        # addEdge to the Socket class
        if self.end_socket is not None:
            self.end_socket.addEdge(self)

    @property
    def edge_type(self):

        return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        if hasattr(self, 'grEdge') and self.grEdge is not None:
            self.scene.grScene.removeItem(self.grEdge)
        # assign new value
        self._edge_type = value
        edgeClass = self.determineEdgeClass(self.edge_type)
        self.grEdge = edgeClass(self)

        self.scene.grScene.addItem(self.grEdge)

        if self.start_socket is not None:
            self.updatePositions()

    def determineEdgeClass(self, edge_type:int):
        edge_class = QDMGraphicsEdgeBezier
        if edge_type == EDGE_TYPE_DIRECT:
            edge_class = QDMGraphicsEdgeDirect
        return edge_class

    @classmethod
    def getEdgeValidators(cls):

        return cls.edge_validators

    @classmethod
    def registerEdgeValidator(cls, validator_callback: 'function'):

        cls.edge_validators.append(validator_callback)

    @classmethod
    def validateEdge(cls, start_socket: 'Socket', end_socket: 'Socket') -> bool:

        for validator in cls.getEdgeValidators():
            if not validator(start_socket, end_socket):
                return False
        return True

    def reconnect(self, from_socket: 'Socket', to_socket: 'Socket'):
        if self.start_socket == from_socket:
            self.start_socket = to_socket
        elif self.end_socket == from_socket:
            self.end_socket = to_socket

    def getGraphicsEdgeClass(self):
        return QDMGraphicsEdge

    def createEdgeClassInstance(self):
        self.grEdge = self.getGraphicsEdgeClass()(self)
        self.scene.grScene.addItem(self.grEdge)
        if self.start_socket is not None:
            self.updatePositions()
        return self.grEdge

    def getOtherSocket(self, known_socket:'Socket'):
        return self.start_socket if known_socket == self.end_socket else self.end_socket

    def doSelect(self, new_state:bool=True):
        self.grEdge.doSelect(new_state)

    def updatePositions(self):
        source_pos = self.start_socket.getSocketPosition()
        source_pos[0] += self.start_socket.node.grNode.pos().x()
        source_pos[1] += self.start_socket.node.grNode.pos().y()
        self.grEdge.setSource(*source_pos)
        if self.end_socket is not None:
            end_pos = self.end_socket.getSocketPosition()
            end_pos[0] += self.end_socket.node.grNode.pos().x()
            end_pos[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDestination(*end_pos)
        else:
            self.grEdge.setDestination(*source_pos)
        self.grEdge.update()


    def remove_from_sockets(self):
        self.end_socket = None
        self.start_socket = None


    def remove(self, silent_for_socket:'Socket'=None, silent=False):
        old_sockets = [self.start_socket, self.end_socket]

        # ugly hack, since I noticed that even when you remove grEdge from scene,
        # sometimes it stays there! How dare you Qt!
        if DEBUG: print(" - hide grEdge")
        self.grEdge.hide()

        if DEBUG: print(" - remove grEdge", self.grEdge)
        self.scene.grScene.removeItem(self.grEdge)
        if DEBUG: print("   grEdge:", self.grEdge)

        self.scene.grScene.update()

        if DEBUG: print("# Removing Edge", self)
        if DEBUG: print(" - remove edge from all sockets")
        self.remove_from_sockets()
        if DEBUG: print(" - remove edge from scene")
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass
        if DEBUG: print(" - everything is done.")

        try:
            # notify nodes from old sockets
            for socket in old_sockets:
                if socket and socket.node:
                    if silent:
                        continue
                    if silent_for_socket is not None and socket == silent_for_socket:
                        # if we requested silence for Socket and it's this one, skip notifications
                        continue

                    # notify Socket's Node
                    socket.node.onEdgeConnectionChanged(self)
                    if socket.is_input: socket.node.onInputChanged(socket)

        except Exception as e: dumpException(e)


    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.id if self.start_socket is not None else None),
            ('end', self.end_socket.id if self.end_socket is not None else None),
        ])

    def deserialize(self, data:dict, hashmap:dict={}, restore_id:bool=True, *args, **kwargs) -> bool:
        if restore_id: self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']


# Example: using validators for Edge
# You can register edge validators wherever you want, even here...
# However if you do use overridden Edge, you should call registerEdgeValidator on that overridden class
#
# from GUIWINDOW.node_edge_validators import *
# Edge.registerEdgeValidator(edge_validator_debug)
# Edge.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
# Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)
# Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_different_color)
