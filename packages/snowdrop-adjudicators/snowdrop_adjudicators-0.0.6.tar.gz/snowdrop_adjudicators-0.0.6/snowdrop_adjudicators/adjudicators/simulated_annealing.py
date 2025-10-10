import neal
import numpy as np
from typing import Optional

from snowdrop_tangled_game_engine import GameState

from snowdrop_adjudicators.adjudicators.adjudicator import Adjudicator, AdjudicationResult, IsingModel


class SimulatedAnnealingAdjudicator(Adjudicator):
    """Adjudicator implementation using simulated annealing"""

    def __init__(self) -> None:
        """Initialize the simulated annealing adjudicator"""
        super().__init__()
        self.sampler = neal.SimulatedAnnealingSampler()
        self.num_reads: int = 10000
        self.num_sweeps: int = 16
        self.beta_max: float = 3.0
        self.epsilon: Optional[float] = None

    def setup(self, **kwargs) -> None:
        """Configure simulated annealing parameters. kwargs is a dictionary with key 'epsilon'
        and optional keys 'num_reads', 'num_sweeps', and 'beta_max'

        Keyword Args:
            epsilon (float): Draw boundary
            num_reads (int): Number of annealing reads (default: 10000)
            num_sweeps (int): Number of sweeps per read (default: 16)
            beta_max (float): Maximum inverse temperature (default: 3.0)

        Raises:
            ValueError: If parameters are invalid
        """
        if 'num_reads' in kwargs:
            if not isinstance(kwargs['num_reads'], int) or kwargs['num_reads'] <= 0:
                raise ValueError("num_reads must be a positive integer")
            self.num_reads = kwargs['num_reads']

        if 'num_sweeps' in kwargs:
            if not isinstance(kwargs['num_sweeps'], int) or kwargs['num_sweeps'] <= 0:
                raise ValueError("num_sweeps must be a positive integer")
            self.num_sweeps = kwargs['num_sweeps']

        if 'beta_max' in kwargs:
            if not isinstance(kwargs['beta_max'], (int, float)) or kwargs['beta_max'] <= 0:
                raise ValueError("beta_max must be a positive number")
            self.beta_max = float(kwargs['beta_max'])

        if 'epsilon' not in kwargs:
            raise ValueError(f"epsilon must be provided in setup")
        else:
            if not isinstance(kwargs['epsilon'], float):
                raise ValueError("epsilon must be a float")
            self.epsilon = kwargs['epsilon']

        self._parameters = {
            'num_reads': self.num_reads,
            'num_sweeps': self.num_sweeps,
            'beta_max': self.beta_max,
            'epsilon': self.epsilon
        }

    def adjudicate(self, game_state: GameState) -> AdjudicationResult:
        """Adjudicate the game state using simulated annealing.

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

        # Calculate beta range based on coupling strengths
        beta_range = [
            1 / np.sqrt(np.sum([Jij ** 2 for Jij in ising_model['j'].values()]) + 0.001),
            self.beta_max
        ]

        # Perform simulated annealing
        response = self.sampler.sample_ising(
            ising_model['h'],
            ising_model['j'],
            beta_range=beta_range,
            num_reads=self.num_reads,
            num_sweeps=self.num_sweeps,
            randomize_order=True
        )

        # Calculate correlation matrix
        samples = np.array(response.record.sample, dtype=float)

        # creates symmetric matrix with zeros on diagonal (so that self-correlation of one is not counted) -- this is
        # the standard for computing influence vector
        correlation_matrix = (np.einsum('si,sj->ij', samples, samples) / self.num_reads -
                              np.eye(game_state['num_nodes']))

        # Compute results
        winner, score, influence_vector = self._compute_winner_score_and_influence(game_state=game_state,
                                                                                   correlation_matrix=correlation_matrix)

        return AdjudicationResult(
            game_state=game_state,
            adjudicator='simulated_annealing',
            winner=winner,
            score=score,
            influence_vector=influence_vector,
            correlation_matrix=correlation_matrix,
            parameters=self._parameters
        )
