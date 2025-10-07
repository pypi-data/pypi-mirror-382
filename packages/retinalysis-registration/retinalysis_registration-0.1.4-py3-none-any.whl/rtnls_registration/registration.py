import cv2
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import PolynomialFeatures
from dataclasses import dataclass

from rtnls_registration.preprocess import preprocess
from rtnls_registration.timing import TimingStats, timing
from rtnls_registration.transformation import (
    CompositeTransform,
    ProjectiveTransform,
    Polynomial2DTransform,
    approximate_projective_transform,
    exact_affine_coefficients,
    simplify_transforms,
)


@dataclass
class Features:
    kp: object
    des: object
    kp_hc: object
    des_hc: object


class Registration:
    """SIFT-based retinal image registration with optional quadratic refinement.

    Parameters
    - refineInlierThreshold: Pixel radius for refinement neighbor search.
    - n_neighbors: Number of spatial neighbors considered during refinement.
    - quadratic: Enable quadratic residual fit when enough inliers are found.
    - preprocess_args: Keyword args forwarded to `preprocess`.
    - max_rotation_deg: Max allowed keypoint rotation difference for matches.
    - max_scale: Max allowed keypoint scale ratio for matches.
    - ransacReprojThreshold: OpenCV RANSAC reprojection threshold (pixels).
    """

    def __init__(self, **kwargs):
        self.refineInlierThreshold = kwargs.get("refineInlierThreshold", 10)
        self.n_neighbors = kwargs.get("n_neighbors", 10)
        self.quadratic = kwargs.get("quadratic", True)
        self.preprocess_args = kwargs.get("preprocess_args", {})

        # angle and scale difference thresholds for valid matches
        self.max_rotation_deg = kwargs.get("max_rotation_deg", 20)
        self.max_scale = kwargs.get("max_scale", 1.8)

        self.ransacReprojThreshold = kwargs.get("ransacReprojThreshold", 10)

        self.sift_high_contrast = cv2.SIFT_create(
            contrastThreshold=kwargs.get("contrastThreshold", 0.1)
        )

        self.sift = cv2.SIFT_create(
            contrastThreshold=kwargs.get("contrastThreshold", 0.05)
        )

        self.stats = TimingStats()
        self.timing = lambda name: timing(self.stats, name)

    def __call__(self, image0, image1):
        """Register `image0` to `image1` and return a `CompositeTransform`."""

        self.set_reference(image0)
        self.set_target(image1)

        return self.run()

    def set_reference(self, image, image_type=None, crop_coords=None):
        """Set reference image; optional `image_type` and crop ((x1,y1),(x2,y2))."""
        self.preprocess_result0, self.features0 = self._init_image(
            image, 0, image_type=image_type, crop_coords=crop_coords
        )

    def set_target(self, image, image_type=None, crop_coords=None):
        """Set target image; optional `image_type` and crop ((x1,y1),(x2,y2))."""
        self.preprocess_result1, self.features1 = self._init_image(
            image, 1, image_type=image_type, crop_coords=crop_coords
        )

    def _init_image(self, image, suffix, image_type=None, crop_coords=None):
        with self.timing(f"preprocess_image{suffix}"):
            cropping_matrix = None
            if crop_coords is not None:
                top_left, bottom_right = crop_coords
                x1, y1 = top_left
                x2, y2 = bottom_right
                image = image[y1:y2, x1:x2]
                source_coords = np.array([[x1, y1], [x1, y2], [x2, y2]])
                w, h = image.shape[:2]
                target_coords = np.array([[0, 0], [0, h], [w, h]])
                a, b, c, d, e, f = exact_affine_coefficients(source_coords, target_coords)
                cropping_matrix = np.array([[a, b, c], [d, e, f], [0, 0, 1]])

            preprocess_result = preprocess(
                image, image_type=image_type, **self.preprocess_args
            )

            if cropping_matrix is not None:
                preprocess_result.M = cropping_matrix @ preprocess_result.M

        with self.timing(f"extract_keypoints{suffix}"):
            vessels = preprocess_result.vessel_enhanced
            mask = preprocess_result.mask

            kp, des = self.extract_keypoints_with(self.sift, vessels, mask)

            last_vessel = vessels[-1] if isinstance(vessels, list) else vessels
            kp_hc, des_hc = self.extract_keypoints_with(
                self.sift_high_contrast, last_vessel, mask
            )

            features = Features(kp, des, kp_hc, des_hc)

        return preprocess_result, features

    def _find_base_transform(self):
        f_hc = {
            "kp0": self.features0.kp_hc,
            "des0": self.features0.des_hc,
            "kp1": self.features1.kp_hc,
            "des1": self.features1.des_hc,
        }
        f = {
            "kp0": self.features0.kp,
            "des0": self.features0.des,
            "kp1": self.features1.kp,
            "des1": self.features1.des,
        }
        for features in [f_hc, f]:
            for method in ["good", "cross", "top"]:
                base_transform, all_matches, inliers = self.get_ransac_transform(
                    features=features, method=method
                )
                if not discardTransform(
                    base_transform.M,
                    max_rotation_deg=self.max_rotation_deg,
                    max_scale=self.max_scale,
                ):
                    return base_transform, all_matches, inliers
        raise ValueError("Failed to find valid base transform")

    def run(self):
        try:
            with self.timing("get_ransac_transform"):
                base_transform, all_matches, inliers = self._find_base_transform()

                self.base_transform = base_transform
                self.all_matches = all_matches
                self.inliers = inliers
                matches = [all_matches[i] for i in np.where(inliers)[0]]
        except Exception:
            return ProjectiveTransform(np.eye(3))

        with self.timing("apply_refine"):
            max_feature_distance = max(m.distance for m in matches)

            matches, transform = self.apply_refine(max_feature_distance, base_transform)

        self.final_matches = matches

        n = len(matches)
        if self.quadratic and n >= 20:
            with self.timing("get_quadratic_fit"):
                parabolic_transform = self.get_quadratic_fit(transform)
                transform = CompositeTransform([transform, parabolic_transform])

        return simplify_transforms(
            [
                ProjectiveTransform(
                    self.preprocess_result0.M
                ),  # preprocessing transform
                transform,  # actual registration
                # inverse preprocessing
                ProjectiveTransform(np.linalg.inv(self.preprocess_result1.M)),
            ]
        )

    def apply_refine(self, max_feature_distance, transform):
        n = 0
        while True:
            matches, transform = self.refine_transform(
                transform, max_feature_distance
            )
            n_new = len(matches)
            if n_new <= n:
                break
            n = n_new

        return matches, transform

    def extract_keypoints_with(self, detector, image, mask):
        """Return `(keypoints, descriptors)` using `detector` on `image` (or list)."""
        if isinstance(image, list):
            kp = []
            des = []
            for im in image:
                k, d = detector.detectAndCompute(im, mask=mask)
                if k is not None and len(k) > 0:
                    kp.extend(k)
                    if d is not None and len(d) > 0:
                        des.extend(d)
            return kp, (np.array(des) if len(des) > 0 else None)
        else:
            return detector.detectAndCompute(image, mask=mask)

    def get_ransac_transform(
        self, features, method="cross", ratio_threshold=0.75, k=3, n_matches=1000
    ):
        des0, des1 = features["des0"], features["des1"]
        if des0 is None or des1 is None:
            raise ValueError("Missing descriptors for RANSAC transform")

        used_matches = self._get_matches(
            features["des0"], features["des1"], method, ratio_threshold, k, n_matches
        )

        if len(used_matches) < 3:
            raise ValueError("Insufficient matches for affine estimation")

        points0 = np.array([features["kp0"][m.queryIdx].pt for m in used_matches])
        points1 = np.array([features["kp1"][m.trainIdx].pt for m in used_matches])
        A, mask = cv2.estimateAffinePartial2D(
            points0,
            points1,
            cv2.RANSAC,
            ransacReprojThreshold=self.ransacReprojThreshold,
        )
        if A is None:
            raise ValueError("Affine estimation failed")
        M = np.vstack([A, [0, 0, 1]])
        try:
            transform = ProjectiveTransform(M)
        except np.linalg.LinAlgError:
            raise ValueError("Unable to estimate affine transform")
        return transform, used_matches, mask

    def _get_matches(self, des0, des1, method, ratio_threshold, k, n_matches):
        """Get descriptor matches by `method` (cross|good|top)."""
        if method == "cross":
            bf = cv2.BFMatcher(crossCheck=True)
            return bf.match(des0, des1)
        elif method == "good":
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(des0, des1, k=2)
            return [m for m, n in matches if m.distance < ratio_threshold * n.distance]
        elif method == "top":
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(des0, des1, k=k)
            all_matches = [m for ms in matches for m in ms]
            return sorted(all_matches, key=lambda x: x.distance)[:n_matches]

    def get_quadratic_fit(self, base_transform):
        """Fit quadratic residual on inliers and return `Polynomial2DTransform`."""

        # src/dst for quadratic fit from refinement features
        src = np.array([self.features0.kp[m.queryIdx].pt for m in self.final_matches])
        dst = np.array([self.features1.kp[m.trainIdx].pt for m in self.final_matches])

        src_mapped = base_transform.apply(src)
        dx, dy = (src_mapped - dst).T

        X_poly = PolynomialFeatures(degree=2).fit_transform(src_mapped)

        model_dx = LinearRegression().fit(X_poly, dx)
        model_dy = LinearRegression().fit(X_poly, dy)

        return Polynomial2DTransform(model_dx, model_dy, degree=2)

    def refine_transform(self, base_transform, max_feature_distance):
        """Refine `base_transform` by spatial search + descriptor gating."""
        # Extract points (dense 0.05-contrast set) and map source through the current transform
        src_points = np.array([kp.pt for kp in self.features0.kp])
        dst_points = np.array([kp.pt for kp in self.features1.kp])

        mapped_src_points = base_transform.apply(src_points)

        # Spatial neighbor search around mapped source points
        if len(dst_points) == 0:
            return [], base_transform
        neighbor_index = NearestNeighbors(n_neighbors=min(self.n_neighbors, len(dst_points))).fit(dst_points)
        neighbor_distances, neighbor_indices = neighbor_index.kneighbors(
            mapped_src_points
        )

        matches = []
        src_inliers, dst_inliers = [], []
        max_dist_sq = max_feature_distance**2

        for src_idx in range(len(src_points)):
            # Filter neighbors by pixel distance and keypoint validity
            candidate_indices = [
                dst_idx
                for dist, dst_idx in zip(
                    neighbor_distances[src_idx], neighbor_indices[src_idx]
                )
                if dist < self.refineInlierThreshold
                and self.is_valid_match(self.features0.kp[src_idx], self.features1.kp[dst_idx])
            ]

            if not candidate_indices:
                continue

            # Choose the appearance-closest candidate by descriptor distance
            src_desc = self.features0.des[src_idx]
            candidate_descriptor_distances = [
                np.sum((src_desc - self.features1.des[dst_idx]) ** 2)
                for dst_idx in candidate_indices
            ]

            best_idx = int(np.argmin(candidate_descriptor_distances))
            best_dist = candidate_descriptor_distances[best_idx]

            # Enforce descriptor distance ceiling inherited from RANSAC-inliers
            if best_dist > max_dist_sq:
                continue

            best_dst_idx = candidate_indices[best_idx]
            matches.append(cv2.DMatch(src_idx, best_dst_idx, best_dist))
            src_inliers.append(src_points[src_idx])
            dst_inliers.append(dst_points[best_dst_idx])

        if len(src_inliers) < 4:
            return matches, base_transform

        refined_transform = approximate_projective_transform(src_inliers, dst_inliers)
        return matches, refined_transform

    def is_valid_match(self, k0, k1):
        """
        Checks if a pair of keypoints is a valid match based on certain criteria.

        Args:
            k0 (cv2.KeyPoint): Keypoint from the first image.
            k1 (cv2.KeyPoint): Keypoint from the second image.

        Returns:
            bool: True if the match is valid, False otherwise.
        """

        angle_diff = abs((k0.angle - k1.angle + 180) % 360 - 180)
        if angle_diff > self.max_rotation_deg:
            return False

        s_max, s_min = max(k0.size, k1.size), min(k0.size, k1.size)
        return s_max / s_min <= self.max_scale


