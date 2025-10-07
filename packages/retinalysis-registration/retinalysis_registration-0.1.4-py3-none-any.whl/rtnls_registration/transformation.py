from functools import reduce
from enum import Enum
from abc import ABC, abstractmethod

import cv2
import numpy as np
from scipy.ndimage import map_coordinates
from sklearn.preprocessing import PolynomialFeatures


class Interpolation(Enum):
    NEAREST = cv2.INTER_NEAREST
    BILINEAR = cv2.INTER_LINEAR
    BICUBIC = cv2.INTER_CUBIC


def get_param_xy(param):
    if hasattr(param, '__iter__') and len(param) == 2:
        return param
    else:
        return param, param


class Transform(ABC):
    @abstractmethod
    def apply(self, points, **kwargs):
        """Apply the transform to the given points."""
        pass

    @abstractmethod
    def apply_inverse(self, points, **kwargs):
        """Apply the inverse transform to the given points."""
        pass

    @abstractmethod
    def warp(self, image, out_size=None, **kwargs):
        """Warp an image using this transform."""
        pass

    @abstractmethod
    def warp_inverse(self, image, out_size=None, **kwargs):
        """Warp an image using the inverse of this transform."""
        pass

    @abstractmethod
    def get_dsize(self, image, out_size=None):
        """Calculate output image dimensions."""
        pass

    @abstractmethod
    def to_dict(self):
        """Convert transform parameters to a dictionary."""
        pass

    def __repr__(self):
        """Default string representation for transform classes."""
        return f"{self.__class__.__name__}()"


# ---- Internal helpers (kept local to this module) ----
def _normalize_image_for_warp(image, cval=0.0):
    original_dtype = image.dtype
    if original_dtype == np.uint8:
        return image.astype(np.float32) / 255.0, float(cval) / 255.0, original_dtype
    elif original_dtype == bool:
        return image.astype(np.float32), float(cval), original_dtype
    else:
        return image.astype(np.float32), float(cval), original_dtype


def _restore_image_dtype(image_float, original_dtype):
    if original_dtype == np.uint8:
        return (np.clip(image_float, 0.0, 1.0) * 255.0).astype(np.uint8)
    elif original_dtype == bool:
        return (image_float > 0.5)
    else:
        return image_float.astype(original_dtype, copy=False)


def _remap_image(image_float, coords, order=1, mode='constant', cval=0.0):
    ys, xs = coords
    if len(image_float.shape) == 3:
        channels = image_float.shape[2]
        h, w = ys.shape
        result = np.zeros((h, w, channels), dtype=np.float32)
        for i in range(channels):
            result[:, :, i] = map_coordinates(
                image_float[:, :, i], (ys, xs),
                order=order, mode=mode, cval=cval
            ).reshape(h, w)
        return result
    else:
        h, w = ys.shape
        return map_coordinates(
            image_float, (ys, xs),
            order=order, mode=mode, cval=cval
        ).reshape(h, w)


