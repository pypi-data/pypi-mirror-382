""" Game class for the Tangled game. """
from enum import IntEnum
from typing import Any

from snowdrop_tangled_game_engine.game_types import Vertex, Edge, InvalidPlayerError, InvalidGameStateError, InvalidMoveError


class Game:
    """
    Members:
        vertices (list[Vertex]): The vertices in the game graph
        edges (list[Edge]): The edges in the game graph
        player1_id (str): The ID of player 1
        player2_id (str): The ID of player 2
        graph_id (int): The ID of the game graph
        turn_count (int): The number of turns taken in the game
        current_player_index (int): The index of the current player (1 or 2)

    Enums:
        MoveType: The type of move that can be made in the game
    """

    vertices: list[Vertex] = []
    edges: list[Edge] = []
    player1_id: str = ""
    player2_id: str = ""
    graph_id: int = 0
    turn_count: int = 0
    current_player_index: int = 0  # Player index whose turn it is (1 or 2)

    class MoveType(IntEnum):
        """
        The type of move that can be made in the game.

        Values:
            NONE (int): No legal moves or it's not the player's turn.
            EDGE (int): Set a preferred edge state.
            QUIT (int): Quit the game.
        """

        NONE = -1  # No legal moves or it's not the player's turn
        EDGE = 0
        QUIT = 1

    def __init__(self):
        """Initialize the game."""
        pass

    def get_player_node(self, player_index: int = 0) -> int:
        """
        Return the node that the player, identified by plater_index, owns, or -1 if none.

        Args:
            player_index (int): The player index to check (1 or 2). Default is 0 for either player.
        """

        if player_index == 0:
            player_index = self.current_player_index

        state_id = Vertex.State.P1 if player_index == 1 else Vertex.State.P2
        return next((node.node_id for node in self.vertices if node.state == state_id), -1)

    def is_my_turn(self, player_id: str) -> bool:
        """
        Return True if it is the player's turn, False otherwise.

        Args:
            player_id (str): The player ID to check.
        """

        return player_id in [self.player1_id, self.player2_id] and player_id == [self.player1_id, self.player2_id][
            self.current_player_index - 1]

    def is_game_over(self) -> bool:
        """
        Return True if the game is over. This is the case iff all edges are colored.

        Returns:
            bool: True if the game is over, False otherwise.
        """

        # Check that vertices are owned
        if self.get_player_node(1) == -1 or self.get_player_node(2) == -1:
            raise ValueError("something went wrong ... one or both vertices not properly assigned.")

        # If all edges are claimed return True else return False
        return all(edge.state != Edge.State.NONE for edge in self.edges)

    def create_game(self, num_vertices: int = 0, edges: list[tuple[int, int]] = None,
                    player1_invite: str = "", player2_invite: str = "", graph_id: int = 0,
                    vertex_ownership: tuple[int, int] | None = None):
        """
        Initialize a game with graph_id, player ids (player1_invite and player2_invite) and number of vertices and edges.

        Args:
            num_vertices (int): The number of vertices in the game
            edges (list[tuple[int, int]]): The edges in the game as vertex pairs.
                Edge vertices must be unique, in lexical order, and within the vertex range.
            player1_invite (str): The ID of player 1 invited to this game
            player2_invite (str): The ID of player 2 invited to this game
            graph_id (int): The ID of the game graph
            vertex_ownership (tuple[int, int] | None): The vertex ownership of the game vertices, eg (0, 4)
        """

        if num_vertices > 0:
            self.vertices = [Vertex(node) for node in range(num_vertices)]

        for index, vertex in enumerate(self.vertices):
            if vertex_ownership[0] == index:
                vertex.state = Vertex.State.P1
            elif vertex_ownership[1] == index:
                vertex.state = Vertex.State.P2
            else:
                vertex.state = Vertex.State.NONE

        if edges:
            # Check that the edges are valid
            if any(node1 >= num_vertices or node2 >= num_vertices for node1, node2 in edges):
                raise InvalidGameStateError("Edge vertices are out of range")
            if any(node1 > node2 or node1 == node2 for node1, node2 in edges):
                raise InvalidGameStateError("Edge vertices are invalid. Node1 >= Node2.")

            # Sort the edges by tuple value 0 then 1
            edges.sort(key=lambda x: (x[0], x[1]))
            self.edges = [Edge(node1, node2) for node1, node2 in edges
                          if node1 < num_vertices and num_vertices > node2 > node1]

        self.turn_count = 0
        self.current_player_index = 1
        self.player1_id = player1_invite
        self.player2_id = player2_invite
        self.graph_id = graph_id

    def join_game(self, player_id: str, player_num: int):
        """
        Join the game with the player_id and player_num.

        Args:
            player_id (str): The player ID
            player_num (int): The player number, either 1 or 2, or 0 for either player
        """

        if player_num not in [0, 1, 2]:
            raise InvalidPlayerError("Invalid player number")

        if player_num == 0:

            if player_id == self.player1_id or not self.player1_id:
                self.player1_id = player_id
            elif player_id == self.player2_id or not self.player2_id:
                self.player2_id = player_id
            else:
                raise InvalidPlayerError("Game is full")

        if player_num == 1 and (not self.player1_id or self.player1_id == player_id):
            self.player1_id = player_id
        elif player_num == 2 and (not self.player2_id or self.player2_id == player_id):
            self.player2_id = player_id
        else:
            raise InvalidPlayerError("Player not allowed to join game")

    def get_game_state(self) -> dict[str, Any]:
        """Return the game state as a dictionary.

        Returns:
            {
                "num_nodes": int,
                 # List of edges as vertex pairs and edge state
                "edges": list[tuple[int, int, int]],
                "graph_id": int,
                "player1_id": str,
                "player2_id": str,
                "turn_count": int,
                "current_player_index": int (1 or 2),
                "player1_node": int, # -1 if no node
                "player2_node": int, # -1 if no node
            }
        """
        game_state = {
            "num_nodes": len(self.vertices),
            "edges": [(edge.vertices[0], edge.vertices[1], edge.state.value) for edge in self.edges],
            "graph_id": self.graph_id,
            "player1_id": self.player1_id,
            "player2_id": self.player2_id,
            "turn_count": self.turn_count,
            "current_player_index": self.current_player_index,
            "player1_node": self.get_player_node(1),
            "player2_node": self.get_player_node(2),
        }

        return game_state

    def set_game_state(self, state: dict[str, Any], validate: bool = True) -> None:
        """
        Set the game state from a dictionary. Validate that it matches the
        current game structure, if requested.

        Args:
            state (Dict[str, any]): The game state to set.
                Format:
                {
                    "num_nodes": int,
                    "edges": list[tuple[int, int, int]],
                    "player1_id": str,
                    "player2_id": str,
                    "turn_count": int,
                    "current_player_index": int (1 or 2),
                    "player1_node": int, # -1 if no node
                    "player2_node": int, # -1 if no node
                }
            validate (bool): Validate the game state by confirming matching playfield dimensions.
                If False, set the game state without validation, overwriting dimensions to match the state.
                If True, validate that the passed state matches the current game dimensions, and raise an error if not.
                Default is True.
        """

        # Use the dictionary to set the game state

        # Always check that the turn count and current player index match and are valid
        if (index := state["current_player_index"]) not in [1, 2]:
            raise InvalidGameStateError(f"Invalid current player index (must be 1 or 2): {index}")
        if state["turn_count"] % 2 != index - 1:
            raise InvalidGameStateError(f"Invalid turn count. Doesn't match current player index.")

        # Validate the data if requested
        if validate:
            # Check that the state has the correct keys
            if not all(key in state for key in
                       ["num_nodes", "edges", "turn_count", "current_player_index", "player1_node", "player2_node"]):
                raise InvalidGameStateError("Missing keys in game state")

            # Check that the game details match, such as vertex count and edge count
            if state["num_nodes"] != len(self.vertices) or len(state["edges"]) != len(self.edges):
                raise InvalidGameStateError("Game state does not match game details")

        else:
            # Set the game state without validation by creating a new game with the state details
            self.create_game(state["num_nodes"], [(edge[0], edge[1]) for edge in state["edges"]])
            self.player1_id = state.get("player1_id", "")
            self.player2_id = state.get("player2_id", "")

        self.turn_count = state["turn_count"]
        self.current_player_index = state["current_player_index"]
        for index, edge in enumerate(self.edges):
            # Check that edge vertices match
            if edge.vertices[0] != state["edges"][index][0] or edge.vertices[1] != state["edges"][index][1]:
                raise InvalidGameStateError(f"Edge vertices do not match for edge {index}")
            edge.state = Edge.State(state["edges"][index][2])

        for index, vertex in enumerate(self.vertices):
            if state["player1_node"] == index:
                vertex.state = Vertex.State.P1
            elif state["player2_node"] == index:
                vertex.state = Vertex.State.P2
            else:
                vertex.state = Vertex.State.NONE

    def get_legal_moves_by_index(self, player_index: int) -> list[tuple[int, int, int]]:
        """
        Return a list of legal moves for the player index.

        Args:
            player_index (str): The player index to get legal moves for (1 or 2).

        Returns:
            list[tuple[int, int, int]]: A list of legal moves for the player.
                Each move is a list of three integers: move type, move index, and move state.
                Move types are from the MoveType enum.
                Move indices are the edge index, starting from 0 in lexical order.
                Move states are from the Edge.State enums.
        """

        if player_index not in [1, 2]:
            raise InvalidPlayerError("Invalid player index. Must be 1 or 2.")

        return self.get_legal_moves([self.player1_id, self.player2_id][player_index - 1])

    def get_legal_moves(self, player_id: str) -> list[tuple[int, int, int]]:
        """
        Return a list of legal moves for the player.

        Args:
            player_id (str): The player ID to get legal moves for.

        Returns:
            list[tuple[int, int, int]]: A list of legal moves for the player.
                Each move is a list of three integers: move type, move index, and move state.
                Move types are from the MoveType enum.
                Move indices are the edge index, starting from 0 in lexical order.
                Move states are from the Edge.State enums.
        """
        legal_moves: list[tuple[int, int, int]] = []
        edge_move_count = 0

        # Check that the player exists
        if player_id not in [self.player1_id, self.player2_id]:
            raise InvalidPlayerError("Player not in game.")

        # Check if the player_id is the current player
        if player_id != [self.player1_id, self.player2_id][self.current_player_index - 1]:
            legal_moves.append((Game.MoveType.NONE.value, 0, 0))
        else:
            # Find valid edge moves
            for index, edge in enumerate(self.edges):
                if edge.state == Edge.State.NONE:
                    edge_move_count += 1
                    legal_moves.append((Game.MoveType.EDGE.value, index, Edge.State.ZERO.value))
                    legal_moves.append((Game.MoveType.EDGE.value, index, Edge.State.FM.value))
                    legal_moves.append((Game.MoveType.EDGE.value, index, Edge.State.AFM.value))

            # Add the quit move if there are any legal moves
            if legal_moves:
                legal_moves.append((Game.MoveType.QUIT.value, 0, 0))

        return legal_moves

    def make_move(self, player_id: str, move_type: int, move_index: int, move_state: int):
        """
        Make a move in the game.

        Args:
            player_id (str): The player ID making the move.
            move_type (int): The type of move to make (see Game.MoveType).
            move_index (int): The index of the move (edge index, starting from 0 in lexical order).
            move_state (int): The state of the move (see Edge.State).

        Example:
            game.make_move("player1", Game.MoveType.EDGE.value, 0, Edge.State.FM.value)
        """

        # For now, skip "QUIT" move type
        if move_type == Game.MoveType.QUIT.value:
            return False

        # Check that the player exists
        if player_id not in [self.player1_id, self.player2_id]:
            raise InvalidPlayerError("Player not in game.")

        if player_id != [self.player1_id, self.player2_id][self.current_player_index - 1]:
            # Maybe handle a quit request even if not current player?
            raise InvalidPlayerError("Not this player's turn.")

        legal_moves = self.get_legal_moves_by_index(self.current_player_index)

        if (move_type, move_index, move_state) not in legal_moves:
            raise InvalidMoveError("Invalid move")

        if move_type not in [Game.MoveType.EDGE.value]:
            raise InvalidMoveError("Invalid move type")
        elif move_type == Game.MoveType.EDGE.value:
            if move_index >= len(self.edges):
                raise InvalidMoveError("Invalid edge index")

            edge = self.edges[move_index]
            if edge.state != Edge.State.NONE:
                raise InvalidMoveError("Edge already claimed")
            if move_state == Edge.State.NONE.value or move_state > Edge.State.AFM.value:
                raise InvalidMoveError("Selected edge state not valid.")

            edge.state = Edge.State(move_state)

        self.current_player_index = 1 if self.current_player_index == 2 else 2
        self.turn_count += 1

        if self.is_game_over():
            # Game over, calculate the score
            pass


__all__ = ["Game", "InvalidMoveError", "InvalidPlayerError", "InvalidGameStateError"]
