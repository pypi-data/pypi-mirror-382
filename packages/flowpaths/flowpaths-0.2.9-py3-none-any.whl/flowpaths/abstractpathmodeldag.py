import flowpaths.stdag as stdag
from flowpaths.utils import safetypathcovers
from flowpaths.utils import solverwrapper as sw
import flowpaths.utils as utils
import time
import copy
from abc import ABC, abstractmethod

class AbstractPathModelDAG(ABC):
    """
    This is an abstract class modelling a path-finding (M)ILP in a DAG. The design of this package is based on the
    following principles:

    - The class is designed to be extended by other classes that model specific path-finding problems in DAGs.
    In this way, they all benefit from the variables it encodes, and the safety optimizations it provides.
    - The class uses our custom [SolverWrapper](solver-wrapper.md) class, which is a wrapper around the solvers HiGHS (open source) and 
    Gurobi (free with academic license). In this way, both solvers can be used interchangeably.

    More in detail, this class encodes `k` s-t paths in the DAG G, where s is the global source of the stDAG 
    and t is the global sink. It also allows for subpath constraints that must appear in at least one of the s-t paths.

    The class creates the following variables:

    - **edge_vars**: `edge_vars[(u, v, i)]` = 1 if path `i` goes through edge `(u, v)`, `0` otherwise
    - **edge_position_vars**: `edge_position_vars[(u, v, i)]` = position of edge `(u, v)` in path `i`, starting from position 0

        - These variables are created only if `encode_edge_position` is set to `True`
        - Note that positions are relative to the globals source `s` of the stDAG, thus the first edge in a path is 
        the edge from `s` to the first vertex in the original graph, and this first edge has position 0
        - If you set `length_attr`, then the positions are relative to the edge lengths, and not the number of edges
        The first edge still gets position 0, and other edges get positions equal to the sum of the lengths of the edges before them in the path
        - If you set `length_attr`, and an edge has missing edge length, then it gets length 1

    - **path_length_vars**: `path_length_vars[(i)]` = length of path `i`

        - These variables are created only if `encode_path_length` is set to `True`
        - Note that the length of a path is the sum of the lengths of the edges in the path
        - If you set `length_attr`, then the lengths are the sum of the lengths of the edges in the path
        - If you set `length_attr`, and an edge has missing edge length, then it gets length 1
        - **NOTE**: the length also includes the edges from global source to the first vertex, and from the last vertex to the global sink. By default, these do not have a length attached, so each gets length 1.
        
    - **solver**: a solver object to solve the (M)ILP, implemented using our [SolverWrapper](solver-wrapper.md) class.

    !!! node "Safety optimizations"
        This class uses the "safety information" (see [https://doi.org/10.48550/arXiv.2411.03871](https://doi.org/10.48550/arXiv.2411.03871)) in the graph to fix some 
        `edge_vars` to 1 or 0. The safety information consists of safe paths, or safe sequences, that are guaranteed to appear in at least 
        one cover (made up of any number of s-t paths) of the edges in `trusted_edges_for_safety`. That is, when implementing a new
        path-finding (M)ILP, you can guarantee that 

        1. The solution is made up of s-t paths
        2. Any solution covers all edges in `trusted_edges_for_safety`, then safety optimizations can be used to fix some `edge_vars` to 1, 
        which can speed up the solving process, while guaranteeing global optimality.
    """
    # storing some defaults
    optimize_with_safe_paths = True
    optimize_with_safe_sequences = False
    optimize_with_safe_zero_edges = True
    optimize_with_subpath_constraints_as_safe_sequences = True
    optimize_with_safety_as_subpath_constraints = False
    optimize_with_safety_from_largest_antichain = False

    def __init__(
        self,
        G: stdag.stDAG,
        k: int,
        subpath_constraints: list = [],
        subpath_constraints_coverage: float = 1,
        subpath_constraints_coverage_length: float = None,
        encode_edge_position: bool = False,
        encode_path_length: bool = False,
        length_attr: str = None,
        optimization_options: dict = None,
        solver_options: dict = {},
        solve_statistics: dict = {},
    ):
        """
        Parameters
        ----------

        - `G: stDAG.stDAG`  
            
            The directed acyclic graph (DAG) to be used. Create it using the [`stDAG` class](stdag.md).

        - `k: int`
            
            The number of paths to be modeled.

        - `subpath_constraints: list`, optional
            
            A list of lists, where each list is a sequence of edges (not necessarily contiguous, i.e. path). Defaults to an empty list.
            
            Each sequence of edges must appear in at least one solution path; if you also pass subpath_constraints_coverage, 
            then each sequence of edges must appear in at least subpath_constraints_coverage fraction of some solution path, see below.
        
        - `subpath_constraints_coverage: float`, optional
            
            Coverage fraction of the subpath constraints that must be covered by some solution paths, in terms of number of edges. 
                - Defaults to 1 (meaning that 100% of the edges of the constraint need to be covered by some solution path).
        
        - `subpath_constraints_coverage_length: float`, optional 
            
            Coverage fraction of the subpath constraints that must be covered by some solution paths, in terms of length of the subpath. Defaults to `None`, meaning that this is not imposed. 
            - If you set this constraint, you cannot set `subpath_constraints_coverage` (and its default value of 1 will be ignored).
            - If you set this constraint, you also need to set `length_attr`. If an edge has missing edge length, it gets length 1.

        - `encode_edge_position: bool`, optional
        
            Whether to encode the position of the edges in the paths. Defaults to `False`.

        - `encode_path_length: bool`, optional
            
            Whether to encode the length of the paths (in terms of number of edges, or sum of lengths of edges, if set via `length_attr`). Defaults to `False`.

        - `length_attr: str`, optional
            
            The attribute name from where to get the edge lengths. Defaults to `None`.
            
            - If set, then the edge positions, or path lengths (above) are in terms of the edge lengths specified in the `length_attr` field of each edge
            - If set, and an edge has a missing edge length, then it gets length 1.
        
        - `optimization_options: dict`, optional 
            
            Dictionary of optimization options. Defaults to `None`, in which case the default values are used. See the [available optimizations](solver-options-optimizations.md). 
            If you pass any safety optimizations, you must also pass the dict entry `"trusted_edges_for_safety"` (see below). 
            If a child class has already solved the problem and has the solution paths, it can pass them via the dict entry `"external_solution_paths"` to skip the solver creation and encoding of paths (see below).
            
            - `"trusted_edges_for_safety": set`
        
                Set of trusted edges for safety. Defaults to `None`.

                !!! warning "Global optimality"
                    In order for the optimizations to still guarantee a global optimum, you must guarantee that:

                    1. The solution is made up of source-to-sink paths, and
                    2. Every edge in `trusted_edges_for_safety` appears in some solution path, for all solutions. This naturally holds for several problems, for example [Minimum Flow Decomposition](minimum-flow-decomposition.md) or [k-Minimum Path Error] where in fact, under default settings, **all** edges appear in all solutions.

            - `"external_solution_paths" : list`
            
                External solution paths, as a list of paths, where every path is a list of nodes. Defaults to `None`.
                If you provide this, this class skip the solver creation and encoding of paths, and just return these paths. 
                This is useful when the child class managed to solver the problem in a different way, 
                and needs to let this class know them, in order to have a consistent API.

        - `solver_options: dict`, optional
            
            Dictionary of solver options. Defaults to `{}`, in which case the default values are used. 
            See the [available solver options](solver-options-optimizations.md).

        - `solve_statistics: dict`, optional
            
            Dictionary to store solve statistics. Defaults to `{}`.


        Raises
        ----------
        - ValueError: If `trusted_edges_for_safety` is not provided when optimizing with `optimize_with_safe_paths` or `optimize_with_safe_sequences`.
        - ValueError: If both `optimize_with_safe_paths` and `optimize_with_safe_sequences` are set to `True`.
        """

        self.G = G
        if G.number_of_edges() == 0:
            utils.logger.error(f"{__name__}: The input graph G has no edges. Please provide a graph with at least one edge.")
            raise ValueError(f"The input graph G has no edges. Please provide a graph with at least one edge.")
        self.id = self.G.id
        self.k = k
        self.length_attr = length_attr
        
        self.subpath_constraints = copy.deepcopy(subpath_constraints)
        if self.subpath_constraints is not None:
            self._check_valid_subpath_constraints()

        self.subpath_constraints_coverage = subpath_constraints_coverage
        self.subpath_constraints_coverage_length = subpath_constraints_coverage_length
        if len(subpath_constraints) > 0:
            if self.subpath_constraints_coverage <= 0 or self.subpath_constraints_coverage > 1:
                utils.logger.error(f"{__name__}: subpath_constraints_coverage must be in the range (0, 1]")
                raise ValueError("subpath_constraints_coverage must be in the range (0, 1]")
                
            if self.subpath_constraints_coverage_length is not None:
                if self.subpath_constraints_coverage_length <= 0 or self.subpath_constraints_coverage_length > 1:
                    utils.logger.error(f"{__name__}: subpath_constraints_coverage_length must be in the range (0, 1]")
                    raise ValueError("If set, subpath_constraints_coverage_length must be in the range (0, 1]")
                if self.length_attr is None:
                    utils.logger.error(f"{__name__}: If subpath_constraints_coverage_length is set, length_attr must be provided.")
                    raise ValueError("If subpath_constraints_coverage_length is set, length_attr must be provided.")
                if self.subpath_constraints_coverage < 1:
                    utils.logger.error(f"{__name__}: If subpath_constraints_coverage_length is set, you cannot set also subpath_constraints_coverage.")
                    raise ValueError("If subpath_constraints_coverage_length is set, you cannot set also subpath_constraints_coverage.")

        self.solve_statistics = solve_statistics
        self.edge_vars = {}
        self.edge_vars_sol = {}
        self.subpaths_vars = {}
        self.encode_edge_position = encode_edge_position
        self.encode_path_length = encode_path_length
        self.edge_position_vars = {}

        self.solver_options = solver_options
        if self.solver_options is None:
            self.solver_options = {}
        self.threads = self.solver_options.get("threads", sw.SolverWrapper.threads)

        # optimizations
        if optimization_options is None:
            optimization_options = {}
        self.optimize_with_safe_paths = optimization_options.get("optimize_with_safe_paths", AbstractPathModelDAG.optimize_with_safe_paths)
        self.external_safe_paths = optimization_options.get("external_safe_paths", None)
        self.optimize_with_safe_sequences = optimization_options.get("optimize_with_safe_sequences", AbstractPathModelDAG.optimize_with_safe_sequences)
        self.optimize_with_subpath_constraints_as_safe_sequences = optimization_options.get("optimize_with_subpath_constraints_as_safe_sequences", AbstractPathModelDAG.optimize_with_subpath_constraints_as_safe_sequences)
        self.trusted_edges_for_safety = optimization_options.get("trusted_edges_for_safety", None)
        self.optimize_with_safe_zero_edges = optimization_options.get("optimize_with_safe_zero_edges", AbstractPathModelDAG.optimize_with_safe_zero_edges)
        self.external_solution_paths = optimization_options.get("external_solution_paths", None)
        self.allow_empty_paths = optimization_options.get("allow_empty_paths", False)
        self.optimize_with_safety_as_subpath_constraints = optimization_options.get("optimize_with_safety_as_subpath_constraints", AbstractPathModelDAG.optimize_with_safety_as_subpath_constraints)
        self.optimize_with_safety_from_largest_antichain = optimization_options.get("optimize_with_safety_from_largest_antichain", AbstractPathModelDAG.optimize_with_safety_from_largest_antichain)
        
        self._is_solved = False
        if self.external_solution_paths is not None:
            self._is_solved = True

        # some checks
        if self.optimize_with_safe_paths and self.external_safe_paths is None and self.trusted_edges_for_safety is None:
            utils.logger.error(f"{__name__}: trusted_edges_for_safety must be provided when optimizing with safe paths")
            raise ValueError("trusted_edges_for_safety must be provided when optimizing with safe lists")        
        if self.optimize_with_safe_sequences and self.external_safe_paths is not None:
            utils.logger.error(f"{__name__}: Cannot optimize with both external safe paths and safe sequences")
            raise ValueError("Cannot optimize with both external safe paths and safe sequences")

        if self.optimize_with_safe_paths and self.optimize_with_safe_sequences:
            utils.logger.error(f"{__name__}: Cannot optimize with both safe paths and safe sequences")
            raise ValueError("Cannot optimize with both safe paths and safe sequences")        
                
        self.safe_lists = []
        if self.external_safe_paths is not None:
            self.safe_lists = self.external_safe_paths
        elif self.optimize_with_safe_paths and not self.is_solved() and self.trusted_edges_for_safety is not None:
            start_time = time.perf_counter()
            self.safe_lists += safetypathcovers.safe_paths(
                G=self.G,
                edges_to_cover=self.trusted_edges_for_safety,
                no_duplicates=False,
                threads=self.threads,
            )
            self.solve_statistics["safe_paths_time"] = time.perf_counter() - start_time

        if self.optimize_with_safe_sequences and not self.is_solved():
            start_time = time.perf_counter()
            self.safe_lists += safetypathcovers.safe_sequences(
                G=self.G,
                edges_or_subpath_constraints_to_cover=self.trusted_edges_for_safety,
                no_duplicates=False,
                threads=self.threads,
            )
            self.solve_statistics["safe_sequences_time"] = time.perf_counter() - start_time

        if self.optimize_with_subpath_constraints_as_safe_sequences and len(self.subpath_constraints) > 0 and not self.is_solved():
            if self.subpath_constraints_coverage == 1 and self.subpath_constraints_coverage_length in [1, None]:
                start_time = time.perf_counter()
                self.safe_lists += safetypathcovers.safe_sequences(
                    G=self.G,
                    edges_or_subpath_constraints_to_cover=self.subpath_constraints,
                    no_duplicates=False,
                    threads=self.threads,
                )
                self.solve_statistics["optimize_with_subpath_constraints_as_safe_sequences"] = time.perf_counter() - start_time

        if self.optimize_with_safety_as_subpath_constraints:
            self.subpath_constraints += self.safe_lists

    def create_solver_and_paths(self):
        """
        Creates a solver instance and encodes the paths in the graph.

        This method initializes the solver with the specified parameters and encodes the paths
        by creating variables for edges and subpaths.

        If external solution paths are provided, it skips the solver creation.

        !!! warning "Call this method before encoding other variables and constraints."
        
            Always call this method before encoding other variables and constraints on the paths.

        """
        if self.external_solution_paths is not None:
            return

        self.solver = sw.SolverWrapper(**self.solver_options)

        self._encode_paths()

    def _encode_paths(self):
        
        # Encodes the paths in the graph by creating variables for edges and subpaths.

        # This method initializes the edge and subpath variables for the solver and adds constraints
        # to ensure the paths are valid according to the given subpath constraints and safe lists.
        
        self.edge_indexes = [
            (u, v, i) for i in range(self.k) for (u, v) in self.G.edges()
        ]
        self.path_indexes = [(i) for i in range(self.k)]
        if len(self.subpath_constraints) > 0:
            self.subpath_indexes = [
                (i, j) for i in range(self.k) for j in range(len(self.subpath_constraints))
            ]


        ################################
        #                              #
        #       Encoding paths         #
        #                              #
        ################################

        # The identifiers of the constraints come from https://arxiv.org/pdf/2201.10923 page 14-15

        self.edge_vars = self.solver.add_variables(self.edge_indexes, name_prefix="edge", lb=0, ub=1, var_type="integer")

        for i in range(self.k):
            
            if not self.allow_empty_paths:
                self.solver.add_constraint(
                    self.solver.quicksum(
                        self.edge_vars[(self.G.source, v, i)]
                        for v in self.G.successors(self.G.source)
                    )
                    == 1,
                    name=f"10a_i={i}",
                )
            else:
                self.solver.add_constraint(
                    self.solver.quicksum(
                        self.edge_vars[(self.G.source, v, i)]
                        for v in self.G.successors(self.G.source)
                    )
                    <= 1,
                    name=f"10a_i={i}",
                )
            # Not needed, follows from the others
            # self.solver.add_constraint(
            #     self.solver.quicksum(
            #         self.edge_vars[(u, self.G.sink, i)]
            #         for u in self.G.predecessors(self.G.sink)
            #     )
            #     == 1,
            #     name=f"10b_i={i}",
            # )

        for i in range(self.k):
            for v in self.G.nodes:  # find all edges u->v->w for v in V\{s,t}
                if v == self.G.source or v == self.G.sink:
                    continue
                self.solver.add_constraint(
                    self.solver.quicksum(self.edge_vars[(u, v, i)] for u in self.G.predecessors(v))
                    - self.solver.quicksum(self.edge_vars[(v, w, i)] for w in self.G.successors(v))
                    == 0,
                    f"10c_v={v}_i={i}",
                )

        ################################
        #                              #
        # Encoding subpath constraints #
        #                              #
        ################################

        # Example of a subpath constraint: R=[ [(1,3),(3,5)], [(0,1)] ], means that we have 2 paths to cover, the first one is 1-3-5. the second path is just a single edge 0-1

        if len(self.subpath_constraints) > 0:
            self.subpaths_vars = self.solver.add_variables(
                self.subpath_indexes, name_prefix="r", lb=0, ub=1, var_type="integer")
        
            for i in range(self.k):
                for j in range(len(self.subpath_constraints)):

                    if self.subpath_constraints_coverage_length is None:
                        # By default, the length of the constraints is its number of edges 
                        constraint_length = len(self.subpath_constraints[j])
                        # And the fraction of edges that we need to cover is self.subpath_constraints_coverage
                        coverage_fraction = self.subpath_constraints_coverage
                        self.solver.add_constraint(
                            self.solver.quicksum(self.edge_vars[(e[0], e[1], i)] for e in self.subpath_constraints[j])
                            >= constraint_length * coverage_fraction
                            * self.subpaths_vars[(i, j)],
                            name=f"7a_i={i}_j={j}",
                        )
                    else:
                        # If however we specified that the coverage fraction is in terms of edge lengths
                        # Then the constraints length is the sum of the lengths of the edges,
                        # where each edge without a length gets length 1
                        constraint_length = sum(self.G[u][v].get(self.length_attr, 1) for (u,v) in self.subpath_constraints[j])
                        # And the fraction of edges that we need to cover is self.subpath_constraints_coverage_length
                        coverage_fraction = self.subpath_constraints_coverage_length
                        self.solver.add_constraint(
                            self.solver.quicksum(self.edge_vars[(e[0], e[1], i)] * self.G[e[0]][e[1]].get(self.length_attr, 1) for e in self.subpath_constraints[j])
                            >= constraint_length * coverage_fraction
                            * self.subpaths_vars[(i, j)],
                            name=f"7a_i={i}_j={j}",
                        )
            for j in range(len(self.subpath_constraints)):
                self.solver.add_constraint(
                    self.solver.quicksum(self.subpaths_vars[(i, j)] for i in range(self.k)) >= 1,
                    name=f"7b_j={j}",
                )

        ###############################
        #                             #
        # Encoding position variables #
        #                             #
        ###############################

        # edge_position_vars[(u, v, i)] = position (i.e., index) 
        # of the edge (u, v) in the path i, starting from position 0. 
        if self.encode_edge_position:
            max_length = self.G.number_of_nodes()
            if self.length_attr is not None:
                max_length = sum(self.G[u][v].get(self.length_attr, 1) for (u,v) in self.G.edges())
            self.edge_position_vars = self.solver.add_variables(
                self.edge_indexes, name_prefix="position", lb=0, ub=max_length, var_type="integer"
            )
            for i in range(self.k):
                for (u,v) in self.G.edges():
                    self.solver.add_constraint(
                        self.edge_position_vars[(u, v, i)] 
                            == self.solver.quicksum(
                                self.edge_vars[(edge[0], edge[1], i)] 
                                * self.G[edge[0]][edge[1]].get(self.length_attr, 1) 
                                for edge in self.G.reachable_edges_rev_from[u]
                                ),
                        name=f"position_u={u}_v={v}_i={i}"
                    )

        # path_length_vars[(i)] = length of path i
        if self.encode_edge_position:
            max_length = self.G.number_of_nodes()
            if self.length_attr is not None:
                max_length = sum(self.G[u][v].get(self.length_attr, 1) for (u,v) in self.G.edges())
            self.path_length_vars = self.solver.add_variables(
                self.path_indexes, name_prefix="path_length", lb=0, ub=max_length, var_type="integer"
            )
            for i in range(self.k):
                self.solver.add_constraint(
                    self.path_length_vars[(i)] 
                        == self.solver.quicksum(
                            self.edge_vars[(edge[0], edge[1], i)] 
                            * self.G[edge[0]][edge[1]].get(self.length_attr, 1) 
                            for edge in self.G.edges()
                            ),
                    name=f"path_length_constr_i={i}"
                )

        ########################################
        #                                      #
        # Fixing variables based on safe lists #
        #                                      #
        ########################################

        if self.safe_lists is not None:
            paths_to_fix = self._get_paths_to_fix_from_safe_lists()

            if not self.optimize_with_safety_as_subpath_constraints:
                # iterating over safe lists
                for i in range(min(len(paths_to_fix), self.k)):
                    # print("Fixing variables for safe list #", i)
                    # iterate over the edges in the safe list to fix variables to 1
                    for u, v in paths_to_fix[i]:
                        self.solver.add_constraint(
                            self.edge_vars[(u, v, i)] == 1,
                            name=f"safe_list_u={u}_v={v}_i={i}",
                        )

                    if self.optimize_with_safe_zero_edges:
                        # get the endpoints of the longest safe path in the sequence
                        first_node, last_node = (
                            safetypathcovers.get_endpoints_of_longest_safe_path_in(paths_to_fix[i])
                        )
                        # get the reachable nodes from the last node
                        reachable_nodes = self.G.reachable_nodes_from[last_node]
                        # get the backwards reachable nodes from the first node
                        reachable_nodes_reverse = self.G.reachable_nodes_rev_from[first_node]
                        # get the edges in the path
                        path_edges = set((u, v) for (u, v) in paths_to_fix[i])

                        for u, v in self.G.base_graph.edges():
                            if (
                                (u, v) not in path_edges
                                and u not in reachable_nodes
                                and v not in reachable_nodes_reverse
                            ):
                                # print(f"Adding zero constraint for edge ({u}, {v}) in path {i}")
                                self.solver.add_constraint(
                                    self.edge_vars[(u, v, i)] == 0,
                                    name=f"safe_list_zero_edge_u={u}_v={v}_i={i}",
                                )


    def _get_paths_to_fix_from_safe_lists(self) -> list:
        
        # Returns the paths to fix based on the safe lists.
        # The method finds the longest safe list for each edge and returns the paths to fix based on the longest safe list.

        # If we have no safe lists, we return an empty list
        if self.safe_lists is None or len(self.safe_lists) == 0:
            return []

        # for i, safe_list in enumerate(self.safe_lists):
        #     utils.logger.debug(f"{__name__}: safe_list {i}: {safe_list}")        

        # utils.draw(self.G, 
        #            filename = "debug_safe_lists.pdf", 
        #            subpath_constraints = self.safe_lists)

        large_constant = 0
        if self.optimize_with_safety_from_largest_antichain:
            large_constant = self.G.number_of_edges() * self.G.number_of_edges()

        longest_safe_list = dict()
        for i, safe_list in enumerate(self.safe_lists):
            for edge in safe_list:
                if edge not in longest_safe_list:
                    longest_safe_list[edge] = i
                elif len(self.safe_lists[longest_safe_list[edge]]) < len(safe_list):
                    longest_safe_list[edge] = i

        len_of_longest_safe_list = {
            edge: large_constant + len(self.safe_lists[longest_safe_list[edge]])
            for edge in longest_safe_list
        }
        # for edge, length in len_of_longest_safe_list.items():
        #     utils.logger.debug(f"{__name__}: edge {edge} has longest safe list of length {length} at index {longest_safe_list[edge]}")

        _, edge_antichain = self.G.compute_max_edge_antichain(
            get_antichain=True, weight_function=len_of_longest_safe_list
        )
        utils.logger.debug(f"{__name__}: edge_antichain from safe lists SIZE: {len(edge_antichain)}")
        # utils.logger.debug(f"{__name__}: edge_antichain from safe lists: {len(edge_antichain)}")

        # paths_to_fix = list(
        #     map(lambda edge: self.safe_lists[longest_safe_list[edge]], edge_antichain)
        # )
        paths_to_fix = []
        for edge in edge_antichain:
            # utils.logger.debug(f"{__name__}: edge {edge} in edge_antichain, longest safe list idx: {longest_safe_list[edge]}, safe list: {self.safe_lists[longest_safe_list[edge]]}")
            paths_to_fix.append(self.safe_lists[longest_safe_list[edge]])

        utils.logger.debug(f"{__name__}: paths_to_fix from safe lists SIZE: {len(paths_to_fix)}")
        # utils.logger.debug(f"{__name__}: paths_to_fix from safe lists: {paths_to_fix}")
        
        # utils.draw(self.G, 
        #            filename = "debug_paths_to_fix.pdf", 
        #            subpath_constraints = paths_to_fix)

        return paths_to_fix
    
    def _check_valid_subpath_constraints(self):
        """
        Checks if the subpath constraints are valid.

        Parameters
        ----------
        - subpath_constraints (list): The subpath constraints to be checked.

        Returns
        ----------
        - True if the subpath constraints are valid, False otherwise.

        The method checks if the subpath constraints are valid by ensuring that each subpath
        is a valid path in the graph.
        """

        # Check that self.subpath_constraints is a list of lists
        if not all(isinstance(subpath, list) for subpath in self.subpath_constraints):
            utils.logger.error(f"{__name__}: subpath_constraints must be a list of lists of edges.")
            raise ValueError("subpath_constraints must be a list of lists of edges.")

        for subpath in self.subpath_constraints:
            # Check that each subpath has at least one edge
            if len(subpath) == 0:
                utils.logger.error(f"{__name__}: subpath {subpath} must have at least 1 edge.")
                raise ValueError(f"Subpath {subpath} must have at least 1 edge.")
            # Check that each subpath is a list of tuples of two nodes (edges)
            if not all(isinstance(e, tuple) and len(e) == 2 for e in subpath):
                utils.logger.error(f"{__name__}: each subpath must be a list of edges, where each edge is a tuple of two nodes.")
                raise ValueError("Each subpath must be a list of edges, where each edge is a tuple of two nodes.")
            # Check that each edge in the subpath is in the graph
            for e in subpath:
                if not self.G.has_edge(e[0], e[1]):
                    utils.logger.error(f"{__name__}: subpath {subpath} contains the edge {e} which is not in the graph.")
                    raise ValueError(f"Subpath {subpath} contains the edge {e} which is not in the graph.")


    def solve(self) -> bool:
        """
        Solves the optimization model for the current instance.

        Returns
        ----------
        - True if the model is solved successfully, False otherwise.

        The method first checks if an external solution is already provided. If so, it sets the
        solved attribute to True and returns True.

        If not, it optimizes the model using the solver, and records the solve time and solver status
        in the solve_statistics dictionary. If the solver status indicates an optimal solution
        (either 'kOptimal' (highs) or status code 2 (gurobi)), it sets the solved attribute to True and returns True.
        Otherwise, it sets the solved attribute to False and returns False.
        """
        utils.logger.info(f"{__name__}: solving...")

        # If we already received an external solution, we don't need to solve the model
        if self.external_solution_paths is not None:
            utils.logger.info(f"{__name__}: no need to solve, we have an external solution.")
            self._is_solved = True
            return True

        # self.write_model(f"model-{self.id}.lp")
        start_time = time.perf_counter()
        self.solver.optimize()
        self.solve_statistics[f"milp_solve_time_for_num_paths_{self.k}"] = (
            time.perf_counter() - start_time
        )

        self.solve_statistics[f"milp_solver_status_for_num_paths_{self.k}"] = (
            self.solver.get_model_status()
        )

        if (
            self.solver.get_model_status() == "kOptimal"
            or self.solver.get_model_status() == 2
        ):
            self._is_solved = True
            utils.logger.info(f"{__name__}: solved successfully. Objective value: {self.get_objective_value()}")
            return True

        self._is_solved = False
        return False

    def check_is_solved(self):
        if not self.is_solved():
            utils.logger.error(f"{__name__}: Model not solved. If you want to solve it, call the `solve` method first.")
            raise Exception(
                "Model not solved. If you want to solve it, call the `solve` method first. \
                  If you already ran the `solve` method, then the model is infeasible, or you need to increase parameter time_limit.")
        
    def is_solved(self):
        return self._is_solved
    
    def set_solved(self):
        self._is_solved = True

    @abstractmethod
    def get_solution(self):
        """
        Implement this class in the child class to return the full solution of the model.
        The solution paths are obtained with the get_solution_paths method.
        """
        pass

    @abstractmethod
    def get_lowerbound_k(self):
        """
        Implement this class in the child class to return a lower bound on the number of solution paths to the model.
        If you have no lower bound, you should implement this method to return 1.
        """
        pass

    def get_solution_paths(self) -> list:
        """
        Retrieves the solution paths from the graph.

        This method returns the solution paths either from the external solution paths
        if they are provided at initialization time, or by calculating them based on the
        edge variable solutions.

        Returns
        ----------
        - A list of paths, where each path is represented as a list of vertices.
        """
        if self.external_solution_paths is not None:
            return self.external_solution_paths

        if self.edge_vars_sol == {}:
            self.edge_vars_sol = self.solver.get_values(self.edge_vars, binary_values=True)

        paths = []
        for i in range(self.k):
            vertex = self.G.source
            # checking if there is a path from source to sink
            found_path = False
            for out_neighbor in self.G.successors(vertex):
                if self.edge_vars_sol[(str(vertex), str(out_neighbor), i)] == 1:
                    found_path = True
                    break
            if not found_path:
                path = []
                paths.append(path)
                # print("Warning: No path found for path index", i)
            else:
                path = [vertex]
                while vertex != self.G.sink:
                    for out_neighbor in self.G.successors(vertex):
                        if self.edge_vars_sol[(str(vertex), str(out_neighbor), i)] == 1:
                            vertex = out_neighbor
                            break
                    path.append(vertex)
                if len(path) < 2:
                    utils.logger.error(f"{__name__}: Something went wrong, solution path {path} has less than 2 vertices. This should not happen. Make sure the stDAG has no edge from global source {self.G.source} to global sink {self.G.sink}.")
                    raise Exception(f"Something went wrong, solution path {path} has less than 2 vertices. This should not happen. Make sure the stDAG has no edge from global source {self.G.source} to global sink {self.G.sink}.")

                # We remove the first and the last vertex, because
                # these are the global source and the global sink introduced by stDAG
                paths.append(path[1:-1])

        return paths

    @abstractmethod
    def is_valid_solution(self) -> bool:
        """
        Implement this class in the child class to perform a basic check whether the solution is valid.
        
        If you cannot perform such a check, provide an implementation that always returns True.
        """
        pass

    def verify_edge_position(self):
        
        if not self.encode_edge_position:
            return True
        
        self.check_is_solved()

        paths = self.get_solution_paths()

        edge_position_sol = self.solver.get_values(self.edge_position_vars)

        for path_index, path in enumerate(paths):
            current_edge_position = 0
            path_temp = [self.G.source] + path
            for (u,v) in zip(path_temp[:-1], path_temp[1:]):
                if round(edge_position_sol[(str(u), str(v), path_index)]) != current_edge_position:
                    return False
                current_edge_position += self.G[u][v].get(self.length_attr, 1)
        return True
    
    def verify_path_length(self):
        
        if not self.encode_path_length:
            return True
        
        self.check_is_solved()

        paths = self.get_solution_paths()

        path_length_sol = self.solver.get_values(self.path_length_vars)

        for path_index, path in enumerate(paths):
            if len(path) > 0:
                path_temp = [self.G.source] + path + [self.G.sink]            
                path_length = 0
                for (u,v) in zip(path_temp[:-1], path_temp[1:]):
                    path_length += self.G[u][v].get(self.length_attr, 1)   

                if round(path_length_sol[(path_index)]) != path_length:
                    return False
    
    
        return True

    @abstractmethod
    def get_objective_value(self):
        """
        Implement this class in the child class to return the objective value of the model. This is needed to be able to
        compute the safe paths (i.e. those appearing any optimum solution) for any child class.

        A basic objective value is `k` (when we're trying to minimize the number of paths). If your model has a different
        objective, you should implement this method to return the objective value of the model. If your model has no objective value,
        you should implement this method to return None.
        """
        pass