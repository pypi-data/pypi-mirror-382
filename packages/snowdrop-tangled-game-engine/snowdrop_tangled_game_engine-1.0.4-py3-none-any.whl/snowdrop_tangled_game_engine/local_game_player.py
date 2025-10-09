""" LocalGamePlayer class for playing a game locally. This class is used to play a game locally between two agents. """

from typing import Optional

from snowdrop_tangled_game_engine.game import Game
from snowdrop_tangled_game_engine.base_game_player import GamePlayerBase
from snowdrop_tangled_game_engine.base_agent import GameAgentBase


class LocalGamePlayer(GamePlayerBase):
    """
    LocalGamePlayer class for playing a game locally between two agents.
    Instantiate it with references to the two agents and the game to play.
    Call play_game() to play the game until it is over. Calls will be made by
    play_game to the agents to select moves for their turn until the game is over.
    """

    player_1: GameAgentBase
    player_2: GameAgentBase
    game: Game
    update_display: Optional[callable]

    def __init__(self, player_1: GameAgentBase, player_2: GameAgentBase, game: Game,
                 update_display: Optional[callable] = None):
        """
        Initializes the LocalGamePlayer with the two agents and the game to play.

        Args:
            player_1 (GameAgentBase): The first player agent.
            player_2 (GameAgentBase): The second player agent.
            game (Game): The game to play.
        """

        self.player_1 = player_1
        self.player_2 = player_2
        self.game = game
        self.game.join_game(self.player_1.id, 1)
        self.game.join_game(self.player_2.id, 2)
        self.update_display = update_display

    def play_game(self) -> dict:
        """
        Play the game until it is over. Calls will be made by play_game to the agents
        to select moves for their turn until the game is over.

        Returns:
            dict: The final state of the game.
        """

        while not self.game.is_game_over():
            player = self.player_1 if self.game.is_my_turn(player_id=self.player_1.id) else self.player_2
            move = player.make_move(self.game)
            if move:
                move_type, move_index, move_state = move
                if move_type == Game.MoveType.QUIT.value:
                    print(f"{player.id} quit the game.")
                    break
                self.game.make_move(player.id, move_type, move_index, move_state)
                if self.update_display:
                    self.update_display(self.game.get_game_state())
            else:
                print("No moves available. Ending game.")
                break

        final_state = self.game.get_game_state()
        return final_state


__all__ = ["LocalGamePlayer"]