class ProjectiveTransform(Transform):
    
    def __init__(self, M):
        self.M = M
        self.M_inv = np.linalg.inv(M)

    def to_dict(self):
        return {
            "type": "ProjectiveTransform",
            "Matrix": [float(f) for f in self.M.flatten()],
        }

    @property
    def scale(self):
        """Geometric mean scale: sqrt(|det(A)|) for A = M[:2, :2]."""
        return np.sqrt(abs(self.det2x2))

    @property
    def A(self):
        """Top-left 2x2 submatrix of the homogeneous matrix."""
        return self.M[:2, :2]

    @property
    def det2x2(self):
        """Determinant of the 2x2 linear part A."""
        return float(np.linalg.det(self.A))

    def _svd_decompose(self):
        """Return proper SVD-based decomposition A = R @ S @ Vt with det(R)=+1.

        Returns (R, s1, s2, Vt) where s1>=s2 are singular values and R is a
        proper rotation matrix.
        """
        U, S, Vt = np.linalg.svd(self.A)
        R = U @ Vt
        if np.linalg.det(R) < 0:
            U[:, -1] *= -1
            S[-1] *= -1
            R = U @ Vt
        s1, s2 = float(S[0]), float(S[1])
        return R, s1, s2, Vt

    @property
    def scale_xy(self):
        """Singular value scales (sx, sy) from SVD of A."""
        _, s1, s2, _ = self._svd_decompose()
        return (s1, s2)

    @property
    def rotation_matrix(self):
        """Proper rotation component from polar decomposition of A."""
        R, _, _, _ = self._svd_decompose()
        return R

    @property
    def rotation_degrees(self):
        """Rotation angle in degrees from the rotation matrix."""
        R = self.rotation_matrix
        angle = np.degrees(np.arctan2(R[1, 0], R[0, 0]))
        return float(angle)

    def apply(self, points, **kwargs):
        # Add homogeneous coordinate (1) to each point
        points_homogeneous = np.column_stack([points, np.ones(len(points))])
        p = np.dot(points_homogeneous, self.M.T)
        # Normalize by dividing by the last column (homogeneous coordinate)
        return p[:, :2] / p[:, [-1]]

    def apply_inverse(self, points, **kwargs):
        # Add homogeneous coordinate (1) to each point
        points_homogeneous = np.column_stack([points, np.ones(len(points))])
        p = np.dot(points_homogeneous, self.M_inv.T)
        # Normalize by dividing by the last column (homogeneous coordinate)
        return p[:, :2] / p[:, [-1]]

    def get_dsize(self, image, out_size=None):
        if out_size is None:
            h, w = image.shape[:2]
            corners = np.array([[0, 0], [0, h], [w, h], [w, 0]])
            # Use max for width and height independently
            return tuple(np.ceil(self.apply(corners).max(axis=0)).astype(int))
        else:
            h, w = out_size
            return (w, h)

    def warp(self, image, out_size=None, **kwargs):
        dsize = self.get_dsize(image, out_size)

        # Extract interpolation flag from kwargs if provided
        flags = kwargs.get('flags', None)

        if flags is None and (image.dtype == bool or image.dtype == np.uint8):
            flags = cv2.INTER_NEAREST

        if flags is not None:
            warped = cv2.warpPerspective(
                image, self.M, dsize=dsize, flags=flags, **kwargs)
        else:
            warped = cv2.warpPerspective(image, self.M, dsize=dsize, **kwargs)

        return warped

    def warp_inverse(self, image, out_size=None, **kwargs):
        dsize = self.get_dsize(image, out_size)

        # Extract interpolation flag from kwargs if provided
        flags = kwargs.get('flags', None)

        if flags is None and (image.dtype == bool or image.dtype == np.uint8):
            flags = cv2.INTER_NEAREST

        if flags is not None:
            warped = cv2.warpPerspective(
                image, self.M_inv, dsize=dsize, flags=flags, **kwargs)
        else:
            warped = cv2.warpPerspective(
                image, self.M_inv, dsize=dsize, **kwargs)

        return warped

    def _repr_html_(self):
        html_table = "<h4>Projective Transform:</h4><table>"

        for row in self.M:
            html_table += "<tr>"
            for val in row:
                html_table += f"<td>{val:.3f}</td>"
            html_table += "</tr>"

        html_table += "</table>"
        return html_table

    def __repr__(self):
        """String representation of the projective transform."""
        s1, s2 = self.scale_xy
        det = self.det2x2
        rot = self.rotation_degrees
        return (
            f"ProjectiveTransform(sx={s1:.3f}, sy={s2:.3f}, det={det:.3f}, rot={rot:.1f}°)"
        )

