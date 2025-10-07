"""
`BinarizerImage` component is a subpart of the Image Transformer component.

Binarization converts an image to black and white, making every pixel either 0 or 255.
Any color or grayscale image can be binarized. Methods fall into two types:

- **Global**: applies a single threshold to all pixels.
- **Local**: applies varying thresholds per pixel, usually performing better on images
with uneven lighting.

Otary offers **5 basic** and **12 advanced** binarization methods.

Basic methods: simple, otsu, adaptive, bradley, and sauvola are available directly
from the Image object:

```python
import otary as ot

im = ot.Image.from_file(filepath="path/to/file/image")
im.threshold_sauvola()
```

Advanced methods are accessible via the transformer.binarizer attribute:

```python
im.transformer.binarizer.threshold_isauvola()
```
"""

from typing import Literal, Optional, get_args, TYPE_CHECKING

import cv2
import numpy as np
from numpy.typing import NDArray

from otary.image.base import BaseImage

from otary.image.components.transformer.components.binarizer.ops import (
    threshold_bernsen,
    threshold_bradley,
    threshold_feng,
    threshold_gatos,
    threshold_isauvola,
    threshold_niblack_like,
    threshold_su,
    threshold_adotsu,
    threshold_fair,
)

if TYPE_CHECKING:  # pragma: no cover
    from otary.image import Image

BinarizationMethods = Literal[
    "adaptive",
    "otsu",
    "bernsen",
    "niblack",
    "sauvola",
    "wolf",
    "feng",
    "gatos",
    "bradley",
    "nick",
    "su",
    "phansalkar",
    "adotsu",
    "singh",
    "fair",
    "isauvola",
    "wan",
]


