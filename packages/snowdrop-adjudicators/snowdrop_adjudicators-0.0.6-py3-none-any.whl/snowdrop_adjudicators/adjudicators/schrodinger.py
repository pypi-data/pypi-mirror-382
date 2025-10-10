from typing import Optional

from snowdrop_tangled_game_engine import GameState

from snowdrop_adjudicators.schrodinger.schrodinger_functions import evolve_schrodinger
from snowdrop_adjudicators.adjudicators.adjudicator import Adjudicator, AdjudicationResult, IsingModel


class SchrodingerEquationAdjudicator(Adjudicator):
    """Adjudicator implementation using Schrödinger equation evolution"""

    def __init__(self) -> None:
        """Initialize the adjudicator with default values."""
        super().__init__()
        self.s_min: float = 0.001
        self.s_max: float = 0.999
        self.anneal_time: Optional[float | int] = None   # hardware anneal time in nanoseconds
        self.epsilon: Optional[float] = None

    def setup(self, **kwargs) -> None:
        """Configure the Schrödinger equation parameters. kwargs is a dictionary with keys 'epsilon' and 'anneal_time'
        and optional keys 's_min' and 's_max'

        Keyword Args:
            epsilon (float): Draw boundary
            anneal_time (float): Annealing time in nanoseconds (default: 40.0)
            s_min (float): Minimum annealing parameter (default: 0.001)
            s_max(float): Maximum annealing parameter (default: 0.999)

        Raises:
            ValueError: If parameters are invalid
        """

        if 'anneal_time' not in kwargs:
            raise ValueError(f"anneal_time must be provided in setup")
        else:
            if not isinstance(kwargs['anneal_time'], (int, float)):
                raise ValueError("anneal_time must be an int or float")
            self.anneal_time = kwargs['anneal_time']

        if 'epsilon' not in kwargs:
            raise ValueError(f"epsilon must be provided in setup")
        else:
            if not isinstance(kwargs['epsilon'], float):
                raise ValueError("epsilon must be a float")
            self.epsilon = kwargs['epsilon']

        if 's_min' in kwargs:
            if not isinstance(kwargs['s_min'], (int, float)) or not 0 <= kwargs['s_min'] < 1:
                raise ValueError("s_min must be in [0, 1)")
            self.s_min = float(kwargs['s_min'])

        if 's_max' in kwargs:
            if not isinstance(kwargs['s_max'], (int, float)) or not 0 < kwargs['s_max'] <= 1:
                raise ValueError("s_max must be in (0, 1]")
            self.s_max = float(kwargs['s_max'])

        if self.s_min >= self.s_max:
            raise ValueError("s_min must be less than s_max")

        self._parameters = {
            'anneal_time': self.anneal_time,
            's_min': self.s_min,
            's_max': self.s_max,
            'epsilon': self.epsilon
        }

    def adjudicate(self, game_state: GameState) -> AdjudicationResult:
        """Adjudicate the game state using Schrödinger equation evolution.

        Args:
            game_state: The current game state

        Returns:
            AdjudicationResult containing the adjudication details

        Raises:
            ValueError: If the game state is invalid
        """
        self._validate_game_state(game_state)

        # Convert game state to Ising model
        ising_model: IsingModel = self._game_state_to_ising(game_state)

        # Evolve Schrödinger equation
        correlation_matrix = evolve_schrodinger(
            ising_model['h'],
            ising_model['j'],
            s_min=self.s_min,
            s_max=self.s_max,
            tf=self.anneal_time,
            n_qubits=game_state['num_nodes']
        )

        # Make symmetric (evolve_schrodinger returns upper triangular)
        correlation_matrix = correlation_matrix + correlation_matrix.T

        # Compute results
        winner, score, influence_vector = self._compute_winner_score_and_influence(game_state=game_state,
                                                                                   correlation_matrix=correlation_matrix)

        return AdjudicationResult(
            game_state=game_state,
            adjudicator='schrodinger_equation',
            winner=winner,
            score=score,
            influence_vector=influence_vector,
            correlation_matrix=correlation_matrix,
            parameters=self._parameters
        )
