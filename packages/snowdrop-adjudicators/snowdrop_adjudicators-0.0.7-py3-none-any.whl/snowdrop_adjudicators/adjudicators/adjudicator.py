from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from typing_extensions import TypedDict
import numpy as np
import numpy.typing as npt

from snowdrop_tangled_game_engine import GameState


def evaluate_winner(score: float, epsilon: float) -> str:
    """
    Given a score (float) and a draw boundary epsilon (float),
    returns the winner as a string -- one of ('red', 'blue', 'draw')

    Args:
        score (float): The score of the game
        epsilon (float): The draw boundary of the game

    Returns:
        str: One of 'red', 'blue', 'draw'
    """
    if score > epsilon:
        return 'red'
    elif score < -epsilon:
        return 'blue'
    else:
        return 'draw'


class AdjudicationResult(TypedDict):
    """
    AdjudicationResult instances give the result of adjudication of a terminal state of a Tangled game.

    Members:
        game_state (GameState): a terminal state of a game of type GameState
        adjudicator (str): string, one of 'simulated_annealing' or 'schrodinger_equation' (or more if you create your own)
        winner (str | None): one of 'red', 'blue', 'draw' if there is a winner, or None if not
        score (float): the score of the game, which is influence_vector(red_vertex_index) - influence_vector(blue_vertex_index)
        influence_vector (npt.NDArray[np.float64]): vector of length number of vertices of the influence of each vertex
        correlation_matrix (npt.NDArray[np.float64]): square symmetric matrix of size [number of vertices, number of vertices] with zeros on diagonal
        parameters (dict[str, Union[str, int, float, bool]]): dictionary of adjudication parameters
 """

    game_state: GameState
    adjudicator: str
    winner: Optional[str | None]  # 'red', 'blue', 'draw', or None
    score: Optional[float]
    influence_vector: Optional[npt.NDArray[np.float64]]
    correlation_matrix: Optional[npt.NDArray[np.float64]]
    parameters: dict[str, Union[str, int, float, bool]]


class IsingModel(TypedDict):
    h: dict[int, float]  # Local fields
    j: dict[tuple[int, int], float]  # Coupling strengths


class Adjudicator(ABC):
    """Base interface for game state adjudication implementations"""

    def __init__(self) -> None:
        """Initialize base adjudicator"""
        self._parameters: dict[str, Any] = {}
        self.j_map:dict[int, float] = {0: 0.0,   # edge (i, j) uncolored , J_ij=0
                                       1: 0.0,   # edge (i, j) colored gray, J_ij=0
                                       2: -1.0,  # edge (i, j) colored green, FM coupling, J_ij=-1.0
                                       3: 1.0}   # edge (i, j) colored purple, AFM coupling, J_ij=+1.0
        self.epsilon: float = 0.0      # draw boundary definition

    @abstractmethod
    def setup(self, **kwargs) -> None:
        """Optional setup method for implementation-specific initialization."""
        pass

    @abstractmethod
    def adjudicate(self, game_state: GameState) -> AdjudicationResult:
        """Adjudicate the given game state."""
        pass

    @staticmethod
    def _validate_game_state(game_state: GameState) -> None:
        """Validate the game state structure and contents."""
        required_keys = {
            'num_nodes', 'edges', 'player1_id', 'player2_id',
            'turn_count', 'current_player_index', 'player1_node', 'player2_node'
        }

        if not all(key in game_state for key in required_keys):
            missing_keys = required_keys - set(game_state.keys())
            raise ValueError(f"Game state missing required keys: {missing_keys}")

        if game_state['num_nodes'] < 1:
            raise ValueError("Number of nodes must be positive")

        for edge in game_state['edges']:
            if len(edge) != 3:
                raise ValueError(f"Invalid edge format: {edge}")
            if not (0 <= edge[0] < game_state['num_nodes'] and 0 <= edge[1] < game_state['num_nodes']):
                raise ValueError(f"Edge vertices out of range: {edge}")

    def _game_state_to_ising(self, game_state: GameState) -> IsingModel:
        """Convert game state to Ising model parameters.

        Args:
            game_state: The current game state

        Returns:
            IsingModel containing h (local fields) and j (coupling strengths)
        """
        h = {i: 0.0 for i in range(game_state['num_nodes'])}
        j = {}

        for edge in game_state['edges']:
            v1, v2, edge_label = edge
            if v1 > v2:
                v1, v2 = v2, v1
            j[(v1, v2)] = self.j_map[edge_label]

        return IsingModel(h=h, j=j)

    def _compute_winner_score_and_influence(self,
                                            game_state: GameState,
                                            correlation_matrix: npt.NDArray[np.float64]) -> tuple[str, float, npt.NDArray[np.float64]]:
        """Compute winner, score and influence from correlation matrix """
        if not isinstance(correlation_matrix, np.ndarray):
            raise ValueError("Correlation matrix must be a numpy array")

        rows, cols = correlation_matrix.shape

        if rows != cols:
            raise ValueError(f"Correlation matrix must be square, got {rows}x{cols}")

        if rows != game_state['num_nodes']:
            raise ValueError(f"Matrix size {rows} doesn't match {game_state['num_nodes']} nodes")

        if not (isinstance(game_state['player1_node'], int) and isinstance(game_state['player2_node'], int)):
            raise ValueError("Player nodes must be integers")

        influence_vector = np.sum(correlation_matrix, axis=0)

        score = influence_vector[game_state['player1_node']] - influence_vector[game_state['player2_node']]

        winner = evaluate_winner(score, self.epsilon)

        return winner, score, influence_vector