class BinarizerImage:
    # pylint: disable=line-too-long
    """BinarizerImage class contains all the binarization methods.

    It includes only two global thresholding methods: `threshold_simple` and `threshold_otsu`. The other methods are local thresholding methods.

    It includes the following binarization methods, sorted by year of publication:

    | Name           | Year | Reference                                                                                                                        |
    |----------------|------|------------------------------------------------------------------------------------------------------------------------------------------|
    | Adaptive       |  -   | [OpenCV Adaptive Thresholding Documentation](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html)                           |
    | Otsu           | 1979 | [A Threshold Selection Method from Gray-Level Histograms](https://ieeexplore.ieee.org/document/4310076)                                  |
    | Bernsen        | 1986 | "Dynamic thresholding of grey-level images" by Bernsen                                                                                   |
    | Niblack        | 1986 | "An Introduction to Digital Image Processing" by Wayne Niblack                                                                           |
    | Sauvola        | 1997 | [Adaptive Document Binarization](https://www.researchgate.net/publication/3710586_Adaptive_Document_Binarization)                        |
    | Wolf           | 2003 | [Extraction and Recognition of Artificial Text in Multimedia Documents](https://hal.science/hal-01504401v1)                              |
    | Feng           | 2004 | [Contrast adaptive binarization of low quality document images](https://www.jstage.jst.go.jp/article/elex/1/16/1_16_501/_pdf)            |
    | Gatos          | 2005 | [Adaptive degraded document image binarization](https://users.iit.demokritos.gr/~bgat/PatRec2006.pdf)                                    |
    | Bradley & Roth | 2007 | [Adaptive Thresholding using the Integral Image](https://www.researchgate.net/publication/220494200_Adaptive_Thresholding_using_the_Integral_Image) |
    | Nick           | 2009 | [Comparison of Niblack inspired Binarization Methods for Ancient Documents](https://www.researchgate.net/publication/221253803)           |
    | Su             | 2010 | [Binarization of historical document images using the local maximum and minimum](https://www.researchgate.net/publication/220933012)                                                             |
    | Phansalkar     | 2011 | [Adaptive Local Thresholding for Detection of Nuclei in Diversely Stained Cytology Images](https://www.researchgate.net/publication/224226466) |
    | Adotsu         | 2011 | [AdOtsu: An adaptive and parameterless generalization of Otsu’s method for document image binarization](https://www.researchgate.net/publication/220602345) |
    | Singh          | 2012 | [A New Local Adaptive Thresholding Technique in Binarization](https://www.researchgate.net/publication/220485031)                        |
    | FAIR           | 2013 | [FAIR: A Fast Algorithm for document Image Restoration](https://amu.hal.science/hal-01479805/document)                                   |
    | ISauvola       | 2016 | [ISauvola: Improved Sauvola’s Algorithm for Document Image Binarization](https://www.researchgate.net/publication/304621554_ISauvola_Improved_Sauvola) |
    | WAN            | 2018 | [Binarization of Document Image Using Optimum Threshold Modification](https://www.researchgate.net/publication/326026836)                 |
    """

    def __init__(self, base: BaseImage) -> None:
        self.base = base

    # ----------------------------- GLOBAL THRESHOLDING -------------------------------

    def threshold_simple(self, thresh: int) -> "Image":
        """Compute the image thresholded by a single value T.
        All pixels with value v <= T are turned black and those with value v > T are
        turned white. This is a global thresholding method.

        Args:
            thresh (int): value to separate the black from the white pixels.
        """
        self.base.as_grayscale()
        self.base.asarray = np.array((self.base.asarray > thresh) * 255, dtype=np.uint8)
        return self.base.parent

    def threshold_otsu(self) -> "Image":
        """Apply Otsu global thresholding.
        This is a global thresholding method that automatically determines
        an optimal threshold value from the image histogram.

        Paper (1979):
        [A Threshold Selection Method from Gray-Level Histograms](https://ieeexplore.ieee.org/document/4310076)

        Consider applying a gaussian blur before for better thresholding results.
        See why in the [OpenCV documentation](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html).
        """
        self.base.as_grayscale()
        _, img_thresholded = cv2.threshold(
            self.base.asarray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        self.base.asarray = img_thresholded
        return self.base.parent

    # ------------------------------ LOCAL THRESHOLDING -------------------------------

    def threshold_adaptive(
        self, block_size: int = 11, constant: float = 2.0
    ) -> "Image":
        """Apply adaptive local thresholding.
        This is a local thresholding method that computes the threshold for a pixel
        based on a small region around it.

        Consider applying a gaussian blur before for better thresholding results.
        See why in the [OpenCV documentation](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html).

        Args:
            block_size (int, optional): Size of a pixel neighborhood that is used to
                calculate a threshold value for the pixel: 3, 5, 7, and so on.
                Defaults to 11.
            constant (int, optional): Constant subtracted from the mean or weighted
                mean. Normally, it is positive but may be zero or negative as well.
                Defaults to 2.
        """
        self.base.as_grayscale()
        self.base.asarray = cv2.adaptiveThreshold(
            src=self.base.asarray,
            maxValue=255,
            adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            thresholdType=cv2.THRESH_BINARY,
            blockSize=block_size,
            C=constant,
        )
        return self.base.parent

    def threshold_bernsen(
        self,
        window_size: int = 75,
        contrast_limit: float = 25,
        threshold_global: int = 100,
    ) -> "Image":
        """Apply Bernsen local thresholding.

        Paper (1986):
        "Dynamic thresholding of grey-level images" by Bernsen.

        Args:
            window_size (int, optional): window size for local computations.
                Defaults to 75.
            contrast_limit (float, optional): contrast limit. If the
                contrast is higher than this value, the pixel is thresholded by the
                bernsen threshold otherwise the global threshold is used.
                Defaults to 25.
            threshold_global (int, optional): global threshold. Defaults to 100.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_bernsen(
            img=self.base.asarray,
            window_size=window_size,
            contrast_limit=contrast_limit,
            threshold_global=threshold_global,
        )
        return self.base.parent

    def threshold_niblack(self, window_size: int = 15, k: float = -0.2) -> "Image":
        """Apply Niblack local thresholding.

        Book (1986):
        "An Introduction to Digital Image Processing" by Wayne Niblack.

        Args:
            window_size (int, optional): apply on the
                image. Defaults to 15.
            k (float, optional): factor to apply to regulate the impact
                of the std. Defaults to -0.2.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_niblack_like(
            img=self.base.asarray, method="niblack", window_size=window_size, k=k
        )[1]
        return self.base.parent

    def threshold_sauvola(
        self, window_size: int = 15, k: float = 0.5, r: float = 128.0
    ) -> "Image":
        """Apply Sauvola local thresholding.
        This is a local thresholding method that computes the threshold for a pixel
        based on a small region around it.

        Paper (1997):
        [Adaptive Document Binarization](https://www.researchgate.net/publication/3710586_Adaptive_Document_Binarization)

        Args:
            window_size (int, optional): sauvola window size to apply on the
                image. Defaults to 15.
            k (float, optional): sauvola k factor to apply to regulate the impact
                of the std. Defaults to 0.5.
            r (float, optional): sauvola r value. Defaults to 128.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_niblack_like(
            img=self.base.asarray, method="sauvola", window_size=window_size, k=k, r=r
        )[1]
        return self.base.parent

    def threshold_wolf(self, window_size: int = 15, k: float = 0.5) -> "Image":
        """Apply Wolf local thresholding.

        Paper (2003):
        [Extraction and Recognition of Artificial Text in Multimedia Documents](https://hal.science/hal-01504401v1)

        Args:
            window_size (int, optional): apply on the
                image. Defaults to 15.
            k (float, optional): factor to apply to regulate the impact
                of the std. Defaults to 0.5.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_niblack_like(
            img=self.base.asarray, method="wolf", window_size=window_size, k=k
        )[1]
        return self.base.parent

    def threshold_feng(
        self,
        w1: int = 19,
        w2: int = 33,
        alpha1: float = 0.12,
        k1: float = 0.25,
        k2: float = 0.04,
        gamma: float = 2.0,
    ) -> "Image":
        """Implementation of the Feng thresholding method.

        Paper (2004):
        [Contrast adaptive binarization of low quality document images](https://www.jstage.jst.go.jp/article/elex/1/16/1_16_501/_pdf)

        Args:
            w1 (int, optional): primary window size. Defaults to 19.
            w2 (int, optional): secondary window value. Defaults to 33.
            alpha1 (float, optional): alpha1 value. Defaults to 0.12.
            k1 (float, optional): k1 value. Defaults to 0.25.
            k2 (float, optional): k2 value. Defaults to 0.04.
            gamma (float, optional): gamma value. Defaults to 2.0.
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        self.base.as_grayscale()
        self.base.asarray = threshold_feng(
            img=self.base.asarray,
            w1=w1,
            w2=w2,
            alpha1=alpha1,
            k1=k1,
            k2=k2,
            gamma=gamma,
        )
        return self.base.parent

    def threshold_gatos(
        self,
        q: float = 0.6,
        p1: float = 0.5,
        p2: float = 0.8,
        lh: Optional[float] = None,
        upsampling: bool = False,
        upsampling_factor: int = 2,
    ) -> "Image":
        """Apply Gatos local thresholding.

        Paper (2005):
        [Adaptive degraded document image binarization](https://users.iit.demokritos.gr/~bgat/PatRec2006.pdf)

        Args:
            q (float, optional): q gatos factor. Defaults to 0.6.
            p1 (float, optional): p1 gatos factor. Defaults to 0.5.
            p2 (float, optional): p2 gatos factor. Defaults to 0.8.
            lh (Optional[float], optional): height of character.
                Defaults to None, meaning it is computed automatically to be
                a fraction of the image size.
            upsampling (bool, optional): whether to apply gatos upsampling definition.
                Defaults to False.
            upsampling_factor (int, optional): gatos upsampling factor. Defaults to 2.
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        # pylint: disable=duplicate-code
        self.base.as_grayscale()
        self.base.asarray = threshold_gatos(
            img=self.base.asarray,
            q=q,
            p1=p1,
            p2=p2,
            lh=lh,
            upsampling=upsampling,
            upsampling_factor=upsampling_factor,
        )
        return self.base.parent

    def threshold_bradley(self, window_size: int = 15, t: float = 0.15) -> "Image":
        """Implementation of the Bradley & Roth thresholding method.

        Paper (2007):
        [Adaptive Thresholding using the Integral Image](https://www.researchgate.net/publication/220494200_Adaptive_Thresholding_using_the_Integral_Image)

        Args:
            window_size (int, optional): window size for local computations.
                Defaults to 15.
            t (float, optional): t value in [0, 1]. Defaults to 0.15.

        Returns:
            NDArray[np.uint8]: output thresholded image
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_bradley(
            img=self.base.asarray, window_size=window_size, t=t
        )
        return self.base.parent

    def threshold_nick(self, window_size: int = 19, k: float = -0.1) -> "Image":
        """Apply Nick local thresholding.

        Paper (2009):
        [Comparison of Niblack inspired Binarization Methods for Ancient Documents](https://www.researchgate.net/publication/221253803)

        The paper suggests to use a window size of 19 and a k factor in [-0.2, -0.1].

        Args:
            window_size (int, optional): apply on the
                image. Defaults to 15.
            k (float, optional): factor to apply to regulate the impact
                of the std. Defaults to -0.1.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_niblack_like(
            img=self.base.asarray, method="nick", window_size=window_size, k=k
        )[1]
        return self.base.parent

    def threshold_su(
        self,
        window_size: int = 3,
        n_min: int = -1,
    ) -> "Image":
        """Compute the Su local thresholding.

        Paper (2010):
        [Binarization of historical document images using the local maximum and minimum](https://www.researchgate.net/publication/220933012)

        Args:
            window_size (int, optional): window size for high contrast image
                computation. Defaults to 3.
            n_min (int, optional): minimum number of high contrast pixels within the
                neighborhood window. Defaults to -1 meaning that n_min = window_size.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_su(
            img=self.base.asarray, window_size=window_size, n_min=n_min
        )
        return self.base.parent

    def threshold_phansalkar(
        self, window_size: int = 40, k: float = 0.25, p: float = 3.0, q: float = 10.0
    ) -> "Image":
        """Apply Phansalkar et al. local thresholding.

        Paper (2011):
        [Adaptive Local Thresholding for Detection of Nuclei in Diversely Stained Cytology Images](https://www.researchgate.net/publication/224226466)

        Args:
            window_size (int, optional): apply on the
                image. Defaults to 40.
            k (float, optional): factor to apply to regulate the impact
                of the std. Defaults to 0.25.
            p (float, optional): Phansalkar parameter to regulate low contrast zones.
                Defaults to 3.0.
            q (float, optional): Phansalkar parameter to regulate low contrast zones.
                Defaults to 10.0.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_niblack_like(
            img=self.base.asarray,
            method="phansalkar",
            window_size=window_size,
            k=k,
            p=p,
            q=q,
        )[1]
        return self.base.parent

    def threshold_adotsu(
        self, grid_size: int = 50, k_sigma: float = 1.6, n_steps: int = 2
    ) -> "Image":
        """Apply Adotsu local thresholding.

        Paper (2011):
        [AdOtsu: An adaptive and parameterless generalization of Otsu’s method for document image binarization](https://www.researchgate.net/publication/220602345)

        Args:
            grid_size (int, optional): window size for local computations.
                Defaults to 15.
            k_sigma (float, optional): k_sigma value in [1, 2]. Defaults to 1.6.
            n_steps (int, optional): number of iterations to update the binarization by
                estimating a new background surface. Defaults to 2.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_adotsu(
            img=self.base.asarray, grid_size=grid_size, k_sigma=k_sigma, n_steps=n_steps
        )
        return self.base.parent

    def threshold_singh(self, window_size: int = 15, k: float = 0.06) -> "Image":
        """Apply Singh local thresholding.

        Paper (2012):
        [A New Local Adaptive Thresholding Technique in Binarization](https://www.researchgate.net/publication/220485031)

        Args:
            window_size (int, optional): apply on the
                image. Defaults to 15.
            k (float, optional): factor to apply to regulate the impact
                of the std. Defaults to 0.06.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_niblack_like(
            img=self.base.asarray, method="singh", window_size=window_size, k=k
        )[1]
        return self.base.parent

    def threshold_fair(
        self,
        sfair_window_size: int = 33,
        sfair_clustering_algo: str = "otsu",
        sfair_clustering_max_iter: int = 20,
        sfair_thining: float = 1.0,
        sfair_alpha: float = 0.38,
        post_stain_max_pixels: int = 25,
        post_misclass_txt: bool = True,
        post_clustering_algo: str = "otsu",
        post_clustering_max_iter: int = 10,
        post_max_iter: int = 15,
        post_window_size: int = 75,
        post_beta: float = 1.0,
    ) -> "Image":
        """Apply FAIR local thresholding.

        Paper (2013):
        [FAIR: A Fast Algorithm for document Image Restoration](https://amu.hal.science/hal-01479805/document)

        Args:
            sfair_window_size (int, optional): window size in preprocess
                to cluster background and foreground pixels around edge pixels.
                This parameter is important as a higher value will make the method
                more robust to noise but also more computationally expensive and slow.
                Defaults to 5.
            sfair_clustering_algo (str, optional): clustering algorithm for the S-FAIR
                step. Defaults to "otsu".
            sfair_clustering_max_iter (int, optional): maximum number of iterations for
                the clustering algorithm within the S-FAIR step. Defaults to 20.
            sfair_thining (float, optional): thining factor in [0, 1]. 0 means no
                thinning which means that all edge pixels are processed.
                1 means that only every
                sfair_window_size // 2 edge pixels are processed which signicantly
                speeds up the computation. Defaults to 1.0.
            sfair_alpha (float, optional): It defines the ratio to compute the lower
                threshold in the 1st step of the S-FAIR step.
                It is generally in [0.3, 0.5].
                Defaults to 0.38.
            post_stain_max_pixels (int, optional): maximum number of pixels for a stain
                to be considered as an unknown connected component. Defaults to 25.
            post_misclass_txt (bool, optional): whether to perform the
                post-processing correct_misclassified_text_pixels step.
                Defaults to True.
            post_clustering_algo (str, optional): clustering algorithm for the
                post-processing step. Defaults to "otsu".
            post_clustering_max_iter (int, optional): maximum number of iterations for
                the clustering algorithm within the post-processing step.
                Defaults to 10.
            post_max_iter (int, optional): maximum number of iterations for the
                correct_misclassified_text_pixels step within the post-processing step.
                Defaults to 15.
            post_window_size (int, optional): window size in postprocess
                to cluster background and foreground pixels around edge pixels.
                This parameter is important as a higher value will make the method
                more robust to noise but also more computationally expensive and slow.
                Defaults to 75.
            post_beta (float, optional): factor to define if the unkown pixels
                should be set as text or background. If beta is 1 then
                unknown pixels are set to text if the number of surrounding text pixels
                (N_t) is higher than the number of surrounding background pixels (N_b).
                Simply N_t > N_b. Beta is the value to put more flexibility on the rule
                and thus set unknown pixels to text if N_t > beta * N_b
                Defaults to 1.0.
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        # pylint: disable=duplicate-code
        self.base.as_grayscale()
        self.base.asarray = threshold_fair(
            img=self.base.asarray,
            sfair_window_size=sfair_window_size,
            sfair_clustering_algo=sfair_clustering_algo,
            sfair_clustering_max_iter=sfair_clustering_max_iter,
            sfair_thining=sfair_thining,
            sfair_alpha=sfair_alpha,
            post_stain_max_pixels=post_stain_max_pixels,
            post_misclass_txt=post_misclass_txt,
            post_clustering_algo=post_clustering_algo,
            post_max_iter=post_max_iter,
            post_clustering_max_iter=post_clustering_max_iter,
            post_window_size=post_window_size,
            post_beta=post_beta,
        )
        return self.base.parent

    def threshold_isauvola(
        self,
        window_size: int = 15,
        k: float = 0.01,
        r: float = 128.0,
        connectivity: int = 8,
        contrast_window_size: int = 3,
        opening_n_min_pixels: int = 0,
        opening_connectivity: int = 8,
    ) -> "Image":
        """Apply ISauvola local thresholding.

        Paper (2016):
        [ISauvola: Improved Sauvola’s Algorithm for Document Image Binarization](https://www.researchgate.net/publication/304621554_ISauvola_Improved_Sauvola)

        Args:
            window_size (int, optional): apply on the
                image. Defaults to 15.
            k (float, optional): factor to apply to regulate the impact
                of the std. Defaults to 0.01.
            r (float, optional): factor to apply to regulate the impact
                of the std. Defaults to 128.
            connectivity (int, optional): connectivity to apply on the
                image. Defaults to 8.
            contrast_window_size (int, optional): contrast window size to apply on the
                image. Defaults to 3.
            opening_n_min_pixels (int, optional): opening n min pixels to apply on the
                image. Defaults to 0.
            opening_connectivity (int, optional): opening connectivity to apply on the
                image. Defaults to 8.
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        self.base.as_grayscale()
        self.base.asarray = threshold_isauvola(
            img=self.base.asarray,
            window_size=window_size,
            k=k,
            r=r,
            connectivity=connectivity,
            contrast_window_size=contrast_window_size,
            opening_n_min_pixels=opening_n_min_pixels,
            opening_connectivity=opening_connectivity,
        )
        return self.base.parent

    def threshold_wan(
        self, window_size: int = 15, k: float = 0.5, r: float = 128.0
    ) -> "Image":
        """Apply Wan local thresholding.

        Paper (2018):
        [Binarization of Document Image Using Optimum Threshold Modification](https://www.researchgate.net/publication/326026836)

        Args:
            window_size (int, optional): apply on the
                image. Defaults to 15.
            k (float, optional): factor to apply to regulate the impact
                of the std. Defaults to 0.5.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_niblack_like(
            img=self.base.asarray, method="wan", window_size=window_size, k=k, r=r
        )[1]
        return self.base.parent

    # ---------------------------- BINARY REPRESENTATION ------------------------------

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
                Look at the BinarizationMethods to see all the available methods.
                Defaults to "sauvola".

        Returns:
            NDArray: array where its inner values are 0 or 1
        """
        if method not in list(get_args(BinarizationMethods)):
            raise ValueError(
                f"Invalid binarization method {method}. "
                f"Must be in {BinarizationMethods}"
            )
        getattr(self, f"threshold_{method}")()
        return self.base.asarray_binary

    def binaryrev(self, method: BinarizationMethods = "sauvola") -> NDArray:
        """Reversed binary representation of the image.
        The value 0 is now 1 and value of 255 are now 0. Black is 1 and white is 0.
        This is why it is called the "binary rev" or "binary reversed".

        Args:
            method (str, optional): the binarization method to apply.
                Defaults to "adaptative".

        Returns:
            NDArray: array where its inner values are 0 or 1
        """
        return 1 - self.binary(method=method)
