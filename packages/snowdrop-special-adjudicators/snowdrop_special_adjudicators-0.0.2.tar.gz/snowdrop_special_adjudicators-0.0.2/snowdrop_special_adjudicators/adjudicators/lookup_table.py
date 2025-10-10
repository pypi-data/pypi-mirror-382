import os
from typing import Optional
from pathlib import Path
import numpy as np

from snowdrop_special_adjudicators.utils.utilities import extract_state_key_from_game_state, load_lookup_table, extract_wld_from_lookup_table

from snowdrop_tangled_game_engine import GameState

from snowdrop_adjudicators import Adjudicator, AdjudicationResult, evaluate_winner


class LookupTableAdjudicator(Adjudicator):
    """Adjudicator implementation using pre-computed lookup tables"""

    def __init__(self) -> None:
        """Initialize the lookup table adjudicator"""
        super().__init__()
        self.data_dir: Optional[str] = str(Path(__file__).parent.parent / "data")
        self.lookup_table: Optional[dict[str, np.float16]] | None = None
        self.epsilon: Optional[float] = None
        self.graph_number: Optional[int] = None

    def setup(self, **kwargs) -> None:
        """Configure lookup table parameters. kwargs is a dictionary with keys 'epsilon' and 'graph_number'
        and optional key 'data_dir'

        Keyword Args:
            data_dir (str, optional): Directory containing lookup table data files;
                default works for current lookup_tables
            epsilon (float): Draw boundary
            graph_number (int): Graph number
        Raises:
            ValueError: If parameters are invalid or data directory doesn't exist
        """
        if 'data_dir' in kwargs:
            if not isinstance(kwargs['data_dir'], str):
                raise ValueError("data_dir must be a string")
            if not os.path.isdir(kwargs['data_dir']):
                raise ValueError(f"Directory not found: {kwargs['data_dir']}")
            self.data_dir = kwargs['data_dir']

        if 'epsilon' not in kwargs:
            raise ValueError(f"epsilon must be provided in setup")
        else:
            if not isinstance(kwargs['epsilon'], float):
                raise ValueError("epsilon must be a float")
            self.epsilon = kwargs['epsilon']

        if 'graph_number' not in kwargs:
            raise ValueError(f"graph_number must be provided in setup")
        else:
            if not isinstance(kwargs['graph_number'], int):
                raise ValueError("graph_number must be an int")
            self.graph_number = kwargs['graph_number']

        self._parameters = {'data_dir': self.data_dir,
                            'epsilon': self.epsilon,
                            'graph_number': self.graph_number}

    def _get_lookup_table(self, vertex_count: int, vertex_ownership: tuple[int, int]) -> None:
        """Load the appropriate lookup table for the given graph_number (vertex_count is passed in as a parameter)

        Raises:
            RuntimeError: If lookup table file cannot be loaded
        """

        if not isinstance(vertex_count, int):
            raise RuntimeError("vertex_count must be an int.")

        self.lookup_table = load_lookup_table(data_dir=self.data_dir,
                                              graph_number=self.graph_number,
                                              vertex_count=vertex_count,
                                              vertex_ownership=vertex_ownership)

        # print('WLD was: ', extract_wld_from_lookup_table(self.lookup_table, epsilon=self.epsilon))

    def adjudicate(self, game_state: GameState) -> AdjudicationResult:
        """Adjudicate the game state using the lookup table.

        Args:
            game_state: The current game state

        Returns:
            AdjudicationResult containing the adjudication details

        Raises:
            ValueError: If the game state is invalid or unsupported
            RuntimeError: If lookup table is not loaded
        """
        self._validate_game_state(game_state)

        # Load lookup table if needed
        if self.lookup_table is None:
            self._get_lookup_table(game_state['num_nodes'], (game_state['player1_node'], game_state['player2_node']))

        if not self.lookup_table:
            raise RuntimeError("Failed to load lookup table")

        # Extract lookup_table key from GameState instance
        lookup_state = extract_state_key_from_game_state(game_state)

        try:
            score: np.float16 = self.lookup_table[str(lookup_state)]
            winner = evaluate_winner(float(score), self.epsilon)
        except KeyError:  # key not in results_dict
            raise RuntimeError("key not in lookup table...")

        return AdjudicationResult(
            game_state=game_state,
            adjudicator='lookup_table',
            winner=winner,
            score=float(score),
            influence_vector=None,  # available if we need them from the raw data
            correlation_matrix=None,
            parameters=self._parameters
        )
