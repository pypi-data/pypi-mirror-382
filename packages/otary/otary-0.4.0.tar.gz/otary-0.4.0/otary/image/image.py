"""
Image module for image processing.

The architecture design of this class follow the composition design pattern rather
than inheritance. This is because the Image has got a "has-a" relationship with
the other classes not a "is-a" relationship.
"""

# BEWARE this pylint error is disabled because the Image class is the most
# important class in the module and gathers all the methods from all the components.
# pylint: disable=too-many-lines

from __future__ import annotations

import io
from typing import Any, Optional, Literal, Sequence, TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray
import cv2
import PIL.Image as ImagePIL

import otary.geometry as geo
from otary.geometry.discrete.linear.entity import LinearEntity
from otary.geometry.discrete.shape.axis_aligned_rectangle import AxisAlignedRectangle
from otary.utils.cv.ocrsingleoutput import OcrSingleOutput
from otary.image.base import BaseImage
from otary.image.components import (
    ReaderImage,
    WriterImage,
    DrawerImage,
    TransformerImage,
)
from otary.image.components.transformer.components.binarizer.binarizer import (
    BinarizationMethods,
)
from otary.image.components.transformer.components.morphologyzer.morphologyzer import (
    BlurMethods,
)
from otary.image.components.drawer import (
    PointsRender,
    CirclesRender,
    EllipsesRender,
    SegmentsRender,
    LinearSplinesRender,
    PolygonsRender,
    OcrSingleOutputRender,
)

if TYPE_CHECKING:  # pragma: no cover
    from typing_extensions import Self
else:  # pragma: no cover
    try:
        from typing import Self
    except ImportError:  # make Self available in Python <= 3.10
        from typing_extensions import Self

ScoreDistanceFromCenterMethods = Literal["linear", "gaussian"]


