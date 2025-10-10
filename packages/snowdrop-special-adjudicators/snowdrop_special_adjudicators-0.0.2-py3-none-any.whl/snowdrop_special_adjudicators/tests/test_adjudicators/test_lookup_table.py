import math

from snowdrop_special_adjudicators import LookupTableAdjudicator
from snowdrop_special_adjudicators.utils.utilities import extract_state_key_from_game_state, swap_ones_and_twos


class TestLookupTableAdjudicator:
    """Test suite for LookupTableAdjudicator"""

    def test_adjudicate(self, sample_game_states):
        """Test lookup table adjudicator on provided terminal states
        Requires the lookup tables to be in /data"""

        allowed_graphs, epsilon_values, game_states, correct_results, _, _ = sample_game_states

        adjudication_result_from_lookup_table = {}
        for idx in range(len(allowed_graphs)):
            adj = LookupTableAdjudicator()
            kwargs = {'epsilon': epsilon_values[idx],
                      'graph_number': allowed_graphs[idx]}
            adj.setup(**kwargs)

            adjudication_result_from_lookup_table[allowed_graphs[idx]] = adj.adjudicate(game_states[allowed_graphs[idx]])

            # test if reading the correct score and winner
            assert math.isclose(adjudication_result_from_lookup_table[allowed_graphs[idx]]['score'],
                                correct_results[allowed_graphs[idx]][0])
            assert (adjudication_result_from_lookup_table[allowed_graphs[idx]]['winner'] ==
                    correct_results[allowed_graphs[idx]][1])

            # test if swapping 1 and 2 in vertex position worked
            state_key = extract_state_key_from_game_state(adjudication_result_from_lookup_table[allowed_graphs[idx]]['game_state'])
            swapped_state_key = swap_ones_and_twos(state_key[:game_states[allowed_graphs[idx]]['num_nodes']]) + state_key[game_states[allowed_graphs[idx]]['num_nodes']:]

            assert str(state_key) in adj.lookup_table
            assert str(swapped_state_key) in adj.lookup_table
            assert math.isclose(adj.lookup_table[str(swapped_state_key)], - adj.lookup_table[str(state_key)])
