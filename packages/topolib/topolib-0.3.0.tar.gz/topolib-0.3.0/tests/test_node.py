import pytest
from topolib.elements.node import Node


def test_node_creation():
    node = Node(1, "A", -33.45, -70.66)
    assert node.id == 1
    assert node.name == "A"
    assert node.latitude == -33.45
    assert node.longitude == -70.66


def test_node_setters():
    node = Node(0, "", 0.0, 0.0)
    node.id = 10
    node.name = "TestNode"
    node.latitude = 55.5
    node.longitude = -120.1
    assert node.id == 10
    assert node.name == "TestNode"
    assert node.latitude == 55.5
    assert node.longitude == -120.1


def test_node_coordinates():
    node = Node(2, "B", 10.0, 20.0)
    coords = node.coordinates()
    assert coords == (10.0, 20.0)
