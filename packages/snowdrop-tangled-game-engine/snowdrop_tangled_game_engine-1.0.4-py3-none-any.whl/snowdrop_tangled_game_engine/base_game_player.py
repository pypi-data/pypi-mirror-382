"""
The base class for a game player. This is used in this package to
make a local game player that plays a game locally between two agents.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Type


class GamePlayerBase(ABC):
    """
    The base class for a game player. This is used in this package to
    make a local game player that plays a game locally between two agents.

    It can be extended to create a game player for remote game services
    or other situations.
    """

    @abstractmethod
    def play_game(self, *args, **kwargs) -> dict:
        """
        Implement this function to play the game and return the final state.

        Returns:
            dict: The final state of the game.
                (see Game.get_game_state() for the format)
        """
        pass

    @classmethod
    def start_and_play_full_game(cls, client_class: Type[GamePlayerBase], *args, **kwargs) -> None:
        """
        Starts and plays the game client with the specified subclass. Who won can be extracted by calling
        client.game.get_game_state()

        Args:
            client_class (Type[GamePlayerBase]): The subclass of GamePlayerBase to start.
            *args, **kwargs: Additional arguments for the subclass constructor.

        """

        client = client_class(*args, **kwargs)
        client.play_game()

        # print("Game over")
        # print("Final state is:")
        # print(client.game.get_game_state())


__all__ = ["GamePlayerBase"]
