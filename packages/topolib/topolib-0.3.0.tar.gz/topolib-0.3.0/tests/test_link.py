import pytest
from topolib.elements.node import Node
from topolib.elements.link import Link


def test_link_creation_and_properties():
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    link = Link(10, n1, n2, 5.5)

    assert link.id == 10
    assert link.source is n1
    assert link.target is n2
    assert link.length == 5.5


def test_link_length_validation():
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    with pytest.raises(ValueError):
        Link(1, n1, n2, -1)
    with pytest.raises(TypeError):
        Link(1, n1, n2, "not-a-number")


def test_link_endpoint_validation():
    n1 = Node(1, "A", 0.0, 0.0)

    # a dummy object without node attributes
    class Dummy:
        pass

    with pytest.raises(TypeError):
        Link(1, Dummy(), n1, 1.0)
    with pytest.raises(TypeError):
        Link(1, n1, Dummy(), 1.0)


def test_endpoints_and_repr():
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    link = Link(2, n1, n2, 10)
    assert link.endpoints() == (n1, n2)
    assert "Link(id=2" in repr(link)


def test_link_setters_and_errors():
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    link = Link(99, n1, n2, 1.0)
    # Test id setter
    link.id = 123
    assert link.id == 123

    # Test source setter error
    class Dummy:
        pass

    with pytest.raises(TypeError):
        link.source = Dummy()
    # Test target setter error
    with pytest.raises(TypeError):
        link.target = Dummy()
    # Test length setter error (non-numeric)
    with pytest.raises(TypeError):
        link.length = "bad"
    # Test length setter error (negative)
    with pytest.raises(ValueError):
        link.length = -5


def test_link_length_setter_typeerror():
    n1 = Node(1, "A", 0.0, 0.0)
    n2 = Node(2, "B", 1.0, 1.0)
    link = Link(1, n1, n2, 1.0)
    with pytest.raises(TypeError):
        link.length = object()  # No convertible a float, cubre el except
