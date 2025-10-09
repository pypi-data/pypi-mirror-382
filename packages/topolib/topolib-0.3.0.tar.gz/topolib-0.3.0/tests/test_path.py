import pytest
from topolib.topology.path import Path


class DummyNode:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f"Node({self.id})"


class DummyLink:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f"Link({self.id})"


def test_path_creation():
    nodes = [DummyNode(1), DummyNode(2), DummyNode(3)]
    links = [DummyLink("a"), DummyLink("b")]
    path = Path(nodes, links)
    assert path.nodes == nodes
    assert path.links == links
    assert path.length() == 2
    assert path.hop_count() == 2
    assert path.endpoints() == (nodes[0], nodes[-1])


def test_path_invalid():
    with pytest.raises(ValueError):
        Path([], [])
    with pytest.raises(ValueError):
        Path([DummyNode(1)], [])
    with pytest.raises(ValueError):
        Path([DummyNode(1), DummyNode(2)], [DummyLink("a"), DummyLink("b")])


def test_path_repr():
    nodes = [DummyNode(1), DummyNode(2)]
    links = [DummyLink("a")]
    path = Path(nodes, links)
    s = repr(path)
    assert s.startswith("Path(nodes=")
