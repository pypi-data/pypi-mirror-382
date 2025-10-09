"""
Support types for the Tangled Game Engine.
"""
from enum import IntEnum


class InvalidMoveError(Exception):
    """An exception for an invalid move in the game."""
    pass


class InvalidPlayerError(Exception):
    """An exception for an invalid player trying to join the game."""
    pass


class InvalidGameStateError(Exception):
    """An exception for mismatch between a game state and a Game."""
    pass


class Vertex:
    """
    A vertex in the game graph.

    Members:
        state (Vertex.State): The state of the vertex (0, 1, 2) where 0 is unowned, 1 owned by red, 2 owned by blue.
        node_id (int): The integer label of the vertex.

    Enums:
        State: The state of a vertex.
    """

    class State(IntEnum):
        """
        The state of a vertex.
        Use this to set or interpret the state of a vertex

        Values:
            NONE (int): The vertex has no state (no ownership).
            P1 (int): The vertex is owned by player 1.
            P2 (int): The vertex is owned by player 2.
        """
        NONE = 0
        P1 = 1
        P2 = 2

    def __init__(self, node_id: int):
        """Initialize a vertex in the game graph to no ownership."""
        self.node_id = node_id
        self.state = Vertex.State.NONE


class Edge:
    """
    An edge in the game graph.

    Members:
        vertices (Tuple[int, int]): The two vertices that the edge connects.
        state (Edge.State): The state of the edge.

    Enums:
        State: The state of an edge.
    """

    class State(IntEnum):
        """
        The state of an edge.
        Use this to set or interpret the state of an edge.

        Values:
            NONE (int): The edge has not been set.
            ZERO (int): The edge has been set to ZERO coupling.
            FM (int): The edge is ferromagnetic (FM).
            AFM (int): The edge is antiferromagnetic (AFM).
        """

        NONE = 0
        ZERO = 1
        FM = 2
        AFM = 3

    vertices: tuple[int, int] = None

    def __init__(self, node1_id: int, node2_id: int):
        """Create an initially unset edge in the game graph."""
        self.vertices = (node1_id, node2_id)
        self.state = Edge.State.NONE


__all__ = ["Vertex", "Edge", "InvalidMoveError", "InvalidPlayerError", "InvalidGameStateError"]