class Image:
    """
    Image core class. It groups all the methods available from composition
    from all the image classes.
    """

    # pylint: disable=too-many-public-methods

    reader = ReaderImage()

    def __init__(self, image: NDArray) -> None:
        self.base = BaseImage(image=image, parent=self)
        self.drawer = DrawerImage(base=self.base)
        self.writer = WriterImage(base=self.base)
        self.transformer = TransformerImage(base=self.base)

    # -------------------------------- CLASS METHODS ----------------------------------

    @classmethod
    def from_fillvalue(cls, value: int = 255, shape: tuple = (128, 128, 3)) -> Image:
        """Class method to create an image from a single value

        Args:
            value (int, optional): value in [0, 255]. Defaults to 255.
            shape (tuple, optional): image shape. If it has three elements then
                the last one must be a 3 for a coloscale image.
                Defaults to (128, 128, 3).

        Returns:
            Image: array with a single value
        """
        return cls(image=cls.reader.from_fillvalue(value=value, shape=shape))

    @classmethod
    def from_file(
        cls, filepath: str, as_grayscale: bool = False, resolution: Optional[int] = None
    ) -> Image:
        """Create a Image array from a file image path

        Args:
            filepath (str): path to the image file
            as_grayscale (bool, optional): turn the image in grayscale.
                Defaults to False.
            resolution (Optional[int], optional): resolution of the image.

        Returns:
            Image: Image object with a single value
        """
        return cls(
            cls.reader.from_file(
                filepath=filepath, as_grayscale=as_grayscale, resolution=resolution
            )
        )

    @classmethod
    def from_pdf(
        cls,
        filepath: str,
        as_grayscale: bool = False,
        page_nb: int = 0,
        resolution: Optional[int] = None,
        clip_pct: Optional[AxisAlignedRectangle] = None,
    ) -> Image:
        """Create an Image array from a pdf file.

        Args:
            filepath (str): path to the pdf file
            as_grayscale (bool, optional): turn the image in grayscale.
                Defaults to False.
            page_nb (int, optional): page number to extract. Defaults to 0.
            resolution (Optional[int], optional): resolution of the image.
            clip_pct (Optional[AxisAlignedRectangle], optional): clip percentage of the
                image to only load a small part of the image (crop) for faster loading
                and less memory usage. Defaults to None.

        Returns:
            Image: Image object from pdf
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        return cls(
            cls.reader.from_pdf(
                filepath=filepath,
                as_grayscale=as_grayscale,
                page_nb=page_nb,
                resolution=resolution,
                clip_pct=clip_pct,
            )
        )

    # ---------------------------------- PROPERTIES -----------------------------------

    @property
    def asarray(self) -> NDArray:
        """Array representation of the image"""
        return self.base.asarray

    @asarray.setter
    def asarray(self, value: NDArray) -> None:
        """Setter for the asarray property

        Args:
            value (NDArray): value of the asarray to be changed
        """
        self.base.asarray = value

    @property
    def asarray_binary(self) -> NDArray:
        """Returns the representation of the image as a array with value not in
        [0, 255] but in [0, 1].

        Returns:
            NDArray: an array with value in [0, 1]
        """
        return self.base.asarray_binary

    @property
    def width(self) -> int:
        """Width of the image.

        Returns:
            int: image width
        """
        return self.base.width

    @property
    def height(self) -> int:
        """Height of the image

        Returns:
            int: image height
        """
        return self.base.height

    @property
    def channels(self) -> int:
        """Number of channels in the image

        Returns:
            int: number of channels
        """
        return self.base.channels

    @property
    def center(self) -> NDArray[np.int16]:
        """Center point of the image.

        Please note that it is returned as type int because the center is
        represented as a X-Y coords of a pixel.

        Returns:
            NDArray: center point of the image
        """
        return self.base.center

    @property
    def area(self) -> int:
        """Area of the image

        Returns:
            int: image area
        """
        return self.base.area

    @property
    def shape_array(self) -> tuple[int, int, int]:
        """Returns the array shape value (height, width, channel)

        Returns:
            tuple[int]: image shape
        """
        return self.base.shape_array

    @property
    def shape_xy(self) -> tuple[int, int, int]:
        """Returns the array shape value (width, height, channel)

        Returns:
            tuple[int]: image shape
        """
        return self.base.shape_xy

    @property
    def is_gray(self) -> bool:
        """Whether the image is a grayscale image or not

        Returns:
            bool: True if image is in grayscale, 0 otherwise
        """
        return self.base.is_gray

    @property
    def norm_side_length(self) -> int:
        """Returns the normalized side length of the image.
        This is the side length if the image had the same area but
        the shape of a square (four sides of the same length).

        Returns:
            int: normalized side length
        """
        return self.base.norm_side_length

    @property
    def corners(self) -> NDArray:
        """Returns the corners in clockwise order:

        0. top left corner
        1. top right corner
        2. bottom right corner
        3. bottom left corner

        Returns:
            NDArray: array containing the corners
        """
        return self.base.corners

    # ---------------------------------- BASE METHODS ---------------------------------

    def as_grayscale(self) -> Self:
        """Generate the image in grayscale of shape (height, width)

        Returns:
            Self: original image in grayscale
        """
        self.base.as_grayscale()
        return self

    def as_colorscale(self) -> Self:
        """Generate the image in colorscale (height, width, 3).
        This property can be useful when we wish to draw objects in a given color
        on a grayscale image.

        Returns:
            Self: original image in color
        """
        self.base.as_colorscale()
        return self

    def as_reversed_color_channel(self) -> Self:
        """Generate the image with the color channels reversed.
        This is useful when we want to convert an image from BGR to RGB or vice versa.

        Returns:
            Self: original image with reversed color channels
        """
        self.base.as_reversed_color_channel()
        return self

    def as_filled(self, fill_value: int | NDArray = 255) -> Self:
        """Returns an entirely white image of the same size as the original.
        Can be useful to get an empty representation of the same image to paint
        and draw things on an image of the same dimension.

        Args:
            fill_value (int | NDArray, optional): color to fill the new empty image.
                Defaults to 255 which means that is returns a entirely white image.

        Returns:
            Self: new image with a single color of the same size as original.
        """
        self.base.as_filled(fill_value=fill_value)
        return self

    def as_white(self) -> Self:
        """Returns an entirely white image with the same dimension as the original.

        Returns:
            Self: new white image
        """
        self.base.as_white()
        return self

    def as_black(self) -> Self:
        """Returns an entirely black image with the same dimension as the original.

        Returns:
            Self: new black image
        """
        self.base.as_black()
        return self

    def as_pil(self) -> ImagePIL.Image:
        """Return the image as PIL Image

        Returns:
            ImagePIL: PIL Image
        """
        return self.base.as_pil()

    def as_api_file_input(
        self, fmt: str = "png", filename: str = "image"
    ) -> dict[str, tuple[str, bytes, str]]:
        """Return the image as a file input for API requests.

        Args:
            fmt (str, optional): format of the image. Defaults to "png".
            filename (str, optional): name of the file without the format.
                Defaults to "image".

        Returns:
            dict[str, tuple[str, bytes, str]]: dictionary with file input
                for API requests, where the key is "file" and the value is a tuple
                containing the filename, image bytes, and content type.
        """
        return self.base.as_api_file_input(fmt=fmt, filename=filename)

    def rev(self) -> Self:
        """Reverse the image colors. Each pixel color value V becomes |V - 255|.

        Applied on a grayscale image the black pixel becomes white and the
        white pixels become black.
        """
        self.base.rev()
        return self

    def dist_pct(self, pct: float) -> float:
        """Distance percentage that can be used an acceptable distance error margin.
        It is calculated based on the normalized side length.

        Args:
            pct (float, optional): percentage of distance error. Defaults to 0.01,
                which means 1% of the normalized side length as the
                default margin distance error.

        Returns:
            float: margin distance error
        """
        return self.base.dist_pct(pct=pct)

    def is_equal_shape(self, other: Image, consider_channel: bool = True) -> bool:
        """Check whether two images have the same shape

        Args:
            other (BaseImage): BaseImage object

        Returns:
            bool: True if the objects have the same shape, False otherwise
        """
        return self.base.is_equal_shape(
            other=other.base, consider_channel=consider_channel
        )

    # ---------------------------------- COPY METHOD ----------------------------------

    def copy(self) -> Image:
        """Copy of the image.

        For NumPy arrays containing basic data types (e.g., int, float, bool),
        using copy.deepcopy() is generally unnecessary.
        The numpy.copy() method achieves the same result more efficiently.
        numpy.copy() creates a new array in memory with a separate copy of the data,
        ensuring that modifications to the copy do not affect the original array.

        Returns:
            Image: image copy
        """
        return Image(image=self.asarray.copy())

    # -------------------------------- WRITE METHODS ----------------------------------

    def save(self, fp: str) -> None:
        """Save the image in a local file

        Args:
            fp (str): fp stands for filepath which is the path to the file
        """
        self.writer.save(fp=fp)

    def show(
        self,
        figsize: tuple[float, float] = (-1, -1),
        popup_window_display: bool = False,
    ) -> ImagePIL.Image:
        """Show the image

        Args:
            figsize (tuple[float, float], optional): size of the figure.
                Defaults to (-1, -1), meaning the original size of the image.
            popup_window_display (bool, optional): whether to display the image in a
                popup window. Defaults to False.
        """
        return self.writer.show(
            figsize=figsize, popup_window_display=popup_window_display
        )

    # -------------------------------- DRAWER METHODS ---------------------------------

    def draw_circles(
        self, circles: Sequence[geo.Circle], render: CirclesRender = CirclesRender()
    ) -> Self:
        """Draw circles in the image

        Args:
            circles (list[Circle]): list of Circle geometry objects.
            render (CirclesRender): circle renderer

        Returns:
            Image: new image with circles drawn
        """
        self.drawer.draw_circles(circles=circles, render=render)
        return self

    def draw_ellipses(
        self, ellipses: Sequence[geo.Ellipse], render: EllipsesRender = EllipsesRender()
    ) -> Self:
        """Draw ellipses in the image

        Args:
            ellipses (list[Ellipse]): list of Ellipse geometry objects.
            render (EllipsesRender): ellipse renderer

        Returns:
            Image: new image with ellipses drawn
        """
        self.drawer.draw_ellipses(ellipses=ellipses, render=render)
        return self

    def draw_points(
        self,
        points: list | NDArray | Sequence[geo.Point],
        render: PointsRender = PointsRender(),
    ) -> Self:
        """Draw points in the image

        Args:
            points (NDArray): list of points. It must be of shape (n, 2). This
                means n points of shape 2 (x and y coordinates).
            render (PointsRender): point renderer

        Returns:
            Image: new image with points drawn
        """
        self.drawer.draw_points(points=points, render=render)
        return self

    def draw_segments(
        self,
        segments: NDArray | Sequence[geo.Segment],
        render: SegmentsRender = SegmentsRender(),
    ) -> Self:
        """Draw segments in the image. It can be arrowed segments (vectors) too.

        Args:
            segments (NDArray): list of segments. Can be a numpy array of shape
                (n, 2, 2) which means n array of shape (2, 2) that define a segment
                by two 2D points.
            render (SegmentsRender): segment renderer

        Returns:
            Image: new image with segments drawn
        """
        self.drawer.draw_segments(segments=segments, render=render)
        return self

    def draw_polygons(
        self,
        polygons: Sequence[geo.Polygon],
        render: PolygonsRender = PolygonsRender(),
    ) -> Self:
        """Draw polygons in the image

        Args:
            polygons (Sequence[Polygon]): list of Polygon objects
            render (PolygonsRender): PolygonRender object

        Returns:
            Image: new image with polygons drawn
        """
        self.drawer.draw_polygons(polygons=polygons, render=render)
        return self

    def draw_splines(
        self,
        splines: Sequence[geo.LinearSpline],
        render: LinearSplinesRender = LinearSplinesRender(),
    ) -> Self:
        """Draw linear splines in the image.

        Args:
            splines (Sequence[geo.LinearSpline]): linear splines to draw.
            render (LinearSplinesRender, optional): linear splines render.
                Defaults to LinearSplinesRender().

        Returns:
            Image: new image with splines drawn
        """
        self.drawer.draw_splines(splines=splines, render=render)
        return self

    def draw_ocr_outputs(
        self,
        ocr_outputs: Sequence[OcrSingleOutput],
        render: OcrSingleOutputRender = OcrSingleOutputRender(),
    ) -> Self:
        """Return the image with the bounding boxes displayed from a list of OCR
        single output. It allows you to show bounding boxes that can have an angle,
        not necessarily vertical or horizontal.

        Args:
            ocr_outputs (list[OcrSingleOutput]): list of OcrSingleOutput objects
            render (OcrSingleOutputRender): OcrSingleOutputRender object

        Returns:
            Image: new image with ocr outputs drawn
        """
        self.drawer.draw_ocr_outputs(ocr_outputs=ocr_outputs, render=render)
        return self

    # --------------------------------- BINARIZER -------------------------------------

    def threshold_simple(self, thresh: int) -> Self:
        """Compute the image thesholded by a single value T.
        All pixels with value v <= T are turned black and those with value v > T are
        turned white. This is a global thresholding method.

        Args:
            thresh (int): value to separate the black from the white pixels.

        Returns:
            (Self): output thresholded image
        """
        self.transformer.binarizer.threshold_simple(thresh=thresh)
        return self

    def threshold_otsu(self) -> Self:
        """Apply Otsu global thresholding.
        This is a global thresholding method that automatically determines
        an optimal threshold value from the image histogram.

        Paper (1979):
        https://ieeexplore.ieee.org/document/4310076

        Consider applying a gaussian blur before for better thresholding results.
        See why in https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html.

        As the input image must be a grayscale before applying any thresholding
        methods we convert the image to grayscale.

        Returns:
            (Self): output thresholded image
        """
        self.transformer.binarizer.threshold_otsu()
        return self

    def threshold_adaptive(self, block_size: int = 11, constant: float = 2.0) -> Self:
        """Apply adaptive local thresholding.
        This is a local thresholding method that computes the threshold for a pixel
        based on a small region around it.

        A gaussian blur is applied before for better thresholding results.
        See why in https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html.

        As the input image must be a grayscale before applying any thresholding
        methods we convert the image to grayscale.

        Args:
            block_size (int, optional): Size of a pixel neighborhood that is used to
                calculate a threshold value for the pixel: 3, 5, 7, and so on.
                Defaults to 11.
            constant (int, optional): Constant subtracted from the mean or weighted
                mean. Normally, it is positive but may be zero or negative as well.
                Defaults to 2.

        Returns:
            (Self): output thresholded image
        """
        self.transformer.binarizer.threshold_adaptive(
            block_size=block_size, constant=constant
        )
        return self

    def threshold_sauvola(
        self, window_size: int = 15, k: float = 0.5, r: float = 128.0
    ) -> Self:
        """Apply Sauvola local thresholding.
         This is a local thresholding method that computes the threshold for a pixel
         based on a small region around it.

         Paper (1997):
         https://www.researchgate.net/publication/3710586

         See https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_niblack_sauvola.html # pylint: disable=line-too-long

         As the input image must be a grayscale before applying any thresholding
         methods we convert the image to grayscale.

         Args:
             window_size (int, optional): sauvola window size to apply on the
                 image. Defaults to 15.
             k (float, optional): sauvola k factor to apply to regulate the impact
                 of the std. Defaults to 0.5.
             r (float, optional): sauvola r value. Defaults to 128.

        Returns:
             (Self): output thresholded image
        """
        self.transformer.binarizer.threshold_sauvola(window_size=window_size, k=k, r=r)
        return self

    def threshold_bradley(self, window_size: int = 15, t: float = 0.15) -> Self:
        """Implementation of the Bradley & Roth thresholding method.

        Paper (2007):
        https://www.researchgate.net/publication/220494200_Adaptive_Thresholding_using_the_Integral_Image

        Args:
            window_size (int, optional): window size for local computations.
                Defaults to 15.
            t (float, optional): t value in [0, 1]. Defaults to 0.15.

        Returns:
            NDArray[np.uint8]: output thresholded image
        """
        self.transformer.binarizer.threshold_bradley(window_size=window_size, t=t)
        return self

    def binary(self, method: BinarizationMethods = "sauvola") -> NDArray:
        """Binary representation of the image with values that can be only 0 or 1.
        The value 0 is now 0 and value of 255 are now 1. Black is 0 and white is 1.
        We can also talk about the mask of the image to refer to the binary
        representation of it.

        The sauvola is generally the best binarization method however it is
        way slower than the others methods. The adaptative or otsu method are the best
        method in terms of speed and quality.

        Args:
            method (str, optional): the binarization method to apply.
                Must be in ["adaptative", "otsu", "sauvola", "niblack", "nick", "wolf"].
                Defaults to "sauvola".

        Returns:
            NDArray: array where its inner values are 0 or 1
        """
        return self.transformer.binarizer.binary(method=method)

    def binaryrev(self, method: BinarizationMethods = "sauvola") -> NDArray:
        """Reversed binary representation of the image.
        The value 0 is now 1 and value of 255 are now 0. Black is 1 and white is 0.
        This is why it is called the "binary rev" or "binary reversed".

        Args:
            method (str, optional): the binarization method to apply.
                Must be in ["adaptative", "otsu", "sauvola", "niblack", "nick", "wolf"].
                Defaults to "adaptative".

        Returns:
            NDArray: array where its inner values are 0 or 1
        """
        return self.transformer.binarizer.binaryrev(method=method)

    # ---------------------------------- CROPPER --------------------------------------
    # the copy arguments is special in the crop methods.
    # this is important for performance reasons
    # if you want to crop a small part of an image and conserve the original
    # without doing image.copy().crop() which would copy the entire original image!
    # this would be much more expensive if the image is large

    def crop(
        self, x0: int, y0: int, x1: int, y1: int, copy: bool = False, **kwargs
    ) -> Image | Self:
        """Crop the image in a straight axis-aligned rectangle way given
        by the top-left point [x0, y0] and the bottom-right point [x1, y1]

        This function inputs represents the top-left and bottom-right points.
        This method does not provide a way to extract a rotated rectangle or a
        different shape from the image.

        Remember that in this library the x coordinates represent the y coordinates of
        the image array (horizontal axis of the image).
        The array representation is always rows then columns.
        In this library this is the contrary like in opencv.

        Args:
            x0 (int): top-left x coordinate
            y0 (int): top-left y coordinate
            x1 (int): bottom-right x coordinate
            y1 (int): bottom-right y coordinate
            clip (bool, optional): whether to clip or not. Defaults to True.
            pad (bool, optional): whether to pad or not. Defaults to False.
            copy (bool, optional): whether to copy or not. Defaults to False.
            extra_border_size (int, optional): extra border size to add to the crop
                in the x and y directions. Defaults to 0 which means no extra border.
            pad_value (int, optional): pad fill value. Defaults to 0.

        Returns:
            Image | Self: new cropped image if copy=True else the current image cropped
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        out = self.transformer.cropper.crop(
            x0=x0, y0=y0, x1=x1, y1=y1, copy=copy, **kwargs
        )
        return out if out is not None else self

    def crop_from_topleft(
        self, topleft: NDArray, width: int, height: int, copy: bool = False, **kwargs
    ) -> Image | Self:
        """Crop the image from a rectangle defined by its top-left point, its width and
        its height.

        Args:
            topleft (NDArray): (x, y) coordinates of the top-left point
            width (int): width of the rectangle to crop
            height (int): height of the rectangle to crop
            clip (bool, optional): whether to clip or not. Defaults to True.
            pad (bool, optional): whether to pad or not. Defaults to False.
            copy (bool, optional): whether to copy or not. Defaults to False.
            extra_border_size (int, optional): extra border size to add to the crop
                in the x and y directions. Defaults to 0 which means no extra border.
            pad_value (int, optional): pad fill value. Defaults to 0.

        Returns:
            Image | Self: new cropped image if copy=True else the current image cropped
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        out = self.transformer.cropper.crop_from_topleft(
            topleft=topleft, width=width, height=height, copy=copy, **kwargs
        )
        return out if out is not None else self

    def crop_from_center(
        self, center: NDArray, width: int, height: int, copy: bool = False, **kwargs
    ) -> Image | Self:
        """Crop the image from a rectangle defined by its center point, its width and
        its height.

        Args:
            center (NDArray): (x, y) coordinates of the center point
            width (int): width of the rectangle to crop
            height (int): height of the rectangle to crop
            clip (bool, optional): whether to clip or not. Defaults to True.
            pad (bool, optional): whether to pad or not. Defaults to False.
            copy (bool, optional): whether to copy or not. Defaults to False.
            extra_border_size (int, optional): extra border size to add to the crop
                in the x and y directions. Defaults to 0 which means no extra border.
            pad_value (int, optional): pad fill value. Defaults to 0.

        Returns:
            Image | Self: new cropped image if copy=True else the current image cropped
        """
        out = self.transformer.cropper.crop_from_center(
            center=center, width=width, height=height, copy=copy, **kwargs
        )
        return out if out is not None and copy else self

    def crop_from_axis_aligned_bbox(
        self, bbox: geo.AxisAlignedRectangle, copy: bool = False, **kwargs
    ) -> Image | Self:
        """Crop the image from an Axis-Aligned Bounding Box (AABB).
        Inclusive crops which means that the cropped image will have
        width and height equal to the width and height of the AABB.

        Args:
            bbox (geo.AxisAlignedRectangle): axis-aligned rectangle bounding box
            clip (bool, optional): whether to clip or not. Defaults to True.
            pad (bool, optional): whether to pad or not. Defaults to False.
            copy (bool, optional): whether to copy or not. Defaults to False.
            extra_border_size (int, optional): extra border size to add to the crop
                in the x and y directions. Defaults to 0 which means no extra border.
            pad_value (int, optional): pad fill value. Defaults to 0.

        Returns:
            Image | Self: new cropped image if copy=True else the current image cropped
        """
        out = self.transformer.cropper.crop_from_axis_aligned_rectangle(
            bbox=bbox, copy=copy, **kwargs
        )
        return out if out is not None and copy else self

    def crop_hq_from_aabb_and_pdf(
        self,
        bbox: geo.AxisAlignedRectangle,
        pdf_filepath: str,
        page_nb: int = 0,
        as_grayscale: bool = False,
        resolution: int = 1000,
    ) -> Image:
        """Generate a new image from a pdf file by cropping a High Quality crop
        from a given Axis-Aligned Bounding Box (AABB).

        The crop is of high quality because we can load only the crop part of the image
        from the original pdf.

        Args:
            bbox (geo.AxisAlignedRectangle): crop bounding box
            pdf_filepath (str): PDF filepath
            page_nb (int, optional): page to load in the PDF. The first page is 0.
                Defaults to 0.
            as_grayscale (bool, optional): whether to load the image as grayscale or
                not. Defaults to False.
            resolution (int, optional): resolution of the final crop image.
                Defaults to 1000.

        Returns:
            Image: high quality crop image
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        # get the bbox normalized
        clip_pct = bbox.copy().normalize(x=self.width, y=self.height)

        # obtain the High Quality crop image by reading
        im_crop = Image.from_pdf(
            filepath=pdf_filepath,
            page_nb=page_nb,
            as_grayscale=as_grayscale,
            resolution=resolution,
            clip_pct=clip_pct,
        )
        return im_crop

    def crop_from_polygon(
        self, polygon: geo.Polygon, copy: bool = False, **kwargs
    ) -> Image | Self:
        """Crop from a polygon using its Axis-Aligned Bounding Box (AABB)

        Args:
            polygon (geo.Polygon): polygon object to crop in the image
            copy (bool, optional): whether to create a copy or not. Defaults to False.
            clip (bool, optional): whether to clip or not. Defaults to True.
            pad (bool, optional): whether to pad or not. Defaults to False.
            extra_border_size (int, optional): extra border size to add to the crop
                in the x and y directions. Defaults to 0 which means no extra border.
            pad_value (int, optional): pad fill value. Defaults to 0.

        Returns:
            Image | Self: new cropped image if copy=True else the current image cropped
        """
        out = self.transformer.cropper.crop_from_polygon(
            polygon=polygon, copy=copy, **kwargs
        )
        return out if out is not None and copy else self

    def crop_from_linear_spline(
        self, spline: geo.LinearSpline, copy: bool = False, **kwargs
    ) -> Image | Self:
        """Crop from a Linear Spline using its Axis-Aligned Bounding Box (AABB)

        Args:
            spline (geo.LinearSpline): linear spline object to crop in the image
            copy (bool, optional): whether to create a copy or not. Defaults to False.
                        clip (bool, optional): whether to clip or not. Defaults to True.
            pad (bool, optional): whether to pad or not. Defaults to False.
            extra_border_size (int, optional): extra border size to add to the crop
                in the x and y directions. Defaults to 0 which means no extra border.
            pad_value (int, optional): pad fill value. Defaults to 0.

        Returns:
            Image | Self: new cropped image if copy=True else the current image cropped
        """
        out = self.transformer.cropper.crop_from_linear_spline(
            spline=spline, copy=copy, **kwargs
        )
        return out if out is not None and copy else self

    def crop_segment(
        self,
        segment: NDArray,
        dim_crop_rect: tuple[int, int] = (-1, 100),
        added_width: int = 75,
    ) -> tuple[Image, NDArray, float, NDArray]:
        """Crop around a specific segment in the image. This is done in three
        specific steps:
        1) shift image so that the middle of the segment is in the middle of the image
        2) rotate image by the angle of segment so that the segment becomes horizontal
        3) crop the image

        Args:
            segment (NDArray): segment as numpy array of shape (2, 2).
            dim_crop_rect (tuple, optional): represents (width, height).
                Defaults to heigth of 100 and width of -1 which means
                that the width is automatically computed based on the length of
                the segment.
            added_width (int, optional): additional width for cropping.
                Half of the added_width is added to each side of the segment.
                Defaults to 75.

        Returns:
            tuple[Self, NDArray, float, NDArray]: returns in the following order:
                1) the cropped image
                2) the translation vector used to center the image
                3) the angle of rotation applied to the image
                4) the translation vector used to crop the image
        """
        width_crop_rect, height_crop_rect = dim_crop_rect
        im = self.copy()  # the copy before makes this method slow

        # center the image based on the middle of the line
        geo_segment = geo.Segment(segment)
        im, translation_vector = im.center_to_segment(segment=segment)

        if width_crop_rect == -1:
            # default the width for crop to be a bit more than line length
            width_crop_rect = int(geo_segment.length)
        width_crop_rect += added_width
        assert width_crop_rect > 0 and height_crop_rect > 0

        # rotate the image so that the line is horizontal
        angle = geo_segment.slope_angle(is_y_axis_down=True)
        im = im.rotate(angle=angle)

        # cropping
        im_crop = im.crop_from_center(
            center=im.base.center,
            width=width_crop_rect,
            height=height_crop_rect,
        )

        crop_translation_vector = self.base.center - im_crop.base.center
        return im_crop, translation_vector, angle, crop_translation_vector

    def crop_segment_faster(
        self,
        segment: NDArray,
        dim_crop_rect: tuple[int, int] = (-1, 100),
        added_width: int = 75,
        pad_value: int = 0,
    ) -> Image:
        """Crop around a specific segment in the image.
        This method is faster especially for large images.

        Here is a comparison of the total time taken for cropping with the two methods
        with a loop over 1000 iterations:

        | Image dimension | Crop v1 | Crop faster |
        |-----------------|---------|-------------|
        | 1224 x 946      | 2.0s    | 0.25s       |
        | 2448 x 1892     | 4.51s   | 0.25s       |
        | 4896 x 3784     | 23.2s   | 0.25s       |

        Args:
            segment (NDArray): segment as numpy array of shape (2, 2).
            dim_crop_rect (tuple, optional): represents (width, height).
                Defaults to heigth of 100 and width of -1 which means
                that the width is automatically computed based on the length of
                the segment.
            added_width (int, optional): additional width for cropping.
                Half of the added_width is added to each side of the segment.
                Defaults to 75.

        Returns:
            Self: cropped image around the segment
        """
        width_crop_rect, height_crop_rect = dim_crop_rect
        geo_segment = geo.Segment(segment)
        angle = geo_segment.slope_angle(is_y_axis_down=True)

        if width_crop_rect == -1:
            # default the width for crop to be a bit more than line length
            width_crop_rect = int(geo_segment.length)
        width_crop_rect += added_width
        assert width_crop_rect > 0 and height_crop_rect > 0

        x_extra = abs(added_width / 2 * np.cos(angle))
        y_extra = abs(added_width / 2 * np.sin(angle))

        # add extra width for crop in case segment is ~vertical
        x_extra += int(width_crop_rect / 2) + 1
        y_extra += int(height_crop_rect / 2) + 1

        im: Image = self.crop(
            x0=geo_segment.xmin - x_extra,
            y0=geo_segment.ymin - y_extra,
            x1=geo_segment.xmax + x_extra,
            y1=geo_segment.ymax + y_extra,
            pad=True,
            clip=False,
            copy=True,  # copy the image after cropping for very fast performance
            pad_value=pad_value,
        )

        # rotate the image so that the line is horizontal
        im.rotate(angle=angle)

        # cropping around segment center
        im.crop_from_center(
            center=im.base.center,
            width=width_crop_rect,
            height=height_crop_rect,
        )

        return im

    def crop_from_rectangle_referential(
        self,
        rect: geo.Rectangle,
        rect_topleft_ix: int = 0,
        crop_dim: tuple[float, float] = (-1, -1),
        crop_shift: tuple[float, float] = (0, 0),
    ) -> Image:
        """Crop image in the referential of the rectangle.

        Args:
            rect (geo.Rectangle): rectangle for reference to crop.
            rect_topleft_ix (int): top-left vertice index of the rectangle
            crop_dim (tuple[float, float], optional): (width, height) crop dimension.
                Defaults to (-1, -1).
            crop_shift (tuple[float, float], optional): The shift is (x, y).
                The crop_shift argument is applied from the rectangle center based on
                the axis referential of the rectangle.
                This means that the shift in the Y direction
                is based on the normalized vector (bottom-left, top-left)
                The shift in the X direction is based on the normalized vector
                (top-left, top-right). Defaults to (0, 0) meaning no shift.

        Returns:
            Self: new image cropped
        """
        # shift down and up vector calculated based on the top-left vertice
        rect_shift_up = rect.get_vector_up_from_topleft(topleft_index=rect_topleft_ix)
        rect_shift_left = rect.get_vector_left_from_topleft(
            topleft_index=rect_topleft_ix
        )

        # crop dimension
        rect_heigth = rect.get_height_from_topleft(topleft_index=rect_topleft_ix)
        crop_width = rect_heigth if crop_dim[0] == -1 else crop_dim[0]
        crop_height = rect_heigth if crop_dim[1] == -1 else crop_dim[1]
        crop_width, crop_height = int(crop_width), int(crop_height)
        assert crop_width > 0 and crop_height > 0

        # compute the crop center
        crop_center = rect.centroid
        crop_center += crop_shift[0] * rect_shift_left.normalized  # shift left
        crop_center += crop_shift[1] * rect_shift_up.normalized  # shift up

        # get the crop segment
        crop_segment = geo.Segment(
            [
                crop_center - crop_width / 2 * rect_shift_left.normalized,
                crop_center + crop_width / 2 * rect_shift_left.normalized,
            ]
        )

        return self.crop_segment_faster(
            segment=crop_segment.asarray,
            dim_crop_rect=(crop_width, crop_height),
            added_width=0,
        )

    def crop_rectangle(self, rect: geo.Rectangle, rect_topleft_ix: int = 0) -> Image:
        """Crop from a rectangle that can be rotated in any direction.
        The crop is done using the information of the top-left vertice index to
        determine the width and height of the crop.

        Args:
            rect (geo.Rectangle): rectangle to crop in the referential of the image
            rect_topleft_ix (int, optional): top-left vertice index. Defaults to 0.

        Returns:
            Image: crop of the image
        """
        crop_dim = (
            rect.get_width_from_topleft(rect_topleft_ix),
            rect.get_height_from_topleft(rect_topleft_ix),
        )
        return self.crop_from_rectangle_referential(
            rect=rect, rect_topleft_ix=rect_topleft_ix, crop_dim=crop_dim
        )

    # ------------------------------- GEOMETRY METHODS --------------------------------

    def shift(self, shift: NDArray, fill_value: Sequence[float] = (0.0,)) -> Self:
        """Shift the image by performing a translation operation

        Args:
            shift (NDArray): Vector for translation
            fill_value (int | tuple[int, int, int], optional): value to fill the
                border of the image after the rotation in case reshape is True.
                Can be a tuple of 3 integers for RGB image or a single integer for
                grayscale image. Defaults to (0.0,) which is black.

        Returns:
            Self: shifted image
        """
        self.transformer.geometrizer.shift(shift=shift, fill_value=fill_value)
        return self

    def rotate(
        self,
        angle: float,
        is_degree: bool = False,
        is_clockwise: bool = True,
        reshape: bool = True,
        fill_value: Sequence[float] = (0.0,),
    ) -> Self:
        """Rotate the image by a given angle.

        For the rotation with reshape, meaning preserving the whole image,
        we used the code from the imutils library:
        https://github.com/PyImageSearch/imutils/blob/master/imutils/convenience.py#L41

        Args:
            angle (float): angle to rotate the image
            is_degree (bool, optional): whether the angle is in degree or not.
                If not it is considered to be in radians.
                Defaults to False which means radians.
            is_clockwise (bool, optional): whether the rotation is clockwise or
                counter-clockwise. Defaults to True.
            reshape (bool, optional): whether to preserve the original image or not.
                If True, the complete image is preserved hence the width and height
                of the rotated image are different than in the original image.
                Defaults to True.
            fill_value (Sequence[float], optional): value to
                fill the border of the image after the rotation in case reshape is True.
                Can be a tuple of 3 integers for RGB image or a single integer for
                grayscale image. Defaults to (0.0,) which is black
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        self.transformer.geometrizer.rotate(
            angle=angle,
            is_degree=is_degree,
            is_clockwise=is_clockwise,
            reshape=reshape,
            fill_value=fill_value,
        )
        return self

    def center_to_point(self, point: NDArray) -> tuple[Self, NDArray]:
        """Shift the image so that the input point ends up in the middle of the
        new image

        Args:
            point (NDArray): point as (2,) shape numpy array

        Returns:
            (tuple[Self, NDArray]): Self, translation Vector
        """
        shift_vector = self.transformer.geometrizer.center_to_point(point=point)
        return self, shift_vector

    def center_to_segment(self, segment: NDArray) -> tuple[Self, NDArray]:
        """Shift the image so that the segment middle point ends up in the middle
        of the new image

        Args:
            segment (NDArray): segment as numpy array of shape (2, 2)

        Returns:
            (tuple[Self, NDArray]): Self, vector_shift
        """
        shift_vector = self.transformer.geometrizer.center_to_segment(segment=segment)
        return self, shift_vector

    def restrict_rect_in_frame(self, rectangle: geo.Rectangle) -> geo.Rectangle:
        """Create a new rectangle that is contained within the image borders.
        If the input rectangle is outside the image, the returned rectangle is a
        image frame-fitted rectangle that preserve the same shape.

        Args:
            rectangle (geo.Rectangle): input rectangle

        Returns:
            geo.Rectangle: new rectangle
        """
        return self.transformer.geometrizer.restrict_rect_in_frame(rectangle=rectangle)

    # ----------------------------- MORPHOLOGICAL METHODS -----------------------------

    def resize_fixed(
        self,
        dim: tuple[int, int],
        interpolation: int = cv2.INTER_AREA,
        copy: bool = False,
    ) -> Image | Self:
        """Resize the image using a fixed dimension well defined.
        This function can result in a distorted image if the ratio between
        width and height is different in the original and the new image.

        If the dim argument has a negative value in height or width, then
        a proportional ratio is applied based on the one of the two dimension given.

        Args:
            dim (tuple[int, int]): a tuple with two integers in the following order
                (width, height).
            interpolation (int, optional): resize interpolation.
                Defaults to cv2.INTER_AREA.
            copy (bool, optional): whether to return a new image or not.

        Returns:
            Image | Self: resized new image if copy=True else resized original image
        """
        out = self.transformer.morphologyzer.resize_fixed(
            dim=dim, interpolation=interpolation, copy=copy
        )
        return out if out is not None and copy else self

    def resize(
        self, factor: float, interpolation: int = cv2.INTER_AREA, copy: bool = False
    ) -> Image | Self:
        """Resize the image to a new size using a scaling factor value that
        will be applied to all dimensions (width and height).

        Applying this method can not result in a distorted image.

        Args:
            factor (float): factor in [0, 5] to resize the image.
                A value of 1 does not change the image.
                A value of 2 doubles the image size.
                A maximum value of 5 is set to avoid accidentally producing a gigantic
                image.
            interpolation (int, optional): resize interpolation.
                Defaults to cv2.INTER_AREA.
            copy (bool, optional): whether to return a new image or not.

        Returns:
            Image | Self: resized new image if copy=True else resized original image
        """
        out = self.transformer.morphologyzer.resize(
            factor=factor, interpolation=interpolation, copy=copy
        )
        return out if out is not None and copy else self

    def blur(
        self,
        kernel: tuple = (5, 5),
        iterations: int = 1,
        method: BlurMethods = "average",
        sigmax: float = 0,
    ) -> Self:
        """Blur the image

        Args:
            kernel (tuple, optional): blur kernel size. Defaults to (5, 5).
            iterations (int, optional): number of iterations. Defaults to 1.
            method (str, optional): blur method.
                Must be in ["average", "median", "gaussian", "bilateral"].
                Defaults to "average".
            sigmax (float, optional): sigmaX value for the gaussian blur.
                Defaults to 0.

        Returns:
            Self: blurred image
        """
        self.transformer.morphologyzer.blur(
            kernel=kernel, iterations=iterations, method=method, sigmax=sigmax
        )
        return self

    def dilate(
        self,
        kernel: tuple = (5, 5),
        iterations: int = 1,
        dilate_black_pixels: bool = True,
    ) -> Self:
        """Dilate the image by making the black pixels expand in the image.
        The dilatation can be parametrize thanks to the kernel and iterations
        arguments.

        Args:
            kernel (tuple, optional): kernel to dilate. Defaults to (5, 5).
            iterations (int, optional): number of dilatation iterations. Defaults to 1.
            dilate_black_pixels (bool, optional): whether to dilate black pixels or not

        Returns:
            Self: dilated image
        """
        self.transformer.morphologyzer.dilate(
            kernel=kernel,
            iterations=iterations,
            dilate_black_pixels=dilate_black_pixels,
        )
        return self

    def erode(
        self,
        kernel: tuple = (5, 5),
        iterations: int = 1,
        erode_black_pixels: bool = True,
    ) -> Self:
        """Erode the image by making the black pixels shrink in the image.
        The anti-dilatation can be parametrize thanks to the kernel and iterations
        arguments.

        Args:
            kernel (tuple, optional): kernel to erode. Defaults to (5, 5).
            iterations (int, optional): number of iterations. Defaults to 1.
            erode_black_pixels (bool, optional): whether to erode black pixels or not

        Returns:
            Self: eroded image
        """
        self.transformer.morphologyzer.erode(
            kernel=kernel, iterations=iterations, erode_black_pixels=erode_black_pixels
        )
        return self

    def add_border(self, size: int, fill_value: int = 0) -> Self:
        """Add a border to the image.

        Args:
            thickness (int): border thickness.
            color (int, optional): border color. Defaults to 0.
        """
        self.transformer.morphologyzer.add_border(size=size, fill_value=fill_value)
        return self

    def add_noise_salt_and_pepper(self, amount: float = 0.05) -> Self:
        """Add salt and pepper noise to the image.

        Args:
            amount (float, optional): Proportion of image pixels to alter.
                Defaults to 0.05.
        """
        self.transformer.morphologyzer.add_noise_salt_and_pepper(amount=amount)
        return self

    def add_noise_gaussian(self, mean: float = 0, std: float = 0.05) -> Self:
        """Add Gaussian noise to the image.

        Args:
            amount (float, optional): Proportion of image pixels to alter.
                Defaults to 0.05.
        """
        self.transformer.morphologyzer.add_noise_gaussian(mean=mean, std=std)
        return self

    # -------------------------- ASSEMBLED COMPOSED METHODS ---------------------------
    # methods that use multiple components
    # ---------------------------------------------------------------------------------

    def iou(
        self, other: Image, binarization_method: BinarizationMethods = "sauvola"
    ) -> float:
        """Compute the intersection over union score

        Args:
            other (Image): another image
            binarization_method (str, optional): binarization method to turn images
                into 0 and 1 images. The black pixels will be 1 and the white pixels
                will be 0. This is used to compute the score.
                Defaults to "sauvola".

        Returns:
            float: a score from 0 to 1. The greater the score the greater the other
                image is equal to the original image
        """
        assert self.is_equal_shape(other)
        mask0 = self.binaryrev(method=binarization_method)
        mask1 = other.binaryrev(method=binarization_method)
        return np.sum(mask0 * mask1) / np.count_nonzero(mask0 + mask1)

    def score_contains_v2(
        self, other: Image, binarization_method: BinarizationMethods = "sauvola"
    ) -> float:
        """Score contains version 2 which is more efficient and faster.

        Args:
            other (Image): other Image object
            binarization_method (str, optional): binarization method to turn images
                into 0 and 1 images. The black pixels will be 1 and the white pixels
                will be 0. This is used to compute the score.
                Defaults to "sauvola".

        Returns:
            float: a score from 0 to 1. The greater the score the greater the other
                image is contained within the original image
        """
        assert self.is_equal_shape(other, consider_channel=False)

        cur_binaryrev = self.binaryrev(method=binarization_method)
        other_binaryrev = other.binaryrev(method=binarization_method)

        other_pixels = cur_binaryrev[other_binaryrev == 1]

        coverage = np.sum(other_pixels) / np.sum(other_binaryrev)
        return coverage

    def score_contains(
        self, other: Image, binarization_method: BinarizationMethods = "sauvola"
    ) -> float:
        """How much the other image is contained in the original image.

        Args:
            other (Image): other Image object
            binarization_method (str, optional): binarization method to turn images
                into 0 and 1 images. The black pixels will be 1 and the white pixels
                will be 0. This is used to compute the score.
                Defaults to "sauvola".

        Returns:
            float: a score from 0 to 1. The greater the score the greater the other
                image is contained within the original image
        """
        assert self.is_equal_shape(other, consider_channel=False)
        other_binaryrev = other.binaryrev(method=binarization_method)
        return np.sum(
            self.binaryrev(method=binarization_method) * other_binaryrev
        ) / np.sum(other_binaryrev)

    def score_contains_segments(
        self,
        segments: Sequence[geo.Segment],
        dilate_kernel: tuple = (5, 5),
        dilate_iterations: int = 0,
        binarization_method: BinarizationMethods = "sauvola",
        resize_factor: float = 1.0,
    ) -> list[float]:
        """Compute the contains score in [0, 1] for each individual segment.
        This method can be better than score_contains_polygons in some
        cases.
        It provides a score for each single segments. This way it is better to
        identify which segments specifically are contained in the image or not.

        Args:
            segments (NDArray | list[geo.Segment]): a list of segments
            dilate_kernel (tuple, optional): dilate kernel param. Defaults to (5, 5).
            dilate_iterations (int, optional): dilate iterations param. Defaults to 0.
            binarization_method (str, optional): binarization method. Here
                we can afford the sauvola method since we crop the image first
                and the binarization occurs on a small image.
                Defaults to "sauvola".
            resize_factor (float, optional): resize factor that can be adjusted to
                provide extra speed. A lower value will be faster but less accurate.
                Typically 0.5 works well but less can have a negative impact on accuracy
                Defaults to 1.0 which implies no resize.

        Returns:
            NDArray: list of score for each individual segment in the same order
                as the list of segments
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        added_width = 10
        height_crop = 30
        mid_height_crop = int(height_crop / 2)
        score_segments: list[float] = []

        for segment in segments:

            im = self.crop_segment_faster(
                segment=segment.asarray,
                dim_crop_rect=(-1, height_crop),
                added_width=added_width,
                pad_value=255,
            )

            im.dilate(kernel=dilate_kernel, iterations=dilate_iterations)

            im.resize(factor=resize_factor)

            # re-compute the segment in the crop referential
            segment_crop = geo.Segment(
                np.array(
                    [
                        [added_width, mid_height_crop],
                        [segment.length + added_width, mid_height_crop],
                    ]
                )
                * resize_factor
            )

            # create all-white image of same size as original with the segment drawn
            other = (
                im.copy()
                .as_white()
                .draw_segments(
                    segments=[segment_crop],
                    render=SegmentsRender(thickness=1, default_color=(0, 0, 0)),
                )
                .as_grayscale()
            )

            score = im.score_contains_v2(
                other=other, binarization_method=binarization_method
            )

            score_segments.append(score)

        return score_segments

    def score_contains_polygons(
        self,
        polygons: Sequence[geo.Polygon],
        dilate_kernel: tuple = (5, 5),
        dilate_iterations: int = 0,
        binarization_method: BinarizationMethods = "sauvola",
        resize_factor: float = 1.0,
    ) -> list[float]:
        """Compute the contains score in [0, 1] for each individual polygon.

        Beware: this method is different from the score_contains method because in
        this case you can emphasize the base image by dilating its content.

        Everything that is a 1 in the rmask will be dilated to give more chance for the
        contour to be contained within the image in the calculation. This way you
        can control the sensitivity of the score.

        Args:
            polygons (Sequence[Polygon]): Polygon object
            dilate_kernel (tuple, optional): dilate kernel param. Defaults to (5, 5).
            dilate_iterations (int, optional): dilate iterations param. Defaults to 0.
            binarization_method (str, optional): binarization method. Here
                we can afford the sauvola method since we crop the image first
                and the binarization occurs on a small image.
                Defaults to "sauvola".
            resize_factor (float, optional): resize factor that can be adjusted to
                provide extra speed. A lower value will be faster but less accurate.
                Typically 0.5 works well but less can have a negative impact on accuracy
                Defaults to 1.0 which implies no resize.

        Returns:
            float: a score from 0 to 1. The greater the score the greater the contour
                 is contained within the original image
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        extra_border_size = 10
        scores: list[float] = []
        for polygon in polygons:

            im = self.crop_from_polygon(
                polygon=polygon,
                copy=True,
                pad=True,
                clip=False,
                extra_border_size=extra_border_size,
                pad_value=255,
            )

            im.dilate(kernel=dilate_kernel, iterations=dilate_iterations)

            im.resize(factor=resize_factor)

            # re-compute the polygon in the crop referential
            polygon_crop = geo.Polygon(
                (polygon.crop_coordinates + extra_border_size) * resize_factor
            )

            # create all-white image of same size as original with the geometry entity
            other = (
                im.copy()
                .as_white()
                .draw_polygons(
                    polygons=[polygon_crop],
                    render=PolygonsRender(thickness=1, default_color=(0, 0, 0)),
                )
                .as_grayscale()
            )

            cur_score = im.score_contains_v2(
                other=other, binarization_method=binarization_method
            )

            scores.append(cur_score)

        return scores

    def score_contains_linear_splines(
        self,
        splines: Sequence[geo.LinearSpline],
        dilate_kernel: tuple = (5, 5),
        dilate_iterations: int = 0,
        binarization_method: BinarizationMethods = "sauvola",
        resize_factor: float = 1.0,
    ) -> list[float]:
        """Compute the contains score in [0, 1]for each individual LinearSpline.
        It provides a score for each single linear spline.

        Args:
            splines (Sequence[LinearSpline]): a list of linear splines objects
            dilate_kernel (tuple, optional): dilate kernel param. Defaults to (5, 5).
            dilate_iterations (int, optional): dilate iterations param. Defaults to 0.
            binarization_method (str, optional): binarization method. Here
                we can afford the sauvola method since we crop the image first
                and the binarization occurs on a small image.
                Defaults to "sauvola".
            resize_factor (float, optional): resize factor that can be adjusted to
                provide extra speed. A lower value will be faster but less accurate.
                Typically 0.5 works well but less can have a negative impact on accuracy
                Defaults to 1.0 which implies no resize.
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        extra_border_size = 10
        scores: list[float] = []
        for spline in splines:
            im = self.crop_from_linear_spline(
                spline=spline,
                copy=True,
                pad=True,
                clip=False,
                extra_border_size=extra_border_size,
                pad_value=255,
            )

            im.dilate(kernel=dilate_kernel, iterations=dilate_iterations)

            im.resize(factor=resize_factor)

            spline_crop = geo.LinearSpline(
                (spline.crop_coordinates + extra_border_size) * resize_factor
            )

            # create all-white image of same size as original with the geometry entity
            other = (
                im.copy()
                .as_white()
                .draw_splines(
                    splines=[spline_crop],
                    render=LinearSplinesRender(thickness=1, default_color=(0, 0, 0)),
                )
                .as_grayscale()
            )

            cur_score = im.score_contains_v2(
                other=other, binarization_method=binarization_method
            )

            scores.append(cur_score)

        return scores

    def score_contains_linear_entities(
        self,
        entities: Sequence[LinearEntity],
        dilate_kernel: tuple = (5, 5),
        dilate_iterations: int = 0,
        binarization_method: BinarizationMethods = "sauvola",
        resize_factor: float = 1.0,
    ) -> list[float]:
        """Compute the contains score in [0, 1] for each individual linear entity
        (either LinearSpline or Segment).

        Args:
            entities (list[geo.LinearEntity]): a list of linear entities
                (splines or segments)
            dilate_kernel (tuple, optional): dilate kernel param. Defaults to (5, 5).
            dilate_iterations (int, optional): dilate iterations param. Defaults to 0.
            binarization_method (BinarizationMethods, optional): binarization method.
                Defaults to "sauvola".
            resize_factor (float, optional): resize factor for speed/accuracy tradeoff.
                Defaults to 1.0.

        Returns:
            list[float]: list of scores for each individual entity
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        scores = []
        for entity in entities:
            if isinstance(entity, geo.LinearSpline):
                score = self.score_contains_linear_splines(
                    splines=[entity],
                    dilate_kernel=dilate_kernel,
                    dilate_iterations=dilate_iterations,
                    binarization_method=binarization_method,
                    resize_factor=resize_factor,
                )[0]
            elif isinstance(entity, geo.Segment):
                score = self.score_contains_segments(
                    segments=[entity],
                    dilate_kernel=dilate_kernel,
                    dilate_iterations=dilate_iterations,
                    binarization_method=binarization_method,
                    resize_factor=resize_factor,
                )[0]
            else:
                raise TypeError(
                    f"Unsupported entity type: {type(entity)}. "
                    "Expected LinearSpline or Segment."
                )
            scores.append(score)
        return scores

    def score_distance_from_center(
        self, point: NDArray, method: ScoreDistanceFromCenterMethods = "linear"
    ) -> float:
        """Compute a score to evaluate how far a point is from the
        image center point.

        A score close to 0 means that the point and the image center are far away.
        A score close to 1 means that the point and the image center are close.

        It is particularly useful when calling it where the point argument is a
        contour centroid. Then, a score equal to 1 means that the contour and image
        centers coincide.

        This method can be used to compute a score for a contour centroid:
        - A small score should be taken into account and informs us that the contour
        found is probably wrong.
        - On the contrary, a high score does not ensure a high quality contour.

        Args:
            point (NDArray): 2D point
            method (str): the method to be used to compute the score. Defaults to
                "linear".

        Returns:
            float: a score from 0 to 1.
        """

        def gaussian_2d(
            x: float,
            y: float,
            x0: float = 0.0,
            y0: float = 0.0,
            amplitude: float = 1.0,
            sigmax: float = 1.0,
            sigmay: float = 1.0,
        ) -> float:
            # pylint: disable=too-many-positional-arguments,too-many-arguments
            return amplitude * np.exp(
                -((x - x0) ** 2 / (2 * sigmax**2) + (y - y0) ** 2 / (2 * sigmay**2))
            )

        def cone_positive_2d(
            x: float,
            y: float,
            x0: float = 0.0,
            y0: float = 0.0,
            amplitude: float = 1.0,
            radius: float = 1.0,
        ) -> float:
            # pylint: disable=too-many-positional-arguments,too-many-arguments
            r = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
            if r >= radius:
                return 0
            return amplitude * (1 - r / radius)

        if method == "linear":
            return cone_positive_2d(
                x=point[0],
                y=point[1],
                x0=self.center[0],
                y0=self.center[1],
                radius=self.norm_side_length / 2,
            )
        if method == "gaussian":
            return gaussian_2d(
                x=point[0],
                y=point[1],
                x0=self.center[0],
                y0=self.center[1],
                sigmax=self.dist_pct(0.1),
                sigmay=self.dist_pct(0.1),
            )

        raise ValueError(f"Unknown method {method}")

    def __str__(self) -> str:
        """String representation of the image

        Returns:
            str: string
        """
        return (
            self.__class__.__name__
            + "(height="
            + str(self.height)
            + ", width="
            + str(self.width)
            + ", n_channels="
            + str(self.channels)
            + ")"
        )

    def _repr_image(self, image_format: str, **kwargs: Any) -> Optional[bytes]:
        """Helper function for iPython display hook.

        Just reused the code from PIL library:
        https://github.com/python-pillow/Pillow/blob/main/src/PIL/Image.py

        Args:
          image_format (str): Image format.

        Returns:
            (bytes, optional): image as bytes, saved into the given format.
        """
        b = io.BytesIO()
        try:
            im = self.show()
            im.save(b, image_format, **kwargs)
        except Exception:  # pylint: disable=broad-except
            return None
        return b.getvalue()

    def _repr_png_(self) -> Optional[bytes]:
        """iPython display hook support for PNG format.

        Returns:
            (bytes, optional): PNG version of the image as bytes
        """
        return self._repr_image("PNG", compress_level=1)

    def _repr_jpeg_(self) -> Optional[bytes]:
        """iPython display hook support for JPEG format.

        Returns:
            (bytes, optional): JPEG version of the image as bytes
        """
        return self._repr_image("JPEG")
