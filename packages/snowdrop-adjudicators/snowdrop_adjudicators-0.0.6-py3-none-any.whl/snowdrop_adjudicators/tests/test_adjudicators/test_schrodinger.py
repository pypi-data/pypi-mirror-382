import math

from snowdrop_adjudicators import SchrodingerEquationAdjudicator


class TestSchrodingerAdjudicator:
    """Test suite for SchrodingerEquationAdjudicator"""

    def test_adjudicate(self, sample_game_states):
        """Test that all sample graphs give the correct adjudications"""
        allowed_graphs, epsilon_values, game_states, correct_results, _, anneal_times = sample_game_states

        adjudication_result_from_schrodinger = {}
        for idx in range(len(allowed_graphs)):
            adj = SchrodingerEquationAdjudicator()
            kwargs = {'epsilon': epsilon_values[idx],
                      'anneal_time': anneal_times[idx]}
            adj.setup(**kwargs)

            adjudication_result_from_schrodinger[allowed_graphs[idx]] = adj.adjudicate(game_states[allowed_graphs[idx]])

            # test if reading the correct score and winner
            assert math.isclose(adjudication_result_from_schrodinger[allowed_graphs[idx]]['score'],
                                correct_results[allowed_graphs[idx]][0], abs_tol=0.15)
            assert (adjudication_result_from_schrodinger[allowed_graphs[idx]]['winner'] ==
                    correct_results[allowed_graphs[idx]][1])
