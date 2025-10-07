from dataclasses import dataclass

import numpy as np
from skimage.filters import difference_of_gaussians, sato

from rtnls_registration.cfi_bounds import BoundsBase
from rtnls_registration.mask_extraction import get_cfi_bounds
from rtnls_registration.utils import to_uint8


@dataclass
class PreprocessResult:
    M: np.ndarray
    bounds: BoundsBase
    vessel_enhanced: list
    mask: np.ndarray


def vessel_enhance(
    bounds,
    mask,
    gamma=0.8,
    gauss_min=1,
    gauss_max=16,
    scaling=0.25,
    sigma_min=2,
    sigma_max=4.5,
    sigma_step=0.5,
    **kwargs,
):
    """Enhance vessels via DoG + Sato at multiple scales; return uint8 images list."""
    # Note: all parameters are set emperically, and may not be optimal for all images

    eps = 1e-8
    mask_bool = mask.astype(bool)
    mask_inverted = ~mask_bool

    green_channel = bounds.image[:, :, 1]
    mirrored = bounds.make_mirrored_image(green_channel)
    filtered = difference_of_gaussians(mirrored, gauss_min, gauss_max)

    def sato_at_sigma(sigma):
        s = sato(filtered, sigmas=[sigma])
        s[mask_inverted] = 0
        v = s**gamma
        return np.clip(scaling * v / max(v.std(), eps), 0, 1)

    sigma_range = np.arange(sigma_min, sigma_max + sigma_step / 2, sigma_step)
    vessel_enhanced = [sato_at_sigma(s) for s in sigma_range]
    vessel_enhanced = [to_uint8(v) for v in vessel_enhanced]

    return vessel_enhanced


def preprocess_octa(image, gauss_min=4, gauss_max=6, **kwargs):
    """Simple OCTA preprocessor returning a single uint8 vessel-enhanced image."""
    eps = 1e-8
    im = (image.image[:, :, 1]) / 255
    filtered = difference_of_gaussians(im, gauss_min, gauss_max)
    f_min, f_max = filtered.min(), filtered.max()
    f_norm = (filtered - f_min) / max(f_max - f_min, eps)
    s = sato(1 - f_norm, sigmas=[4])
    result = np.clip(s / max(s.std() ** 0.5, eps), 0, 1)
    return [to_uint8(result)]


def preprocess(image, **kwargs):
    """Compute bounds, mask, and vessel-enhanced images; return `PreprocessResult`."""
    orig_bounds = get_cfi_bounds(image)
    T, bounds = orig_bounds.crop(kwargs.get("resolution", 512))
    mask = bounds.make_binary_mask()

    image_type = kwargs.get("image_type", None)
    if image_type == "OCTA":
        vessel_enhanced = preprocess_octa(bounds, **kwargs)
    else:
        vessel_enhanced = vessel_enhance(bounds, mask, **kwargs)

    return PreprocessResult(T.M, bounds, vessel_enhanced, mask.astype(np.uint8))
