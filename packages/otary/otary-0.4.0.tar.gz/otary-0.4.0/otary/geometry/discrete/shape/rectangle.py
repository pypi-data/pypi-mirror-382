"""
Rectangle class.
It will be particularly useful for the AITT project for describing bounding boxes.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from otary.geometry import Polygon, Vector

if TYPE_CHECKING:  # pragma: no cover
    from typing_extensions import Self
else:  # pragma: no cover
    try:
        from typing import Self
    except ImportError:  # make Self available in Python <= 3.10
        from typing_extensions import Self


class Rectangle(Polygon):
    """Rectangle class to manipulate rectangle object"""

    def __init__(
        self,
        points: NDArray | list,
        is_cast_int: bool = False,
        regularity_margin_error: float = 1e-2,
        desintersect: bool = True,
    ) -> None:
        """Create a Rectangle object.

        Args:
            points (NDArray | list): 2D points that define the rectangle
            is_cast_int (bool, optional): cast points to int. Defaults to False.
            regularity_margin_error (float, optional): defines the allowed margin
                distance error when checking if the points form a rectangle or not
                on initialization.
            desintersect (bool, optional): whether to desintersect the rectangle or not.
                Can be useful if the input points are in a random order and
                self-intersection is possible. In any case, if you try to instantiate
                a self-intersected rectangle a ValueError will be raised.
                Defaults to True.
        """
        if len(points) != 4:
            raise ValueError("Cannot create a Rectangle since it must have 4 points")
        super().__init__(points=points, is_cast_int=is_cast_int)

        if desintersect:
            self.desintersect()

        if self.is_self_intersected:
            raise ValueError(
                "The points form a self-intersected geometric object which is not "
                f"allowed for a {self.__class__.__name__}"
            )

        if not self.is_regular(margin_dist_error_pct=regularity_margin_error):
            raise ValueError(
                "Try to create a Rectangle object but the coordinates "
                "do not form a valid Rectangle. Please check your input coordinates, "
                "the regularity_margin_error and the desintersect parameters."
            )

    @classmethod
    def unit(cls) -> Rectangle:
        """Create a unit Rectangle object

        Returns:
            Rectangle: new Rectangle object
        """
        return cls(points=[[0, 0], [0, 1], [1, 1], [1, 0]])

    @classmethod
    def from_center(
        cls,
        center: NDArray,
        width: float,
        height: float,
        is_cast_int: bool = False,
    ) -> Rectangle:
        """Create a Rectangle object using the center point, width, height.

        Convention to create the rectangle is:
            index 0: top left point
            index 1: top right point
            index 2: bottom right point
            index 3: bottom left point

        Args:
            center (NDArray): center point of the rectangle
            width (float): width of the rectangle
            height (float): height of the rectangle
            is_cast_int (bool, optional): cast the points coordinates to int

        Returns:
            Rectangle: Rectangle object
        """
        # compute the halves lengths
        half_width = width / 2
        half_height = height / 2

        # get center coordinates
        center_x, center_y = center[0], center[1]

        # get the rectangle coordinates
        points = np.array(
            [
                [center_x - half_width, center_y - half_height],
                [center_x + half_width, center_y - half_height],
                [center_x + half_width, center_y + half_height],
                [center_x - half_width, center_y + half_height],
            ]
        )

        return Rectangle(points=points, is_cast_int=is_cast_int)

    @classmethod
    def from_topleft_bottomright(
        cls,
        topleft: NDArray,
        bottomright: NDArray,
        is_cast_int: bool = False,
    ) -> Self:
        """Create a Rectangle object using the top left and bottom right points.

        Convention to create the rectangle is:
            index 0: top left point
            index 1: top right point
            index 2: bottom right point
            index 3: bottom left point

        Args:
            topleft (NDArray): top left point of the rectangle
            bottomright (NDArray): bottom right point of the rectangle

        Returns:
            Rectangle: new Rectangle object
        """
        topright_vertice = np.array([bottomright[0], topleft[1]])
        bottomleft_vertice = np.array([topleft[0], bottomright[1]])
        return cls(
            np.asarray([topleft, topright_vertice, bottomright, bottomleft_vertice]),
            is_cast_int=is_cast_int,
        )

    @classmethod
    def from_topleft(
        cls,
        topleft: NDArray,
        width: float,
        height: float,
        is_cast_int: bool = False,
    ) -> Self:
        """Create a Rectangle object using the top left point, width, height and angle.

        Convention to create the rectangle is:
            index 0: top left point
            index 1: top right point
            index 2: bottom right point
            index 3: bottom left point

        Args:
            topleft (NDArray): top left point of the rectangle
            width (float): width of the rectangle
            height (float): height of the rectangle
            is_cast_int (bool, optional): whether to cast int or not. Defaults to False.

        Returns:
            Rectangle: Rectangle object
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        bottomright_vertice = np.array([topleft[0] + width, topleft[1] + height])
        return cls.from_topleft_bottomright(
            topleft=topleft,
            bottomright=bottomright_vertice,
            is_cast_int=is_cast_int,
        )

    @property
    def is_square(self) -> bool:
        """Whether the rectangle is a square or not

        Returns:
            bool: True if the Rectangle is a Square
        """
        if self.shortside_length == self.longside_length:
            return True

        return False

    def is_axis_aligned_approx(self, precision: int = 3) -> bool:
        """Check if the rectangle is axis-aligned

        Args:
            precision (int, optional): precision for the slope angle.
                This define the number of decimals to consider for the angle
                calculation of both the longside and shortside angle. Defaults to 3.

        Returns:
            bool: True if the rectangle is axis-aligned, False otherwise
        """

        def is_mult_of_90_approx(x, precision: int) -> bool:
            return bool(round((x + 90 * 100), precision) % 90 == 0)

        longside_cond = is_mult_of_90_approx(
            self.longside_slope_angle(degree=True), precision=precision
        )
        shortside_cond = is_mult_of_90_approx(
            self.shortside_slope_angle(degree=True), precision=precision
        )
        return longside_cond and shortside_cond

    @property
    def is_axis_aligned(self) -> bool:
        """Check if the rectangle is exactly axis-aligned.
        If you wish to check if a rectangle is only approximately axis-aligned,
        use the `is_axis_aligned_approx` method.

        Returns:
            bool: True if the rectangle is exactly axis-aligned, False otherwise
        """
        if self.points[0][1] != self.points[1][1]:  # top left y == top right y
            return False
        if self.points[1][0] != self.points[2][0]:  # top right x == bottom right x
            return False
        if self.points[2][1] != self.points[3][1]:  # bottom right y == bottom left y
            return False
        if self.points[3][0] != self.points[0][0]:  # bottom left x == top left x
            return False
        return True

    @property
    def longside_length(self) -> float:
        """Compute the biggest side of the rectangle

        Returns:
            float: the biggest side length
        """
        seg1 = self.segments[0]
        seg2 = self.segments[1]
        return seg1.length if seg1.length > seg2.length else seg2.length

    @property
    def shortside_length(self) -> float:
        """Compute the smallest side of the rectangle

        Returns:
            Segment: Longest side of the Rectangle as a Segment object
        """
        seg1 = self.segments[0]
        seg2 = self.segments[1]
        return seg2.length if seg1.length > seg2.length else seg1.length

    def longside_slope_angle(
        self, degree: bool = False, is_y_axis_down: bool = False
    ) -> float:
        """Compute the biggest slope of the rectangle

        Returns:
            float: the biggest slope
        """
        seg1 = self.segments[0]
        seg2 = self.segments[1]
        seg_bigside = seg1 if seg1.length > seg2.length else seg2
        return seg_bigside.slope_angle(degree=degree, is_y_axis_down=is_y_axis_down)

    def shortside_slope_angle(
        self, degree: bool = False, is_y_axis_down: bool = False
    ) -> float:
        """Compute the smallest slope of the rectangle

        Returns:
            float: the smallest slope
        """
        seg1 = self.segments[0]
        seg2 = self.segments[1]
        seg_smallside = seg2 if seg1.length > seg2.length else seg1
        return seg_smallside.slope_angle(degree=degree, is_y_axis_down=is_y_axis_down)

    def desintersect(self) -> Self:
        """Desintersect the rectangle if it is self-intersected.
        If the rectangle is not self-intersected, returns the same rectangle.

        Returns:
            Rectangle: the desintersected Rectangle object
        """
        if not self.is_self_intersected:
            return self

        # Sort points based on angle from centroid
        def angle_from_center(pt):
            return np.arctan2(pt[1] - self.centroid[1], pt[0] - self.centroid[0])

        sorted_vertices = sorted(self.asarray, key=angle_from_center)
        self.asarray = np.array(sorted_vertices)
        return self

    def join(
        self, rect: Rectangle, margin_dist_error: float = 1e-5
    ) -> Optional[Rectangle]:
        """Join two rectangles into a single one.
        If they share no point in common or only a single point returns None.
        If they share two points, returns a new Rectangle that is the concatenation
        of the two rectangles and that is not self-intersected.
        If they share 3 or more points they represent the same rectangle, thus
        returns this object.

        Args:
            rect (Rectangle): the other Rectangle object
            margin_dist_error (float, optional): the threshold to consider whether the
                rectangle share a common point. Defaults to 1e-5.

        Returns:
            Rectangle: the join new Rectangle object
        """
        shared_points = self.find_shared_approx_vertices(rect, margin_dist_error)
        n_shared_points = len(shared_points)

        if n_shared_points in (0, 1):
            return None
        if n_shared_points == 2:
            new_rect_points = np.concatenate(
                (
                    self.find_vertices_far_from(shared_points, margin_dist_error),
                    rect.find_vertices_far_from(shared_points, margin_dist_error),
                ),
                axis=0,
            )
            return Rectangle(points=new_rect_points).desintersect()
        # if 3 or more points in common it is the same rectangle
        return self

    def _topright_vertice_from_topleft(self, topleft_index: int) -> NDArray:
        """Get the top-right vertice from the topleft vertice

        Args:
            topleft_index (int): index of the topleft vertice

        Returns:
            NDArray: topright vertice
        """
        if self.is_clockwise(is_y_axis_down=True):
            return self.asarray[(topleft_index + 1) % len(self)]
        return self.asarray[topleft_index - 1]

    def _bottomleft_vertice_from_topleft(self, topleft_index: int) -> NDArray:
        """Get the bottom-left vertice from the topleft vertice

        Args:
            topleft_index (int): index of the topleft vertice

        Returns:
            NDArray: topright vertice
        """
        if self.is_clockwise(is_y_axis_down=True):
            return self.asarray[topleft_index - 1]
        return self.asarray[(topleft_index + 1) % len(self)]

    def _bottomright_vertice_from_topleft(self, topleft_index: int) -> NDArray:
        """Get the bottom-right vertice from the topleft vertice

        Args:
            topleft_index (int): index of the topleft vertice

        Returns:
            NDArray: topright vertice
        """
        return self.asarray[(topleft_index + 2) % len(self)]

    def get_vertice_from_topleft(
        self, topleft_index: int, vertice: str = "topright"
    ) -> NDArray:
        """Get vertice from the topleft vertice. You can use this method to
        obtain the topright, bottomleft, bottomright vertice from the topleft vertice.

        Returns:
            NDArray: topright vertice
        """
        if vertice not in ("topright", "bottomleft", "bottomright"):
            raise ValueError(
                "Parameter vertice must be one of"
                "'topright', 'bottomleft', 'bottomright'"
                f"but got {vertice}"
            )
        return getattr(self, f"_{vertice}_vertice_from_topleft")(topleft_index)

    def get_width_from_topleft(self, topleft_index: int) -> float:
        """Get the width from the topleft vertice

        Args:
            topleft_index (int): top-left vertice index

        Returns:
            float: width value
        """
        return float(
            np.linalg.norm(
                self.asarray[topleft_index]
                - self.get_vertice_from_topleft(topleft_index, "topright")
            )
        )

    def get_height_from_topleft(self, topleft_index: int) -> float:
        """Get the heigth from the topleft vertice

        Args:
            topleft_index (int): top-left vertice index

        Returns:
            float: height value
        """
        return float(
            np.linalg.norm(
                self.asarray[topleft_index]
                - self.get_vertice_from_topleft(topleft_index, "bottomleft")
            )
        )

    def get_vector_up_from_topleft(self, topleft_index: int) -> Vector:
        """Get the vector that goes from the bottomleft vertice to the topleft vertice

        Args:
            topleft_index (int): top-left vertice index

        Returns:
            Vector: Vector object descripting the vector
        """
        bottomleft_vertice = self.get_vertice_from_topleft(
            topleft_index=topleft_index, vertice="bottomleft"
        )
        return Vector([bottomleft_vertice, self[topleft_index]])

    def get_vector_left_from_topleft(self, topleft_index: int) -> Vector:
        """Get the vector that goes from the topleft vertice to the topright vertice

        Args:
            topleft_index (int): top-left vertice index

        Returns:
            Vector: Vector object descripting the vector
        """
        rect_topright_vertice = self.get_vertice_from_topleft(
            topleft_index=topleft_index, vertice="topright"
        )
        return Vector([self[topleft_index], rect_topright_vertice])

    def __str__(self) -> str:
        return (  # pylint: disable=duplicate-code
            self.__class__.__name__
            + "(["
            + self.asarray[0].tolist().__str__()
            + ", "
            + self.asarray[1].tolist().__str__()
            + ", "
            + self.asarray[2].tolist().__str__()
            + ", "
            + self.asarray[3].tolist().__str__()
            + "])"
        )

    def __repr__(self) -> str:
        return str(self)
