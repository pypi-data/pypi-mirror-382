"""
Node class for optical network topologies.

This module defines the Node class, representing a network node with geographic coordinates.
"""

from typing import Tuple


class Node:
    """
    .. :noindex:

    Represents a node in an optical network topology.

    :param id: Unique identifier for the node.
    :type id: int
    :param name: Name of the node.
    :type name: str
    :param latitude: Latitude coordinate of the node.
    :type latitude: float
    :param longitude: Longitude coordinate of the node.
    :type longitude: float
    """

    def __init__(self, id: int, name: str, latitude: float, longitude: float):
        self._id = id
        self._name = name
        self._latitude = latitude
        self._longitude = longitude

    @property
    def id(self) -> int:
        """
        Get the unique identifier of the node.

        :return: Node ID.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """
        Set the unique identifier of the node.

        :param value: Node ID.
        :type value: int
        """
        self._id = value

    @property
    def name(self) -> str:
        """
        Get the name of the node.

        :return: Node name.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        Set the name of the node.

        :param value: Node name.
        :type value: str
        """
        self._name = value

    @property
    def latitude(self) -> float:
        """
        Get the latitude coordinate of the node.

        :return: Latitude value.
        :rtype: float
        """
        return self._latitude

    @latitude.setter
    def latitude(self, value: float) -> None:
        """
        Set the latitude coordinate of the node.

        :param value: Latitude value.
        :type value: float
        """
        self._latitude = value

    @property
    def longitude(self) -> float:
        """
        Get the longitude coordinate of the node.

        :return: Longitude value.
        :rtype: float
        """
        return self._longitude

    @longitude.setter
    def longitude(self, value: float) -> None:
        """
        Set the longitude coordinate of the node.

        :param value: Longitude value.
        :type value: float
        """
        self._longitude = value

    def coordinates(self) -> Tuple[float, float]:
        """
        Returns the (latitude, longitude) coordinates of the node.

        :return: Tuple containing latitude and longitude.
        :rtype: Tuple[float, float]
        """
        return self._latitude, self._longitude
