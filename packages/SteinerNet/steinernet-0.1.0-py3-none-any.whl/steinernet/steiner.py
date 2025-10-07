# steinernet/steiner.py

"""
Steiner Tree Algorithms Interface

This module implements various heuristic and exact methods for computing Steiner trees on graphs.

@references
1. Petter, L., Hammer. Path heuristic and Original path heuristic, Section 4.1.3 of the book "The Steiner tree Problem"
2. H. Takahashi and A. Matsuyama, "An approximate solution for the Steiner problem in graphs"
3. F. K. Hwang, D. S. Richards and P. Winter, "The Steiner Tree Problem", Kruskal-Based Heuristic, Section 4.1.4, ISBN: 978-0-444-89098-6
4. Afshin Sadeghi and Holger Froehlich, "Steiner tree methods for optimal sub-network identification: an empirical study", BMC Bioinformatics 2013 14:144
5. F. K. Hwang, D. S. Richards and P. Winter, "The Steiner Tree Problem", Optimal solution for Steiner trees on networks, ISBN: 978-0-444-89098-6
"""

import networkx as nx
import random
import itertools
from .random_walk_tree import random_walk_tree

class SteinerNet:
    """
    Unified interface for computing Steiner trees using multiple algorithms.

    Methods:
        - steinertree: Dispatch algorithm selector
        - SP: Shortest path heuristic [Ref 1]
        - KB: Kruskal-based heuristic [Ref 3]
        - RSP: Randomized shortest paths [Ref 4]
        - SPM: Shortest path-based MST [Ref 2]
        - ASP: All shortest paths union [Ref 4]
        - EXA: Brute-force exact Steiner tree [Ref 5]
        - RW: Random walk Steiner tree [Ref 4]
    """

    def __init__(self, G):
        """
        Initialize the SteinerNet object.

        Parameters:
        G (networkx.Graph): The input graph.
        """
        self.G = G.copy()

    def steinertree(self, terminals, method='SP', repeats=70, optimize=True):
        """
        Compute Steiner tree using selected method.

        Parameters:
        terminals (list): Terminal node IDs.
        method (str): One of 'SP', 'KB', 'RSP', 'SPM', 'ASP', 'EXA', 'RW'.
        repeats (int): Repeats for stochastic methods.
        optimize (bool): Prune tree after construction (for heuristics).

        Returns:
        networkx.Graph: Resulting Steiner tree.
        """
        method = method.upper()
        if method == 'SP':
            return self._shortest_path_heuristic(terminals)
        elif method == 'KB':
            return self._key_node_based(terminals, repeats, optimize)
        elif method == 'RSP':
            return self._randomized_sp(terminals, repeats)
        elif method == 'SPM':
            return self._shortest_path_mst(terminals)
        elif method == 'ASP':
            return self._all_shortest_paths_union(terminals)
        elif method == 'EXA':
            return self._exact_algorithm(terminals)
        elif method == 'RW':
            return self._random_walk(terminals)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _random_walk(self, terminals):
        """
        RW method: Steiner tree by random walk strategy.
        Reference: Sadeghi & Froehlich, BMC Bioinformatics 2013 [Ref 4]
        """
        return random_walk_tree(self.G, terminals)

    def _shortest_path_heuristic(self, terminals):
        T = nx.Graph()
        for i, t1 in enumerate(terminals):
            for t2 in terminals[i+1:]:
                path = nx.shortest_path(self.G, t1, t2, weight='weight')
                nx.add_path(T, path)
        return T

    def _key_node_based(self, terminals, repeats, optimize):
        best_tree = None
        best_score = float('inf')
        nodes = list(self.G.nodes())

        for _ in range(repeats):
            added_nodes = terminals + random.sample([n for n in nodes if n not in terminals], max(1, len(terminals) // 2))
            subgraph = self.G.subgraph(added_nodes)
            T = nx.minimum_spanning_tree(subgraph, weight='weight')
            if optimize:
                T = self._prune_tree(T, terminals)
            score = T.size(weight='weight')
            if score < best_score:
                best_score = score
                best_tree = T

        return best_tree

    def _randomized_sp(self, terminals, repeats):
        best_tree = None
        best_score = float('inf')

        for _ in range(repeats):
            T = nx.Graph()
            t_perm = random.sample(terminals, len(terminals))
            for i in range(len(t_perm)-1):
                path = nx.shortest_path(self.G, t_perm[i], t_perm[i+1], weight='weight')
                nx.add_path(T, path)
            T = self._prune_tree(T, terminals)
            score = T.size(weight='weight')
            if score < best_score:
                best_score = score
                best_tree = T

        return best_tree

    def _shortest_path_mst(self, terminals):
        H = nx.Graph()
        for i, t1 in enumerate(terminals):
            for t2 in terminals[i+1:]:
                path = nx.shortest_path(self.G, t1, t2, weight='weight')
                nx.add_path(H, path)
        T = nx.minimum_spanning_tree(H, weight='weight')
        return T

    def _all_shortest_paths_union(self, terminals):
        T = nx.Graph()
        for i, t1 in enumerate(terminals):
            for t2 in terminals[i+1:]:
                path = nx.shortest_path(self.G, t1, t2, weight='weight')
                nx.add_path(T, path)
        return T

    def _exact_algorithm(self, terminals):
        best_tree = None
        best_cost = float('inf')

        non_terminals = [n for n in self.G.nodes() if n not in terminals]
        for r in range(len(non_terminals) + 1):
            for subset in itertools.combinations(non_terminals, r):
                nodes_subset = list(terminals) + list(subset)
                subgraph = self.G.subgraph(nodes_subset)
                if nx.is_connected(subgraph):
                    T = nx.minimum_spanning_tree(subgraph, weight='weight')
                    cost = T.size(weight='weight')
                    if cost < best_cost:
                        best_cost = cost
                        best_tree = T
        return best_tree

    def _prune_tree(self, tree, terminals):
        T = tree.copy()
        removable = [n for n in T.nodes() if n not in terminals]
        removed = True
        while removed:
            removed = False
            for n in removable:
                if T.degree(n) == 1:
                    T.remove_node(n)
                    removed = True
        return T
