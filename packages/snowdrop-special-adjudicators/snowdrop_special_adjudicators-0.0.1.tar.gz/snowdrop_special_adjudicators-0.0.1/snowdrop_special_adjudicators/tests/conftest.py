""" shared fixtures for tests """
import pytest

# noinspection PyPackageRequirements
from snowdrop_tangled_game_engine import GraphProperties


@pytest.fixture
def sample_game_states():
    """Provide sample terminal game states for testing"""

    graph_properties = GraphProperties()

    # Correct answers
    correct_results: dict[int, tuple[float, str]] = {}
    simulated_annealing_results: dict[int, tuple[float, str]] = {}

    game_states = {}

    for graph_number in graph_properties.allowed_graphs:
        game_states[graph_number] = {'player1_node': graph_properties.vertex_ownership[graph_number][0],
                                     'player2_node': graph_properties.vertex_ownership[graph_number][1]}

        if graph_number == 2:   # K_3 graph, S = [3,3,3], score = 0 (draw)
            game_states[graph_number].update({'num_nodes': 3, 'edges': [(0, 1, 3), (0, 2, 3), (1, 2, 3)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 3,
                                              'current_player_index': 1})
            correct_results[graph_number] = (-0.038330078125, 'draw')
            simulated_annealing_results[graph_number] = (0.000558, 'draw')
        if graph_number == 11:  # P_3 graph, S = [2,3], score = +2 (red)
            game_states[graph_number].update({'num_nodes': 3, 'edges': [(0, 1, 2), (1, 2, 3)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 2,
                                              'current_player_index': 2})
            correct_results[graph_number] = (1.9990234375, 'red')
            simulated_annealing_results[graph_number] = (1.988, 'red')
        if graph_number == 12:  # moser spindle, S = [3, 3, 2, 2, 1, 2, 2, 3, 3, 2, 2], score = 0 (draw)
            game_states[graph_number].update({'num_nodes': 7, 'edges': [(0, 1, 3), (0, 4, 3), (0, 6, 2), (1, 2, 2),
                                                                        (1, 5, 1), (2, 3, 2), (2, 5, 2), (3, 4, 3),
                                                                        (3, 5, 3), (3, 6, 2), (4, 6, 2)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 11,
                                              'current_player_index': 1})
            correct_results[graph_number] = (0.0030517578125, 'draw')
            simulated_annealing_results[graph_number] = (0.62943, 'red')
        if graph_number == 18:  # 3-prism graph; 6 vertices, 9 edges, S = [3, 3, 1, 3, 3, 2, 2, 2, 3], score = -1 (blue)
            game_states[graph_number].update({'num_nodes': 6, 'edges': [(0, 1, 3), (0, 2, 3), (0, 3, 1), (1, 2, 3),
                                                                        (1, 4, 3), (2, 5, 2), (3, 4, 2), (3, 5, 2),
                                                                        (4, 5, 3)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 9,
                                              'current_player_index': 1})
            correct_results[graph_number] = (-0.9912109375, 'blue')
            simulated_annealing_results[graph_number] = (-0.975388, 'blue')
        if graph_number == 19:   # Barbell graph; S = [3,2,2,3,2,3,2]; SA scores -4/9 (blue), QA & SE scores +1/2 (red)
            game_states[graph_number].update({'num_nodes': 6, 'edges': [(0, 1, 3), (0, 2, 2), (1, 2, 2),
                                                                        (2, 5, 3), (3, 4, 2), (3, 5, 3),
                                                                        (4, 5, 2)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 7,
                                              'current_player_index': 1})
            correct_results[graph_number] = (0.379638671875, 'red')
            simulated_annealing_results[graph_number] = (-0.447884, 'blue')
        if graph_number == 20:  # Diamond graph; S = [1,2,2,2,3]; SA scores +4/3, QA & SE scores = +2 (red)
            game_states[graph_number].update({'num_nodes': 4, 'edges': [(0, 1, 1), (0, 3, 2),
                                                                        (1, 2, 2), (1, 3, 2), (2, 3, 3)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 6,
                                              'current_player_index': 2})
            correct_results[graph_number] = (1.9892578125, 'red')
            simulated_annealing_results[graph_number] = (1.325748, 'red')

    return (graph_properties.allowed_graphs,
            graph_properties.epsilon_values,
            game_states,
            correct_results,
            simulated_annealing_results,
            graph_properties.anneal_times)