class Polynomial2DTransform(Transform):
    def __init__(self, model_dx, model_dy, degree=2):
        self.model_dx = model_dx
        self.model_dy = model_dy
        self.degree = degree

        # Validate that models have predict method
        if not hasattr(model_dx, 'predict') or not hasattr(model_dy, 'predict'):
            raise ValueError("Models must have a 'predict' method")

    def to_dict(self):
        def _coeficents(model):
            return [float(f) for f in [model.intercept_, *model.coef_]]

        return {
            "type": "Polynomial2DTransform",
            "degree": int(self.degree),
            "dx": _coeficents(self.model_dx),
            "dy": _coeficents(self.model_dy)
        }

    def _poly_features(self, points):
        return PolynomialFeatures(degree=self.degree).fit_transform(points)

    def apply(self, points, **kwargs):
        points_poly = self._poly_features(points)
        dx = self.model_dx.predict(points_poly)
        dy = self.model_dy.predict(points_poly)
        return np.array(points) - np.array([dx, dy]).T

    def apply_inverse(self, points, **kwargs):
        points_poly = self._poly_features(points)
        dx = self.model_dx.predict(points_poly)
        dy = self.model_dy.predict(points_poly)
        return np.array(points) + np.array([dx, dy]).T

    def get_dsize(self, image, out_size=None):
        """Calculate appropriate output dimensions."""
        if out_size is None:
            return image.shape[:2][::-1]  # Return (w, h) format
        else:
            h, w = out_size
            return (w, h)

    def warp(self, image, out_size=None, fraction=1.0, mode='constant', cval=0.0, order=1, **kwargs):
        if out_size is None:
            h, w = image.shape[:2]
            out_size = (h, w)

        image_float, cval_float, original_dtype = _normalize_image_for_warp(image, cval)

        h, w = out_size
        ys, xs = np.mgrid[0:h, 0:w]
        all_pixels = np.array([xs.flatten(), ys.flatten()]).T
        pixels_poly = self._poly_features(all_pixels)
        dx = self.model_dx.predict(pixels_poly).reshape(h, w)
        dy = self.model_dy.predict(pixels_poly).reshape(h, w)
        pixels_mapped = np.array(
            [(ys - fraction * dy).flatten(), (xs - fraction * dx).flatten()]
        )

        if len(image_float.shape) == 3:
            channels = image_float.shape[2]
            result_float = np.zeros((h, w, channels), dtype=np.float32)
            for i in range(channels):
                result_float[:, :, i] = map_coordinates(
                    image_float[:, :, i], pixels_mapped,
                    order=order, mode=mode, cval=cval_float, **kwargs
                ).reshape(h, w)
        else:
            result_float = map_coordinates(
                image_float, pixels_mapped,
                order=order, mode=mode, cval=cval_float, **kwargs
            ).reshape(h, w)

        # Convert back to original dtype
        return _restore_image_dtype(result_float, original_dtype)

    def warp_inverse(self, image, out_size=None, mode='constant', cval=0.0, order=1, **kwargs):
        if out_size is None:
            out_size = image.shape[:2]
        return self.warp(image, out_size, fraction=-1.0, mode=mode, cval=cval, order=order, **kwargs)

    def _repr_markdown_(self):
        def _coeficents(model):
            return ", ".join(f"{x:.3f}" for x in [model.intercept_, *model.coef_])

        result = f"""
        #### Polynomial2DTransform (degree={self.degree}):
        - dx: ({_coeficents(self.model_dx)}
        - dy: ({_coeficents(self.model_dy)}
        """
        return result.strip()

    def __repr__(self):
        dx_intercept = self.model_dx.intercept_
        dy_intercept = self.model_dy.intercept_
        return f"Polynomial2DTransform(degree={self.degree}, dx_bias={dx_intercept:.3f}, dy_bias={dy_intercept:.3f})"


