import math

from snowdrop_adjudicators import SimulatedAnnealingAdjudicator


class TestSimulatedAnnealingAdjudicator:
    """Test suite for SimulatedAnnealingAdjudicator"""

    def test_adjudicate(self, sample_game_states):
        """Test that all sample graphs give the correct adjudications"""
        allowed_graphs, epsilon_values, game_states, _, simulated_annealing_results, _ = sample_game_states

        adjudication_result_from_simulated_annealing = {}
        for idx in range(len(allowed_graphs)):
            adj = SimulatedAnnealingAdjudicator()
            kwargs = {'epsilon': epsilon_values[idx],
                      'num_reads': 1000000}   # this is more samples than you would typically use
            adj.setup(**kwargs)

            adjudication_result_from_simulated_annealing[allowed_graphs[idx]] = adj.adjudicate(game_states[allowed_graphs[idx]])

            # test if reading the correct score and winner
            assert math.isclose(adjudication_result_from_simulated_annealing[allowed_graphs[idx]]['score'],
                                simulated_annealing_results[allowed_graphs[idx]][0], abs_tol=0.01)   # 1% tolerance
            assert (adjudication_result_from_simulated_annealing[allowed_graphs[idx]]['winner'] ==
                    simulated_annealing_results[allowed_graphs[idx]][1])
