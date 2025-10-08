"""
Base class for game agents. Create a subclass of this class to implement a game agent.
"""
from abc import ABC, abstractmethod
from snowdrop_tangled_game_engine.game import Game


class GameAgentBase(ABC):

    def __init__(self, player_id: str | None = None):
        """
        Initializes the game agent with the player id, which is either a str or (default) None.

        Args:
            player_id (str or None): The player id for this agent.
        """
        if not player_id:   # not None is True, not "any string" is False
            player_id = self.__class__.__name__   # Get the name of the subclass for this class as the player id
        self.__player_id = player_id   # the string or the name of the subclass

    @property
    def id(self) -> str:   # The getter method when you read agent.id
        return self.__player_id

    @id.setter
    def id(self, player_id: str):   # The setter method when you assign to agent.id
        self.__player_id = player_id

    @abstractmethod
    def make_move(self, game: Game) -> tuple[int, int, int]:
        """
        Have the agent make a move in the game. This method must be implemented by a subclass.
        This will be called each time it is the agent's turn to make a move.
        The move must be a valid move for the game and the agent.

        Args:
            game (Game): The game object to make a move in. Use this to get valid moves and the current
            state of the game.

        Returns:
            tuple[int, int, int]: A tuple of the move type (see Game.MoveType), move index (edge index in
            lexical order starting from 0), and move state (see Edge.State).
        """
        pass


__all__ = ["GameAgentBase"]
