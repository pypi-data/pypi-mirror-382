import pytest

from topolib.analysis.metrics import Metrics
from topolib.topology import Topology


from topolib.elements.node import Node
from topolib.elements.link import Link


def test_node_degree():
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    n3 = Node(3, "C", 2.0, 2.0)
    l1 = Link(1, n1, n2, 10)
    l2 = Link(2, n2, n3, 20)
    topo = Topology(nodes=[n1, n2, n3], links=[l1, l2])
    result = Metrics.node_degree(topo)
    assert result == {1: 1, 2: 2, 3: 1}


def test_link_length_stats():
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    l1 = Link(1, n1, n2, 10)
    l2 = Link(2, n2, n1, 20)
    topo = Topology(nodes=[n1, n2], links=[l1, l2])
    stats = Metrics.link_length_stats(topo)
    assert stats["min"] == 10
    assert stats["max"] == 20
    assert stats["avg"] == 15
    # Empty case
    topo_empty = Topology()
    assert Metrics.link_length_stats(topo_empty) == {
        "min": None,
        "max": None,
        "avg": None,
    }


def test_connection_matrix():
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    n3 = Node(3, "C", 2.0, 2.0)
    l1 = Link(1, n1, n2, 10)
    l2 = Link(2, n2, n3, 20)
    topo = Topology(nodes=[n1, n2, n3], links=[l1, l2])
    matrix = Metrics.connection_matrix(topo)
    assert matrix == [
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0],
    ]