class CompositeTransform(Transform):
    def __init__(self, transforms):
        if not transforms:
            raise ValueError(
                "Cannot create CompositeTransform with empty transform list")
        self.transforms = transforms

    def to_dict(self):
        return {
            "type": "CompositeTransform",
            "transforms": [t.to_dict() for t in self.transforms],
        }

    def apply(self, points, **kwargs):
        result = points
        for transform in self.transforms:
            result = transform.apply(result, **kwargs)
        return result

    def apply_inverse(self, points, **kwargs):
        """
        Apply the inverse of each transform in reverse order.

        For a composition of transforms T = T1 ∘ T2 ∘ ... ∘ Tn,
        the inverse is T^(-1) = Tn^(-1) ∘ ... ∘ T2^(-1) ∘ T1^(-1)
        """
        result = points
        for transform in reversed(self.transforms):
            result = transform.apply_inverse(result, **kwargs)
        return result

    def get_dsize(self, image, out_size=None):
        """Calculate appropriate output dimensions."""
        if out_size is not None:
            h, w = out_size
            return (w, h)

        # If out_size is None, compute based on the sequence of transforms
        result = image
        for transform in self.transforms:
            w, h = transform.get_dsize(result, None)
            result = np.zeros((h, w) if len(image.shape) ==
                              2 else (h, w, image.shape[2]))
        return (w, h)

    def warp(self, image, out_size=None, mode='constant', cval=0.0, order=1, **kwargs):
        if out_size is None:
            w, h = self.get_dsize(image, None)
            out_size = (h, w)

        image_float, cval_float, original_dtype = _normalize_image_for_warp(image, cval)

        h, w = out_size
        ys, xs = np.mgrid[0:h, 0:w]
        all_pixels = np.array([xs.flatten(), ys.flatten()]).T
        mapped_pixels = all_pixels
        for transform in reversed(self.transforms):
            mapped_pixels = transform.apply_inverse(
                mapped_pixels, mode=mode, cval=cval, order=order, **kwargs)
        xs, ys = mapped_pixels.T

        if len(image_float.shape) == 3:
            channels = image_float.shape[2]
            result_float = np.zeros((h, w, channels), dtype=np.float32)
            for i in range(channels):
                result_float[:, :, i] = map_coordinates(
                    image_float[:, :, i], (ys, xs),
                    order=order, mode=mode, cval=cval_float
                ).reshape(h, w)
        else:
            result_float = map_coordinates(
                image_float, (ys, xs),
                order=order, mode=mode, cval=cval_float
            ).reshape(h, w)

        return _restore_image_dtype(result_float, original_dtype)

    def warp_inverse(self, image, out_size=None, mode='constant', cval=0.0, order=1, **kwargs):
        """
        Warp image using the inverse transformation.

        This is the inverse operation of warp, applying transforms in original order
        but using their inverse transformations.
        """
        if out_size is None:
            w, h = self.get_dsize(image, None)
            out_size = (h, w)

        original_dtype = image.dtype
        if original_dtype == np.uint8:
            image_float = image.astype(np.float32) / 255.0
            cval_float = float(cval) / 255.0
        elif original_dtype == bool:
            image_float = image.astype(np.float32)
            cval_float = float(cval)
        else:
            image_float = image.astype(np.float32)
            cval_float = float(cval)

        h, w = out_size
        ys, xs = np.mgrid[0:h, 0:w]
        all_pixels = np.array([xs.flatten(), ys.flatten()]).T
        mapped_pixels = all_pixels

        for transform in self.transforms:
            mapped_pixels = transform.apply(
                mapped_pixels, mode=mode, cval=cval, order=order, **kwargs)

        xs, ys = mapped_pixels.T

        if len(image_float.shape) == 3:
            channels = image_float.shape[2]
            result_float = np.zeros((h, w, channels), dtype=np.float32)
            for i in range(channels):
                result_float[:, :, i] = map_coordinates(
                    image_float[:, :, i], (ys, xs),
                    order=order, mode=mode, cval=cval_float
                ).reshape(h, w)
        else:
            result_float = map_coordinates(
                image_float, (ys, xs),
                order=order, mode=mode, cval=cval_float
            ).reshape(h, w)

        if original_dtype == np.uint8:
            return (np.clip(result_float, 0.0, 1.0) * 255.0).astype(np.uint8)
        elif original_dtype == bool:
            return (result_float > 0.5)
        else:
            return result_float.astype(original_dtype, copy=False)

    def __repr__(self):
        """String representation of the composite transform."""
        transform_reprs = [repr(t) for t in self.transforms]
        if len(transform_reprs) <= 3:
            transforms_str = " ∘ ".join(transform_reprs)
        else:
            transforms_str = f"{transform_reprs[0]} ∘ ... ∘ {transform_reprs[-1]}"
        return f"CompositeTransform([{transforms_str}])"


def approximate_affine_coefficients(source_points, target_points):
    n = min(len(source_points), len(target_points))

    if n < 3:
        # Handle case with fewer than 3 point pairs
        raise ValueError(
            "Insufficient point pairs to approximate affine transform")

    A = np.array(
        [[xs, ys, 1, 0, 0, 0] for (xs, ys) in source_points]
        + [[0, 0, 0, xs, ys, 1] for (xs, ys) in source_points]
    )

    B = np.array(
        [xt for (xt, yt) in target_points] + [yt for (xt, yt) in target_points]
    )

    coefficients, _, _, _ = np.linalg.lstsq(A, B, rcond=None)

    return coefficients


def exact_affine_coefficients(source_points, target_points):
    # source_points and target_points should be exactly 3 each

    A = np.vstack([source_points.T, np.ones((1, 3))])
    try:
        A_inv = np.linalg.inv(A)
    except np.linalg.LinAlgError:
        raise ValueError(
            "Points are collinear. Unable to compute an affine transform.")

    return np.dot(target_points.T, A_inv).flatten()


def apply_coefficients(coefficients, points):
    c = coefficients
    xs = c[0] * points[:, 0] + c[1] * points[:, 1] + c[2]
    ys = c[3] * points[:, 0] + c[4] * points[:, 1] + c[5]

    return np.array([xs, ys]).T


