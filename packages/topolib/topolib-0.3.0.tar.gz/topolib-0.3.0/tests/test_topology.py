"""
Unit tests for the Topology class.
Covers all public methods, success and error cases, and adjacency matrix validation (numpy), including NetworkX integration.
"""

import pytest
import numpy as np
from topolib.topology import Topology
from topolib.elements.node import Node
from topolib.elements.link import Link


def test_add_and_get_nodes():
    topo = Topology()
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    topo.add_node(n1)
    topo.add_node(n2)
    assert n1 in topo.nodes and n2 in topo.nodes
    assert len(topo.nodes) == 2
    # Check that nodes are present in the internal networkx graph
    assert n1.id in topo._graph.nodes  # type: ignore
    assert n2.id in topo._graph.nodes  # type: ignore


def test_add_duplicate_node_allowed():
    # The current design allows duplicate nodes (no check in Topology)
    topo = Topology()
    n1 = Node(1, "A", 0.0, 0.0)
    topo.add_node(n1)
    topo.add_node(n1)
    assert topo.nodes.count(n1) == 2


def test_remove_node():
    topo = Topology()
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    topo.add_node(n1)
    topo.add_node(n2)
    topo.remove_node(n1.id)
    assert n1 not in topo.nodes
    assert n2 in topo.nodes
    # Check that the node was removed from the internal graph
    assert n1.id not in topo._graph.nodes  # type: ignore


def test_remove_nonexistent_node():
    import networkx as nx

    topo = Topology()
    n1 = Node(1, "A", 0.0, 0.0)
    # Should raise NetworkXError when trying to remove a node not in the graph
    with pytest.raises(nx.NetworkXError):
        topo.remove_node(n1.id)
    assert n1 not in topo.nodes


def test_add_and_get_links():
    topo = Topology()
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    topo.add_node(n1)
    topo.add_node(n2)
    l1 = Link(1, n1, n2, 10.0)
    topo.add_link(l1)
    assert l1 in topo.links
    assert len(topo.links) == 1
    # Check that the edge is present in the internal networkx graph
    assert topo._graph.has_edge(n1.id, n2.id)  # type: ignore


def test_add_link_with_missing_nodes():
    # The current design allows adding links even if nodes are not in the topology
    topo = Topology()
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    l1 = Link(1, n1, n2, 10.0)
    topo.add_link(l1)
    assert l1 in topo.links


def test_remove_link():
    topo = Topology()
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    topo.add_node(n1)
    topo.add_node(n2)
    l1 = Link(1, n1, n2, 10.0)
    topo.add_link(l1)
    topo.remove_link(l1.id)
    assert l1 not in topo.links
    # Check that the edge was removed from the internal graph
    assert not topo._graph.has_edge(n1.id, n2.id)  # type: ignore


def test_remove_nonexistent_link():
    topo = Topology()
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    topo.add_node(n1)
    topo.add_node(n2)
    # Should not raise, just does nothing
    topo.remove_link(999)
    assert len(topo.links) == 0


def test_adjacency_matrix():
    topo = Topology()
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    n3 = Node(3, "C", 2.0, 2.0)
    topo.add_node(n1)
    topo.add_node(n2)
    topo.add_node(n3)
    l1 = Link(1, n1, n2, 10.0)
    l2 = Link(2, n2, n3, 20.0)
    topo.add_link(l1)
    topo.add_link(l2)
    matrix = topo.adjacency_matrix()
    assert isinstance(matrix, np.ndarray)
    assert matrix.shape == (3, 3)
    # Check connections
    idx = {n.id: i for i, n in enumerate(topo.nodes)}
    assert matrix[idx[n1.id], idx[n2.id]] == 1
    assert matrix[idx[n2.id], idx[n3.id]] == 1
    assert matrix[idx[n1.id], idx[n3.id]] == 0
    # Validate with networkx adjacency
    adj_nx = np.asarray(
        np.array(
            [
                [1 if topo._graph.has_edge(n1.id, n2.id) else 0 for n2 in topo.nodes]  # type: ignore
                for n1 in topo.nodes
            ]
        )
    )
    assert np.array_equal(matrix, adj_nx)


def test_adjacency_matrix_empty():
    topo = Topology()
    matrix = topo.adjacency_matrix()
    assert isinstance(matrix, np.ndarray)
    assert matrix.shape == (0, 0)