def discardTransform(
    M,
    max_scale=1.5,
    max_aspect_ratio=1.2,
    max_rotation_deg=30.0,
    max_shear=0.05,
):
    """Return True if affine `M` is implausible (scale/anisotropy/rotation/shear checks)."""
    # Normalize input to 2x2 linear part A from M
    arr = np.array(M, dtype=float)
    if arr.shape == (3, 3):
        A = arr[:2, :2]
    elif arr.shape == (2, 3):
        A = arr[:2, :2]
    else:
        raise ValueError("discardTransform expects a 3x3 or 2x3 affine matrix M")

    # SVD-based polar decomposition: A = R * S, with R rotation and S symmetric PD
    U, singular_values, Vt = np.linalg.svd(A)
    R = U @ Vt
    # Ensure proper rotation (determinant +1)
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = U @ Vt

    # True rotation angle from R (radians)
    rot_angle = np.arctan2(R[1, 0], R[0, 0])
    if np.abs(rot_angle) > max_rotation_deg * (np.pi / 180.0):
        return True

    # Overall isotropic scale as mean singular value
    s_max = float(np.max(singular_values))
    s_min = float(np.min(singular_values))
    if s_min <= 0:
        return True
    s_iso = float(np.mean(singular_values))
    if s_iso < 1.0 / max_scale or s_iso > max_scale:
        return True

    # Anisotropy (scale similarity) via singular value ratio
    anisotropy = s_max / s_min
    if anisotropy > max_aspect_ratio:
        return True

    # Shear: deviation of the symmetric stretch tensor from isotropy
    S_tensor = Vt.T @ np.diag(singular_values) @ Vt
    shear_norm = np.linalg.norm(S_tensor - s_iso * np.eye(2), ord="fro") / s_iso
    if shear_norm > max_shear:
        return True

    # Translation bounds could be added here if desired
    return False
