from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Sized
from numbers import Number
from pathlib import Path
from typing import Union

import numpy as np
import SimpleITK as sitk
import torch

from ....data.image import Image
from ....data.image import ScalarImage
from ....data.io import get_sitk_metadata_from_ras_affine
from ....data.io import sitk_to_nib
from ....data.subject import Subject
from ....types import TypePath
from ....types import TypeSpacing
from ....types import TypeTripletFloat
from ...spatial_transform import SpatialTransform

TypeTarget = Union[TypeSpacing, str, Path, Image, None]
ONE_MILLIMITER_ISOTROPIC = 1


class Resample(SpatialTransform):
    """Resample image to a different physical space.

    This is a powerful transform that can be used to change the image shape
    or spatial metadata, or to apply a spatial transformation.

    Args:
        target: Argument to define the output space. Can be one of:

            - Output spacing :math:`(s_w, s_h, s_d)`, in mm. If only one value
              :math:`s` is specified, then :math:`s_w = s_h = s_d = s`.

            - Path to an image that will be used as reference.

            - Instance of :class:`~torchio.Image`.

            - Name of an image key in the subject.

            - Tuple ``(spatial_shape, affine)`` defining the output space.

        pre_affine_name: Name of the *image key* (not subject key) storing an
            affine matrix that will be applied to the image header before
            resampling. If ``None``, the image is resampled with an identity
            transform. See usage in the example below.
        image_interpolation: See :ref:`Interpolation`.
        label_interpolation: See :ref:`Interpolation`.
        scalars_only: Apply only to instances of :class:`~torchio.ScalarImage`.
            Used internally by :class:`~torchio.transforms.RandomAnisotropy`.
        antialias: If ``True``, apply Gaussian smoothing before
            downsampling along any dimension that will be downsampled. For example,
            if the input image has spacing (0.5, 0.5, 4) and the target
            spacing is (1, 1, 1), the image will be smoothed along the first two
            dimensions before resampling. Label maps are not smoothed.
            The standard deviations of the Gaussian kernels are computed according to
            the method described in Cardoso et al.,
            `Scale factor point spread function matching: beyond aliasing in image
            resampling
            <https://link.springer.com/chapter/10.1007/978-3-319-24571-3_81>`_,
            MICCAI 2015.
        **kwargs: See :class:`~torchio.transforms.Transform` for additional
            keyword arguments.

    Example:
        >>> import torch
        >>> import torchio as tio
        >>> transform = tio.Resample()                      # resample all images to 1mm isotropic
        >>> transform = tio.Resample(2)                     # resample all images to 2mm isotropic
        >>> transform = tio.Resample('t1')                  # resample all images to 't1' image space
        >>> # Example: using a precomputed transform to MNI space
        >>> ref_path = tio.datasets.Colin27().t1.path  # this image is in the MNI space, so we can use it as reference/target
        >>> affine_matrix = tio.io.read_matrix('transform_to_mni.txt')  # from a NiftyReg registration. Would also work with e.g. .tfm from SimpleITK
        >>> image = tio.ScalarImage(tensor=torch.rand(1, 256, 256, 180), to_mni=affine_matrix)  # 'to_mni' is an arbitrary name
        >>> transform = tio.Resample(colin.t1.path, pre_affine_name='to_mni')  # nearest neighbor interpolation is used for label maps
        >>> transformed = transform(image)  # "image" is now in the MNI space

    .. note::
        The ``antialias`` option is recommended when large (e.g. > 2×) downsampling
        factors are expected, particularly for offline (before training) preprocessing,
        when run times are not a concern.

    .. plot::

        import torchio as tio
        subject = tio.datasets.FPG()
        subject.remove_image('seg')
        resample = tio.Resample(8)
        t1_resampled = resample(subject.t1)
        subject.add_image(t1_resampled, 'Antialias off')
        resample = tio.Resample(8, antialias=True)
        t1_resampled_antialias = resample(subject.t1)
        subject.add_image(t1_resampled_antialias, 'Antialias on')
        subject.plot()
    """

    def __init__(
        self,
        target: TypeTarget = ONE_MILLIMITER_ISOTROPIC,
        image_interpolation: str = 'linear',
        label_interpolation: str = 'nearest',
        pre_affine_name: str | None = None,
        scalars_only: bool = False,
        antialias: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.target = target
        self.image_interpolation = self.parse_interpolation(
            image_interpolation,
        )
        self.label_interpolation = self.parse_interpolation(
            label_interpolation,
        )
        self.pre_affine_name = pre_affine_name
        self.scalars_only = scalars_only
        self.antialias = antialias
        self.args_names = [
            'target',
            'image_interpolation',
            'label_interpolation',
            'pre_affine_name',
            'scalars_only',
            'antialias',
        ]

    @staticmethod
    def _parse_spacing(spacing: TypeSpacing) -> tuple[float, float, float]:
        result: Iterable
        if isinstance(spacing, Iterable) and len(spacing) == 3:
            result = spacing
        elif isinstance(spacing, Number):
            result = 3 * (spacing,)
        else:
            message = (
                'Target must be a string, a positive number'
                f' or a sequence of positive numbers, not {type(spacing)}'
            )
            raise ValueError(message)
        if np.any(np.array(spacing) <= 0):
            message = f'Spacing must be strictly positive, not "{spacing}"'
            raise ValueError(message)
        return result

    @staticmethod
    def check_affine(affine_name: str, image: Image):
        if not isinstance(affine_name, str):
            message = f'Affine name argument must be a string, not {type(affine_name)}'
            raise TypeError(message)
        if affine_name in image:
            matrix = image[affine_name]
            if not isinstance(matrix, (np.ndarray, torch.Tensor)):
                message = (
                    'The affine matrix must be a NumPy array or PyTorch'
                    f' tensor, not {type(matrix)}'
                )
                raise TypeError(message)
            if matrix.shape != (4, 4):
                message = f'The affine matrix shape must be (4, 4), not {matrix.shape}'
                raise ValueError(message)

    @staticmethod
    def check_affine_key_presence(affine_name: str, subject: Subject):
        for image in subject.get_images(intensity_only=False):
            if affine_name in image:
                return
        message = (
            f'An affine name was given ("{affine_name}"), but it was not found'
            ' in any image in the subject'
        )
        raise ValueError(message)

    def apply_transform(self, subject: Subject) -> Subject:
        use_pre_affine = self.pre_affine_name is not None
        if use_pre_affine:
            assert self.pre_affine_name is not None  # for mypy
            self.check_affine_key_presence(self.pre_affine_name, subject)

        for image in self.get_images(subject):
            # If the current image is the reference, don't resample it
            if self.target is image:
                continue

            # If the target is not a string, or is not an image in the subject,
            # do nothing
            try:
                target_image = subject[self.target]
                if target_image is image:
                    continue
            except (KeyError, TypeError, RuntimeError):
                pass

            # Choose interpolation
            if not isinstance(image, ScalarImage):
                if self.scalars_only:
                    continue
                interpolation = self.label_interpolation
            else:
                interpolation = self.image_interpolation
            interpolator = self.get_sitk_interpolator(interpolation)

            # Apply given affine matrix if found in image
            if use_pre_affine and self.pre_affine_name in image:
                assert self.pre_affine_name is not None  # for mypy
                self.check_affine(self.pre_affine_name, image)
                matrix = image[self.pre_affine_name]
                if isinstance(matrix, torch.Tensor):
                    matrix = matrix.numpy()
                image.affine = matrix @ image.affine

            floating_sitk = image.as_sitk(force_3d=True)

            resampler = self._get_resampler(
                interpolator,
                floating_sitk,
                subject,
                self.target,
            )
            if self.antialias and isinstance(image, ScalarImage):
                downsampling_factor = self._get_downsampling_factor(
                    floating_sitk,
                    resampler,
                )
                sigmas = self._get_sigmas(
                    downsampling_factor,
                    floating_sitk.GetSpacing(),
                )
                floating_sitk = self._smooth(floating_sitk, sigmas)
            resampled = resampler.Execute(floating_sitk)

            array, affine = sitk_to_nib(resampled)
            image.set_data(torch.as_tensor(array))
            image.affine = affine
        return subject

    @staticmethod
    def _smooth(
        image: sitk.Image,
        sigmas: np.ndarray,
        epsilon: float = 1e-9,
    ) -> sitk.Image:
        """Smooth the image with a Gaussian kernel.

        Args:
            image: Image to be smoothed.
            sigmas: Standard deviations of the Gaussian kernel for each
                dimension. If a value is NaN, no smoothing is applied in that
                dimension.
            epsilon: Small value to replace NaN values in sigmas, to avoid
                division-by-zero errors.
        """

        sigmas[np.isnan(sigmas)] = epsilon  # no smoothing in that dimension
        gaussian = sitk.SmoothingRecursiveGaussianImageFilter()
        gaussian.SetSigma(sigmas.tolist())
        smoothed = gaussian.Execute(image)
        return smoothed

    @staticmethod
    def _get_downsampling_factor(
        floating: sitk.Image,
        resampler: sitk.ResampleImageFilter,
    ) -> np.ndarray:
        """Get the downsampling factor for each dimension.

        The downsampling factor is the ratio between the output spacing and
        the input spacing. If the output spacing is smaller than the input
        spacing, the factor is set to NaN, meaning downsampling is not applied
        in that dimension.

        Args:
            floating: The input image to be resampled.
            resampler: The resampler that will be used to resample the image.
        """
        input_spacing = np.array(floating.GetSpacing())
        output_spacing = np.array(resampler.GetOutputSpacing())
        factors = output_spacing / input_spacing
        no_downsampling = factors <= 1
        factors[no_downsampling] = np.nan
        return factors

    def _get_resampler(
        self,
        interpolator: int,
        floating: sitk.Image,
        subject: Subject,
        target: TypeTarget,
    ) -> sitk.ResampleImageFilter:
        """Instantiate a SimpleITK resampler."""
        resampler = sitk.ResampleImageFilter()
        resampler.SetInterpolator(interpolator)
        self._set_resampler_reference(
            resampler,
            target,  # type: ignore[arg-type]
            floating,
            subject,
        )
        return resampler

    def _set_resampler_reference(
        self,
        resampler: sitk.ResampleImageFilter,
        target: TypeSpacing | TypePath | Image,
        floating_sitk,
        subject,
    ):
        # Target can be:
        # 1) An instance of torchio.Image
        # 2) An instance of pathlib.Path
        # 3) A string, which could be a path or an image in subject
        # 4) A number or sequence of numbers for spacing
        # 5) A tuple of shape, affine
        # The fourth case is the different one
        if isinstance(target, (str, Path, Image)):
            if isinstance(target, Image):
                # It's a TorchIO image
                image = target
            elif Path(target).is_file():
                # It's an existing file
                path = target
                image = ScalarImage(path)
            else:  # assume it's the name of an image in the subject
                try:
                    image = subject[target]
                except KeyError as error:
                    message = (
                        f'Image name "{target}" not found in subject.'
                        f' If "{target}" is a path, it does not exist or'
                        ' permission has been denied'
                    )
                    raise ValueError(message) from error
            self._set_resampler_from_shape_affine(
                resampler,
                image.spatial_shape,
                image.affine,
            )
        elif isinstance(target, Number):  # one number for target was passed
            self._set_resampler_from_spacing(resampler, target, floating_sitk)
        elif isinstance(target, Iterable) and len(target) == 2:
            assert not isinstance(target, str)  # for mypy
            shape, affine = target
            if not (isinstance(shape, Sized) and len(shape) == 3):
                message = (
                    'Target shape must be a sequence of three integers, but'
                    f' "{shape}" was passed'
                )
                raise RuntimeError(message)
            if not affine.shape == (4, 4):
                message = (
                    'Target affine must have shape (4, 4) but the following'
                    f' was passed:\n{shape}'
                )
                raise RuntimeError(message)
            self._set_resampler_from_shape_affine(
                resampler,
                shape,
                affine,
            )
        elif isinstance(target, Iterable) and len(target) == 3:
            self._set_resampler_from_spacing(resampler, target, floating_sitk)
        else:
            raise RuntimeError(f'Target not understood: "{target}"')

    def _set_resampler_from_shape_affine(self, resampler, shape, affine):
        origin, spacing, direction = get_sitk_metadata_from_ras_affine(affine)
        resampler.SetOutputDirection(direction)
        resampler.SetOutputOrigin(origin)
        resampler.SetOutputSpacing(spacing)
        resampler.SetSize(shape)

    def _set_resampler_from_spacing(self, resampler, target, floating_sitk):
        target_spacing = self._parse_spacing(target)
        reference_image = self.get_reference_image(
            floating_sitk,
            target_spacing,
        )
        resampler.SetReferenceImage(reference_image)

    @staticmethod
    def get_reference_image(
        floating_sitk: sitk.Image,
        spacing: TypeTripletFloat,
    ) -> sitk.Image:
        old_spacing = np.array(floating_sitk.GetSpacing(), dtype=float)
        new_spacing = np.array(spacing, dtype=float)
        old_size = np.array(floating_sitk.GetSize())
        old_last_index = old_size - 1
        old_last_index_lps = np.array(
            floating_sitk.TransformIndexToPhysicalPoint(old_last_index.tolist()),
            dtype=float,
        )
        old_origin_lps = np.array(floating_sitk.GetOrigin(), dtype=float)
        center_lps = (old_last_index_lps + old_origin_lps) / 2
        # We use floor to avoid extrapolation by keeping the extent of the
        # new image the same or smaller than the original.
        new_size = np.floor(old_size * old_spacing / new_spacing)
        # We keep singleton dimensions to avoid e.g. making 2D images 3D
        new_size[old_size == 1] = 1
        direction = np.asarray(floating_sitk.GetDirection(), dtype=float).reshape(3, 3)
        half_extent = (new_size - 1) / 2 * new_spacing
        new_origin_lps = (center_lps - direction @ half_extent).tolist()
        reference = sitk.Image(
            new_size.astype(int).tolist(),
            floating_sitk.GetPixelID(),
            floating_sitk.GetNumberOfComponentsPerPixel(),
        )
        reference.SetDirection(floating_sitk.GetDirection())
        reference.SetSpacing(new_spacing.tolist())
        reference.SetOrigin(new_origin_lps)
        return reference

    @staticmethod
    def _get_sigmas(downsampling_factor: np.ndarray, spacing: np.ndarray) -> np.ndarray:
        """Compute optimal standard deviation for Gaussian kernel.

        From Cardoso et al., `Scale factor point spread function matching:
        beyond aliasing in image resampling
        <https://link.springer.com/chapter/10.1007/978-3-319-24571-3_81>`_,
        MICCAI 2015.

        Args:
            downsampling_factor: Array with the downsampling factor for each
                dimension.
            spacing: Array with the spacing of the input image in mm.
        """
        k = downsampling_factor
        # Equation from top of page 678 of proceedings (4/9 in the PDF)
        variance = (k**2 - 1) * (2 * np.sqrt(2 * np.log(2))) ** (-2)
        sigma = spacing * np.sqrt(variance)
        return sigma