def approximate_projective_transform(source_points, target_points):
    # based on: https://github.com/opencv/opencv/blob/11b020b9f9e111bddd40bffe3b1759aa02d966f0/modules/imgproc/src/imgwarp.cpp#L3001
    n = min(len(source_points), len(target_points))
    if n < 4:
        raise ValueError(
            "Insufficient point pairs to approximate a projective transform"
        )

    A = []
    B = []
    for (xs, ys), (xt, yt) in zip(source_points, target_points):
        A.append((xs, ys, 1, 0, 0, 0, -xs * xt, -ys * xt))
        B.append(xt)
        A.append((0, 0, 0, xs, ys, 1, -xs * yt, -ys * yt))
        B.append(yt)

    a, c, e, b, d, f, g, h = np.linalg.pinv(A) @ B
    return ProjectiveTransform(np.array([[a, c, e], [b, d, f], [g, h, 1]]))


def approximate_affine_transform(source_points, target_points):
    n = min(len(source_points), len(target_points))

    if n < 3:
        # Handle case with fewer than 3 point pairs
        raise ValueError(
            "Insufficient point pairs to approximate affine transform")

    A = np.array(
        [[xs, ys, 1, 0, 0, 0] for (xs, ys) in source_points]
        + [[0, 0, 0, xs, ys, 1] for (xs, ys) in source_points]
    )

    B = np.array(
        [xt for (xt, yt) in target_points] + [yt for (xt, yt) in target_points]
    )

    coefficients, _, _, _ = np.linalg.lstsq(A, B, rcond=None)

    matrix = np.reshape(np.append(coefficients, [0, 0, 1]), (3, 3))
    return ProjectiveTransform(matrix)


def get_affine_transform(in_size, out_size, rotate=0, scale=1, center=None, flip=(False, False)):
    """
    Parameters:
    in_size: size of the input image (h, w)
    out_size: size of the extracted patch (h, w)
    rotate: angle in degrees
    scale: scaling factor s or (sy, sx)
    center: center of the patch (cy, cx)
    flip: apply horizontal/vertical flipping
    """

    # center to top left corner
    if center is None:
        h, w = get_param_xy(in_size)
        cy, cx = h / 2, w / 2
    else:
        cy, cx = center
    C1 = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]], dtype=float)

    # rotate
    th = rotate * np.pi / 180
    R = np.array(
        [[np.cos(th), -np.sin(th), 0], [np.sin(th), np.cos(th), 0], [0, 0, 1]],
        dtype=float,
    )

    # scale
    sy, sx = get_param_xy(scale)
    S = np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]], dtype=float)

    # top left corner to center
    h, w = get_param_xy(out_size)
    ty = h / 2
    tx = w / 2
    C2 = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], dtype=float)

    M = C2 @ S @ R @ C1
    flip_vertical, flip_horizontal = flip

    if flip_horizontal:
        M = np.array([[-1, 0, w], [0, 1, 0], [0, 0, 1]]) @ M
    if flip_vertical:
        M = np.array([[1, 0, 0], [0, -1, h], [0, 0, 1]]) @ M

    return ProjectiveTransform(M)


def simplify_transforms(transforms):
    def collect_transforms(transforms):
        result = []
        for transform in transforms:
            if isinstance(transform, CompositeTransform):
                result.extend(collect_transforms(transform.transforms))
            else:
                result.append(transform)
        return result

    flattened = collect_transforms(transforms)

    def combine_transforms(group):
        return reduce(lambda acc, t: t.M @ acc, group[1:], group[0].M)
    # Process transforms sequentially
    simplified = []
    projective_group = []

    for transform in flattened:
        if isinstance(transform, ProjectiveTransform):
            projective_group.append(transform)
        else:
            # Process any collected ProjectiveTransforms
            if projective_group:
                combined_matrix = combine_transforms(projective_group)
                simplified.append(ProjectiveTransform(combined_matrix))
                projective_group = []

            # Add the non-projective transform
            simplified.append(transform)

    # Handle any remaining ProjectiveTransforms
    if projective_group:
        combined_matrix = combine_transforms(projective_group)
        simplified.append(ProjectiveTransform(combined_matrix))

    if len(simplified) == 1:
        return simplified[0]
    return CompositeTransform(simplified)

identity = ProjectiveTransform(np.eye(3))