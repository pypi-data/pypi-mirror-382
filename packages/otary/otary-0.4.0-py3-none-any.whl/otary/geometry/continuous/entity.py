"""
ContinuousGeometryEntity module class
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import cv2
import numpy as np
from numpy.typing import NDArray

from otary.geometry.entity import GeometryEntity
from otary.geometry import Polygon, Rectangle, AxisAlignedRectangle


class ContinuousGeometryEntity(GeometryEntity, ABC):
    """
    ContinuousGeometryEntity class which is the abstract base class for
    continuous or smooth geometry objects like circles, ellipse, etc...
    """

    DEFAULT_N_POLY_APPROX = 1000  # number of pts to use in polygonal approximation

    def __init__(self, n_points_polygonal_approx: int = DEFAULT_N_POLY_APPROX):
        """Initialize a ContinuousGeometryEntity object

        Args:
            n_points_polygonal_approx (int, optional): n points to be used in
                the polygonal approximation.
                Defaults to DEFAULT_N_POINTS_POLYGONAL_APPROX.
        """
        self._n_points_polygonal_approx = n_points_polygonal_approx
        # self._polyapprox = is defined in subclasses

    # --------------------------------- PROPERTIES ------------------------------------

    @property
    def n_points_polygonal_approx(self) -> int:
        """Get the number of points for the polygonal approximation.

        Returns:
            int: The number of points used in the polygonal approximation.
        """
        return self._n_points_polygonal_approx

    @n_points_polygonal_approx.setter
    def n_points_polygonal_approx(self, value):
        """
        Set the number of points for the polygonal approximation.
        This would also update the polygonal approximation of the geometry entity.

        Args:
            value (int): The number of points to be used in the polygonal approximation.
        """
        self._n_points_polygonal_approx = value
        self.update_polyapprox()

    @property
    def polyaprox(self) -> Polygon:
        """Generate a polygonal approximation of the continuous geometry entity.

        Beware: No setter is defined for this property as it is a read-only property.
        You can update the polygonal approximation using the method named
        `update_polyapprox`.

        Returns:
            Polygon: polygonal approximation of the continuous geometry entity
        """
        return self._polyapprox

    @abstractmethod
    def polygonal_approx(self, n_points: int, is_cast_int: bool) -> Polygon:
        """Generate a polygonal approximation of the continuous geometry entity

        Args:
            n_points (int): number of points that make up the polygonal
                approximation. The bigger the better to obtain more precise
                results in intersection or other similar computations.

        Returns:
            Polygon: polygonal approximation of the continuous geometry entity
        """

    @abstractmethod
    def curvature(self, point: NDArray) -> float:
        """Curvature at the point defined as parameter

        Args:
            point (NDArray): input point.

        Returns:
            float: _description_
        """

    @property
    def xmax(self) -> float:
        """Get the maximum X coordinate of the geometry entity

        Returns:
            np.ndarray: 2D point
        """
        return self.polyaprox.xmax

    @property
    def xmin(self) -> float:
        """Get the minimum X coordinate of the geometry entity

        Returns:
            np.ndarray: 2D point
        """
        return self.polyaprox.xmin

    @property
    def ymax(self) -> float:
        """Get the maximum Y coordinate of the geometry entity

        Returns:
            np.ndarray: 2D point
        """
        return self.polyaprox.ymax

    @property
    def ymin(self) -> float:
        """Get the minimum Y coordinate of the geometry entity

        Returns:
            np.ndarray: 2D point
        """
        return self.polyaprox.ymin

    # ---------------------------- MODIFICATION METHODS -------------------------------

    # done in the derived classes

    # ------------------------------- CLASSIC METHODS ---------------------------------

    def update_polyapprox(self) -> None:
        """Update the polygonal approximation of the continuous geometry entity"""
        # pylint: disable=attribute-defined-outside-init
        self._polyapprox = self.polygonal_approx(
            n_points=self.n_points_polygonal_approx, is_cast_int=False
        )

    def enclosing_axis_aligned_bbox(self) -> AxisAlignedRectangle:
        """Compute the smallest area enclosing Axis-Aligned Bounding Box (AABB)
        See: https://docs.opencv.org/3.4/dd/d49/tutorial_py_contour_features.html

        Returns:
            AxisAlignedRectangle: AxisAlignedRectangle object
        """
        topleft_x, topleft_y, width, height = cv2.boundingRect(
            array=self.polyaprox.asarray.astype(np.float32)
        )
        topleft = np.array([topleft_x, topleft_y])
        return AxisAlignedRectangle.from_topleft(
            topleft=topleft, width=width, height=height
        )

    def enclosing_oriented_bbox(self) -> Rectangle:
        """Compute the smallest area enclosing Oriented Bounding Box (OBB)
        See: https://docs.opencv.org/3.4/dd/d49/tutorial_py_contour_features.html

        Returns:
            Rectangle: Rectangle object
        """
        rect = cv2.minAreaRect(self.polyaprox.asarray.astype(np.float32))
        bbox = cv2.boxPoints(rect)
        return Rectangle(bbox)

    def enclosing_convex_hull(self) -> Polygon:
        """Compute the smallest area enclosing Convex Hull
        See: https://docs.opencv.org/3.4/dd/d49/tutorial_py_contour_features.html

        Returns:
            Polygon: Polygon object
        """

        convexhull = np.squeeze(cv2.convexHull(self.polyaprox.asarray))
        return Polygon(convexhull)
