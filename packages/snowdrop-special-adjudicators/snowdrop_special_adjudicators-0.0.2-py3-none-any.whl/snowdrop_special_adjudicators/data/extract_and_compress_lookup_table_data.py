import sys
import pickle
import gzip
import numpy as np
from typing import Any


def main() -> None:
    """Helper function to process raw adjudication data and convert to compressed lookup tables.

    Takes raw adjudication data files containing quantum annealing results for various
    graphs and extracts the scores into simplified lookup tables. The processed data
    is saved as compressed pickle files.

    The function processes graphs 2, 11, 12, 18, 19, and 20, using predefined
    quantum annealing parameters (num_reads and anneal_time) specific to each graph.
    Scores are converted to float16 for memory efficiency.

    Input files: graph_{N}_adjudicated_unique_terminal_states_for_paper.pkl
    Output files: graph_{N}_adjudicated.pkl.gz

    Raises:
        FileNotFoundError: If input adjudication data files are missing
        KeyError: If expected quantum annealing data structure is not found
    """
    # Quantum annealing parameters: graph_id -> [num_reads, anneal_time]
    solver_data: dict[int, list[int]] = {
        2: [100000, 350],
        11: [100000, 350],
        12: [10000, 40],
        18: [10000, 100],
        19: [100000, 350],
        20: [100000, 350]
    }

    for graph_number in [2, 11, 12, 18, 19, 20]:
        raw_file_path = f"graph_{graph_number}_adjudicated_unique_terminal_states_for_paper.pkl"

        with open(raw_file_path, 'rb') as fp:
            raw_adjudication_data: dict[str, Any] = pickle.load(fp)

        # Extract quantum annealing scores and convert to float16 for efficiency
        # Format: lookup_values['[1, 2, 0, 1, 1, 2]'] = score (np.float16)
        lookup_values: dict[str, np.float16] = {}
        num_reads, anneal_time = solver_data[graph_number]

        qa_data = raw_adjudication_data['fixed']['quantum_annealing'][num_reads][anneal_time]
        for state_key, result in qa_data.items():
            lookup_values[state_key] = np.float16(result['score'])

        # Save as compressed pickle for faster loading
        output_file_path = f"graph_{graph_number}_adjudicated.pkl.gz"
        with gzip.open(output_file_path, 'wb', compresslevel=9) as f:
            pickle.dump(lookup_values, f)  # type: ignore


if __name__ == "__main__":
    sys.exit(main())
