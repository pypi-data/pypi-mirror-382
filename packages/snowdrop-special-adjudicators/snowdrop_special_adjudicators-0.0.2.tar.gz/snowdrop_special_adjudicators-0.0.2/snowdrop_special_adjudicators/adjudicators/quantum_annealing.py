from pathlib import Path
from typing import Optional, Any
import numpy as np
from dwave.system import DWaveSampler, FixedEmbeddingComposite

from snowdrop_special_adjudicators.utils.find_hardware_embeddings import get_embeddings
from snowdrop_special_adjudicators.utils.find_graph_automorphisms import get_automorphisms

from snowdrop_tangled_game_engine import GameState

from snowdrop_adjudicators import Adjudicator, AdjudicationResult


class QuantumAnnealingAdjudicator(Adjudicator):
    """Adjudicator implementation using D-Wave quantum annealing"""

    def __init__(self) -> None:
        """Initialize the quantum annealing adjudicator"""
        super().__init__()

        self.anneal_time: Optional[float | int | None] = None   # value in nanoseconds
        self.epsilon: Optional[float | None] = None
        self.solver_name: Optional[str | None] = None   #  'Advantage2_system1.6'
        self.graph_number: Optional[int | None] = None

        self.num_reads: int = 10000
        self.num_chip_runs: int = 1
        self.use_gauge_transform: bool = False
        self.use_shim: bool = False
        self.shim_iterations: int = 1
        self.alpha_phi: float = 0.1
        self.data_dir: str | Path = Path(__file__).parent.parent / 'data'

        self.embeddings: list[list[int]] | None = None
        self.automorphisms: list[dict[int, int]] | None = None
        self.shim_stats: dict[str, Any] = {}
        self.base_sampler: DWaveSampler | None = None

    def setup(self, **kwargs) -> None:
        """Configure quantum annealing parameters and initialize D-Wave connection.

        kwargs is a dictionary with keys 'anneal_time', 'epsilon', 'solver_name', 'graph_number'
        and optional keys 'num_reads', 'num_chip_runs', 'use_gauge_transform', 'use_shim',
        'shim_iterations', 'alpha_phi', 'data_dir'

        Keyword Args:
            anneal_time (float, int): Annealing time in nanoseconds
            epsilon (float): Draw boundary
            solver_name (str): Name of D-Wave solver to use
            graph_number (int): Graph number for embedding lookup

            num_reads (int): Number of annealing reads per run
            num_chip_runs (int): Number of separate chip programming runs
            use_gauge_transform (bool): Whether to apply gauge transformations
            use_shim (bool): Whether to use shimming process
            shim_iterations (int): Number of shimming iterations if shimming is used
            alpha_phi (float): Learning rate for flux bias offsets
            data_dir (str | Path): Path to data directory

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If D-Wave connection fails
        """

        if 'data_dir' in kwargs:
            if not isinstance(kwargs['data_dir'], str | Path):
                raise ValueError("data_dir must be a string or a Path object")
            self.data_dir = kwargs['data_dir']

        if 'alpha_phi' in kwargs:
            if not isinstance(kwargs['alpha_phi'], float):
                raise ValueError("alpha_phi must be a float")
            self.alpha_phi = kwargs['alpha_phi']

        if 'shim_iterations' in kwargs:
            if not isinstance(kwargs['shim_iterations'], int) or kwargs['shim_iterations'] <= 0:
                raise ValueError("shim_iterations must be a positive integer")
            self.shim_iterations = kwargs['shim_iterations']

        if 'use_shim' in kwargs:
            if not isinstance(kwargs['use_shim'], bool):
                raise ValueError("use_shim must be boolean")
            self.use_shim = kwargs['use_shim']

        if 'use_gauge_transform' in kwargs:
            if not isinstance(kwargs['use_gauge_transform'], bool):
                raise ValueError("use_gauge_transform must be boolean")
            self.use_gauge_transform = kwargs['use_gauge_transform']

        if 'num_chip_runs' in kwargs:
            if not isinstance(kwargs['num_chip_runs'], int) or kwargs['num_chip_runs'] <= 0:
                raise ValueError("num_chip_runs must be a positive integer")
            self.num_chip_runs = kwargs['num_chip_runs']

        if 'num_reads' in kwargs:
            if not isinstance(kwargs['num_reads'], int) or kwargs['num_reads'] <= 0:
                raise ValueError("num_reads must be a positive integer")
            self.num_reads = kwargs['num_reads']

        if 'graph_number' not in kwargs:
            raise ValueError(f"graph_number must be provided in setup")
        else:
            if not isinstance(kwargs['graph_number'], int):
                raise ValueError("graph_number must be an int")
            self.graph_number = kwargs['graph_number']

        if 'solver_name' not in kwargs:
            raise ValueError(f"solver_name must be provided in setup")
        else:
            if not isinstance(kwargs['solver_name'], str):
                raise ValueError("solver_name must be a string")
            self.solver_name = kwargs['solver_name']

        if 'anneal_time' not in kwargs:
            raise ValueError(f"anneal_time must be provided in setup")
        else:
            if not isinstance(kwargs['anneal_time'], float | int):
                raise ValueError("anneal_time must be a float or int")
            self.anneal_time = kwargs['anneal_time']

        if 'epsilon' not in kwargs:
            raise ValueError(f"epsilon must be provided in setup")
        else:
            if not isinstance(kwargs['epsilon'], float):
                raise ValueError("epsilon must be a float")
            self.epsilon = kwargs['epsilon']

        # we need these so always compute / load in
        self.automorphisms = get_automorphisms(self.graph_number, self.data_dir)
        self.embeddings = get_embeddings(self.graph_number, self.solver_name, self.data_dir)

        # Initialize sampler; added connection_close and request_timeout to see if this fixes things
        try:
            self.base_sampler = DWaveSampler(solver=self.solver_name, connection_close=True, request_timeout=600)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize D-Wave sampler: {str(e)}")

        # initialize shim_stats if required
        if self.use_shim:
            self.shim_stats = {'qubit_magnetizations': [],
                               'average_absolute_value_of_magnetization': [],
                               'all_flux_bias_offsets': []}

        # Store parameters

        self._parameters = {
            'anneal_time': self.anneal_time,
            'epsilon': self.epsilon,
            'solver_name': self.solver_name,
            'graph_number': self.graph_number,
            'num_reads': self.num_reads,
            'num_chip_runs': self.num_chip_runs,
            'use_gauge_transform': self.use_gauge_transform,
            'use_shim': self.use_shim,
            'shim_iterations': self.shim_iterations,
            'alpha_phi': self.alpha_phi,
            'data_dir': self.data_dir
        }

    def close_connection_to_hardware(self):
        self.base_sampler.close()

    def _process_embedding(self, game_state: GameState, automorphism: dict[int, int], num_embeddings: int) -> dict[int, list[int]]:
        """Process embedding with given automorphism.

        Args:
            game_state: Current game state
            automorphism: Graph automorphism to apply
            num_embeddings: number of embeddings to use; default is all of them

        Returns:
            Processed embedding mapping
        """

        num_vertices = game_state['num_nodes']

        inverted_automorphism_to_use = {v: k for k, v in automorphism.items()}  # swaps key <-> values

        permuted_embedding = []

        for each_embedding in self.embeddings[:num_embeddings]:
            # each_embedding is like [1093, 1098, 136]; 343 of these for three-vertex graph
            this_embedding = []
            for each_vertex in range(num_vertices):  # each_vertex ranges from 0 to 2
                this_embedding.append(each_embedding[inverted_automorphism_to_use[each_vertex]])
            permuted_embedding.append(this_embedding)

        # given that permuted_embedding looks like [[1229, 1235, 563], [872, 242, 866], ...]
        # this next part converts into the format {0: [1229], 1: [1235], 2: [563], 3: [872], 4: [242], 5: [866]}

        embedding_map = {}

        for embedding_idx in range(num_embeddings):
            for each_vertex in range(num_vertices):  # up to 0..1037
                embedding_map[num_vertices * embedding_idx + each_vertex] = \
                    [permuted_embedding[embedding_idx][each_vertex]]

        return embedding_map

    def adjudicate(self, game_state: GameState) -> AdjudicationResult:
        """Adjudicate the game state using quantum annealing.

        Args:
            game_state: The current game state

        Returns:
            AdjudicationResult containing the adjudication details

        Raises:
            ValueError: If the game state is invalid
            RuntimeError: If quantum annealing fails
        """

        if not self.base_sampler:
            raise RuntimeError("Sampler not initialized. Call setup() first.")

        self._validate_game_state(game_state)

        num_vertices = game_state['num_nodes']
        num_embeddings = len(self.embeddings)
        total_samples = np.zeros((1, num_vertices))  # Initial array for stacking

        all_samples = None
        indices_of_flips = None

        # here the 'num_reads' parameter is set so that the actual sample count that's returned is what the user set
        # for num_reads -- we get extra samples from both num_embeddings and self.num_chip_runs. For example
        # if num_embeddings = 343 and self.num_chip_runs = 2, and the user asks for self.num_reads = 10,000
        # then the actual 'num_reads' sent to the solver would be int(10000/343/2) = 14. This will return a total of
        # approximately 10,000 samples.
        sampler_kwargs: dict[str, Any] = {
            'num_reads': int(self.num_reads / num_embeddings / self.num_chip_runs),
            'answer_mode': 'raw'
        }

        sampler_kwargs.update({
            'fast_anneal': True,
            'annealing_time': self.anneal_time / 1000.0,
            'auto_scale': False
        })

        if self.use_shim:
            sampler_kwargs.update({'readout_thermalization': 100.,
                                   'auto_scale': False,
                                   'flux_drift_compensation': True,
                                   'flux_biases': [0] * self.base_sampler.properties['num_qubits']})
            shim_iterations = self.shim_iterations
        else:
            shim_iterations = 1  # if we don't shim, just run through shim step only once

        # **********************************************************
        # Step 0: convert game_state to the desired base Ising model
        # **********************************************************

        # for tangled, h_j=0 for all vertices j in the game graph, and J_ij is one of +1, -1, or 0 for all vertex
        # pairs i,j. I named the "base" values (the actual problem defined on the game graph we are asked to solve)
        # base_ising_model.

        base_ising_model = self._game_state_to_ising(game_state)

        # We now enter a loop where each pass through the loop programs the chip to specific values of h and J but
        # now for the entire chip. We do this by first selecting one automorphism and embedding it in multiple
        # parallel ways across the entire chip, and then optionally applying a gauge transform across all the qubits
        # used. This latter process chooses different random gauges for each of the embedded instances.

        for _ in range(self.num_chip_runs):

            # *******************************************************************
            # Step 1: Randomly select an automorphism and embed it multiple times
            # *******************************************************************

            automorphism: dict[int, int] = np.random.choice(self.automorphisms)
            embedding_map = self._process_embedding(game_state, automorphism, num_embeddings)

            # *****************************************************************************************************
            # Step 2: Set h, J parameters for full chip using parallel embeddings of a randomly chosen automorphism
            # *****************************************************************************************************

            # compute full_h and full_j which are h, jay values for the entire chip assuming the above automorphism
            # I am calling the problem definition and variable ordering before the automorphism the BLACK or BASE
            # situation. After the automorphism the problem definition and variable labels change -- I'm calling the
            # situation after the automorphism has been applied the BLUE situation.

            full_h = {}
            full_j = {}

            for embedding_idx in range(num_embeddings):
                for each_vertex in range(num_vertices):
                    full_h[num_vertices * embedding_idx + each_vertex] = 0

            for k, v in base_ising_model['j'].items():
                edge_under_automorph = (min(automorphism[k[0]], automorphism[k[1]]),
                                        max(automorphism[k[0]], automorphism[k[1]]))
                full_j[edge_under_automorph] = v
                for j in range(1, num_embeddings):
                    full_j[(edge_under_automorph[0] + num_vertices * j,
                            edge_under_automorph[1] + num_vertices * j)] = v

            # **************************************************************************
            # Step 3: Choose random gauge, modify h, J parameters for full chip using it
            # **************************************************************************

            # next we optionally apply a random gauge transformation. I call the situation after the gauge
            # transformation has been applied the BLUE with RED STAR situation.

            if self.use_gauge_transform:
                flip_map = [np.random.choice([-1, 1]) for _ in full_h]  # random list of +1, -1 values of len # qubits
                indices_of_flips = [i for i, x in enumerate(flip_map) if x == -1]  # the indices of the -1 values

                for edge_key, j_val in full_j.items():  # for each edge and associated J value
                    full_j[edge_key] = j_val * flip_map[edge_key[0]] * flip_map[edge_key[1]]  # Jij -> J_ij g_i g_j

            # *****************************************
            # Step 4: Choose sampler and its parameters
            # *****************************************

            sampler_kwargs.update({'h': full_h,
                                   'J': full_j})

            sampler = FixedEmbeddingComposite(self.base_sampler, embedding=embedding_map)  # applies the embedding

            # *************************************************************************
            # Step 5: Optionally start shimming process in the BLUE with RED STAR basis
            # *************************************************************************

            # all of this in the BLUE with RED STAR basis, ie post automorph, post gauge transform
            for shim_iteration_idx in range(shim_iterations):

                # **************************************
                # Step 6: Generate samples from hardware
                # **************************************

                #########################################################################
                # this is where hardware is called
                # moved all_samples into try except block
                try:
                    ss = sampler.sample_ising(**sampler_kwargs)
                    all_samples = ss.record.sample
                except Exception as e:
                    print(f"Exception encountered while using quantum hardware: {e}")
                    print("trying again ...")
                    # retry sample call
                    ss = sampler.sample_ising(**sampler_kwargs)
                    all_samples = ss.record.sample

                #########################################################################

                if self.use_shim:

                    # *************************************************************
                    # Step 6a: Compute average values of each qubit == magnetization
                    # *************************************************************

                    magnetization = np.sum(all_samples,
                                           axis=0) / self.num_reads  # BLUE with RED STAR label ordering
                    self.shim_stats['average_absolute_value_of_magnetization'].append(
                        np.sum([abs(k) for k in magnetization]) / len(magnetization))

                    qubit_magnetization = [0] * self.base_sampler.properties['num_qubits']
                    for k, v in embedding_map.items():
                        qubit_magnetization[v[0]] = magnetization[k]  # check

                    self.shim_stats['qubit_magnetizations'].append(qubit_magnetization)

                    # **************************************
                    # Step 6b: Adjust flux bias offset terms
                    # **************************************

                    for k in range(self.base_sampler.properties['num_qubits']):
                        sampler_kwargs['flux_biases'][k] -= self.alpha_phi * qubit_magnetization[k]

                    self.shim_stats['all_flux_bias_offsets'].append(sampler_kwargs['flux_biases'])

            # *****************************************************************************************************
            # Step 7: Reverse gauge transform, from BLUE with RED STAR to just BLUE, after shimming process is done
            # *****************************************************************************************************

            if self.use_gauge_transform:
                all_samples[:, indices_of_flips] = -all_samples[:, indices_of_flips]

            # ***********************************
            # Step 8: Stack samples in BLUE order
            # ***********************************

            # this should make a big fat stack of the results in BLUE variable ordering
            all_samples_processed_blue = all_samples[:, range(num_vertices)]
            for k in range(1, num_embeddings):
                all_samples_processed_blue = np.vstack((all_samples_processed_blue,
                                                        all_samples[:, range(num_vertices * k,
                                                                             num_vertices * (k + 1))]))

            # **********************************************************************
            # Step 9: Reorder columns to make them BLACK order instead of BLUE order
            # **********************************************************************

            all_samples_processed_black = all_samples_processed_blue[:,
                                          [automorphism[i] for i in range(all_samples_processed_blue.shape[1])]]

            # *********************************************************
            # Step 10: Add new samples to the stack, all in BLACK order
            # *********************************************************

            total_samples = np.vstack((total_samples, all_samples_processed_black))

        # ***************************************************************
        # Step 11: Post process samples stack to extract return variables
        # ***************************************************************

        total_samples = np.delete(total_samples, (0), axis=0)  # delete first row of zeros

        # I changed sample count to what should be the actual sample count
        # sample_count = self.params.num_reads * num_embeddings * self.params.num_chip_runs
        sample_count = int(
            self.num_reads / num_embeddings / self.num_chip_runs) * num_embeddings * self.num_chip_runs

        # this is a full matrix with zeros on the diagonal that uses all the samples
        correlation_matrix = \
            (np.einsum('si,sj->ij', total_samples, total_samples) / sample_count -
             np.eye(num_vertices))

        # Compute results
        winner, score, influence_vector = self._compute_winner_score_and_influence(game_state=game_state,
                                                                                   correlation_matrix=correlation_matrix)

        # add samples to the result returned
        self._parameters.update({'samples': total_samples})

        return AdjudicationResult(
            game_state=game_state,
            adjudicator='quantum_annealing',
            winner=winner,
            score=score,
            influence_vector=influence_vector,
            correlation_matrix=correlation_matrix,
            parameters=self._parameters
        )
