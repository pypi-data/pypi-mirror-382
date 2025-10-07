import cv2
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import PolynomialFeatures

from rtnls_registration.preprocess import preprocess
from rtnls_registration.timing import TimingStats, timing
from rtnls_registration.transformation import (
    CompositeTransform, ProjectiveTransform, Polynomial2DTransform,
    approximate_projective_transform,
    simplify_transforms)


class RegistrationSIFT:
    """
        Class for performing image registration using the Scale-Invariant Feature Transform (SIFT) algorithm.

        Args:
            refineInlierThreshold (float): The inlier threshold for refining the registration. Default is 5.
            n_neighbors (int): The number of nearest neighbors to consider for matching. Default is 10.
    """

    def __init__(self, **kwargs):
        self.refineInlierThreshold = kwargs.get("refineInlierThreshold", 10)
        self.n_neighbors = kwargs.get("n_neighbors", 10)
        self.quadratic = kwargs.get("quadratic", True)
        self.preprocess_args = kwargs.get("preprocess_args", {})
        if kwargs.get("mode", "default") == "fast":
            self.preprocess_args["sigma_min"] = 2.0
            self.preprocess_args["sigma_max"] = 2.0
        self.max_angle_difference = kwargs.get("max_angle_difference", 20)
        self.max_scale_difference = kwargs.get("max_scale_difference", 1.8)

        self.sift_01 = cv2.SIFT_create(contrastThreshold=0.1)
        self.sift_005 = cv2.SIFT_create(contrastThreshold=0.05)

        self.stats = TimingStats()
        self.timing = lambda name: timing(self.stats, name)

    def __call__(self, image0, image1):
        """
        Register two retinal images using the SIFT algorithm. Applies preprocessing to both images

        Args:
            image0 (ndarray): The first retinal image.
            image1 (ndarray): The second retinal image.

        Returns:
            CompositeTransform: The transformation that aligns image0 to image1.
        """

        self.set_reference(image0)
        self.set_target(image1)

        return self.run()

    def set_reference(self, image):
        self._set_image(image, 0)
        self._init_keypoints(0)

    def set_target(self, image):
        self._set_image(image, 1)
        self._init_keypoints(1)

    def _init_keypoints(self, suffix):
        with self.timing(f"extract_keypoints_{suffix}"):
            vessels = getattr(self, f"vessels{suffix}")
            mask = getattr(self, f"mask{suffix}")
            kp_01, des_01 = self.extract_keypoints_with(self.sift_01, vessels[-1], mask)
            kp_005, des_005 = self.extract_keypoints_with(self.sift_005, vessels, mask)

            setattr(self, f"kp{suffix}_01", kp_01)
            setattr(self, f"des{suffix}_01", des_01)
            setattr(self, f"kp{suffix}_005", kp_005)
            setattr(self, f"des{suffix}_005", des_005)


    def _set_image(self, image, suffix):
        with self.timing(f"preprocess_image{suffix}"):
            M, bounds, vessels, mask = preprocess(image, **self.preprocess_args)

            setattr(self, f"M{suffix}", M)
            setattr(self, f"bounds{suffix}", bounds)
            setattr(self, f"vessels{suffix}", vessels)
            setattr(self, f"mask{suffix}", mask)

    def run(self):
        with self.timing("get_ransac_transform"):
            base_transform, all_matches, inliers = self.get_ransac_transform()
            self.base_transform = base_transform
            self.all_matches = all_matches
            self.inliers = inliers
            matches = [all_matches[i] for i in np.where(inliers)[0]]

        with self.timing("apply_refine"):
            max_feature_distance = max(m.distance for m in matches)
            matches, transform = self.apply_refine(
                max_feature_distance, base_transform
            )
        
        self.final_matches = matches

        src = np.array([self.kp0_005[m.queryIdx].pt for m in matches])
        dst = np.array([self.kp1_005[m.trainIdx].pt for m in matches])

        
        n = len(matches)
        if self.quadratic and n >= 20:
            with self.timing("get_quadratic_fit"):
                parabolic_transform = self.get_quadratic_fit(transform, src, dst)
                transform = CompositeTransform([transform, parabolic_transform])

        return simplify_transforms(
            [
                ProjectiveTransform(self.M0),  # preprocessing transform
                transform,  # actual registration
                # inverse preprocessing
                ProjectiveTransform(np.linalg.inv(self.M1)),
            ]
        )

    def apply_refine(self, max_feature_distance, transform):
        n = 0
        while True:
            matches, transform = self.refine_transform(transform, max_feature_distance)
            n_new = len(matches)
            if n_new <= n:
                break
            n = n_new

        return matches, transform

    def extract_keypoints_with(self, detector, image, mask):
        """
        Extracts keypoints and descriptors from the given image using a provided SIFT detector.

        Args:
            image (numpy.ndarray or list): The input image or a list of images.
            mask (numpy.ndarray, optional): The optional mask to apply on the image(s).

        Returns:
            tuple: A tuple containing the keypoints and descriptors.
                - keypoints (list): A list of keypoints.
                - descriptors (numpy.ndarray): An array of descriptors.

        """
        if type(image) == list:
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

    def get_ransac_transform(self):
        # Use the robust 0.1-contrast SIFT features for initial matching
        des0 = self.des0_01
        des1 = self.des1_01
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des0, des1, k=2)

        good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

        points0 = np.array([self.kp0_01[m.queryIdx].pt for m in good_matches])
        points1 = np.array([self.kp1_01[m.trainIdx].pt for m in good_matches])
       
        A, mask = cv2.estimateAffinePartial2D(points0, points1, cv2.RANSAC, ransacReprojThreshold=10)
        M = np.vstack([A, [0, 0, 1]])
        try:
            transform = ProjectiveTransform(M)
        except np.linalg.LinAlgError:
            raise ValueError("Unable to estimate affine transform")
        return transform, good_matches, mask

    def get_quadratic_fit(self, base_transform, src, dst):
        """
        Calculates a quadratic fit for the residual to dst after applying base_transform to src.


        Parameters:
        - base_transform: The base transformation to apply to the source points.
        - src: The source points.
        - dst: The destination points.

        Returns:
            - Polynomial2DTransform: The quadratic (degree=2) polynomial transformation.
        """

        src_mapped = base_transform.apply(src)
        dx, dy = (src_mapped - dst).T

        X_poly = PolynomialFeatures(degree=2).fit_transform(src_mapped)

        model_dx = LinearRegression()
        model_dy = LinearRegression()
        model_dx.fit(X_poly, dx)
        model_dy.fit(X_poly, dy)

        return Polynomial2DTransform(model_dx, model_dy, degree=2)

    def refine_transform(self, base_transform, max_feature_distance):
        """
        Refines the given transform by finding more matches.

        Args:
            base_transform: The initial transform to be refined.
            max_feature_distance: The maximum feature distance allowed for a match.

        Returns:
            A tuple containing the matches found and the refined transform.
        """
        # Extract points (dense 0.05-contrast set) and map source through the current transform
        src_points = np.array([keypoint.pt for keypoint in self.kp0_005])
        dst_points = np.array([keypoint.pt for keypoint in self.kp1_005])

        pixel_distance_threshold = self.refineInlierThreshold
        mapped_src_points = base_transform.apply(src_points)

        # Spatial neighbor search around mapped source points
        neighbor_index = NearestNeighbors(n_neighbors=self.n_neighbors).fit(dst_points)
        neighbor_distances, neighbor_indices = neighbor_index.kneighbors(mapped_src_points)

        matches = []
        src_inliers = []
        dst_inliers = []
        max_feature_distance_squared = max_feature_distance ** 2

        for src_idx in range(len(src_points)):
            # Filter neighbors by pixel distance and keypoint validity
            candidate_indices = [
                dst_idx
                for dist, dst_idx in zip(neighbor_distances[src_idx], neighbor_indices[src_idx])
                if dist < pixel_distance_threshold
                and self.is_valid_match(self.kp0_005[src_idx], self.kp1_005[dst_idx])
            ]

            if not candidate_indices:
                continue

            # Choose the appearance-closest candidate by descriptor distance
            candidate_descriptor_distances = [
                np.sum((self.des0_005[src_idx] - self.des1_005[dst_idx]) ** 2)
                for dst_idx in candidate_indices
            ]

            best_candidate_index = int(np.argmin(candidate_descriptor_distances))
            best_descriptor_distance = candidate_descriptor_distances[best_candidate_index]

            # Enforce descriptor distance ceiling inherited from RANSAC-inliers
            if best_descriptor_distance > max_feature_distance_squared:
                continue

            best_dst_idx = candidate_indices[best_candidate_index]

            matches.append(cv2.DMatch(src_idx, best_dst_idx, best_descriptor_distance))
            src_inliers.append(src_points[src_idx])
            dst_inliers.append(dst_points[best_dst_idx])

        if len(src_inliers) < 4:
            # failed to refine
            print('failed to refine')
            print(len(src_inliers))
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

        angle_difference = abs((k0.angle - k1.angle + 180) % 360 - 180)

        if angle_difference > self.max_angle_difference:
            return False

        s0, s1 = max(k0.size, k1.size), min(k0.size, k1.size)
        if s0 / s1 > self.max_scale_difference:
            return False


        return True

def discardTransform(
    coefficients,
    max_scale=1.8,
    max_aspect_ratio=1.2,
    max_rotation=20.0 * (np.pi / 180.0),
    max_shear=0.05,
    # max_translation=(700, 400),
):
    """
    Discard non-rigid/implausible affine transforms using polar decomposition.

    Parameters
    - coefficients: [a, b, tx, c, d, ty] affine coefficients
    - max_scale: allowable bound on overall isotropic scale (mean singular value)
    - max_aspect_ratio: allowable anisotropy (ratio of largest/smallest singular value)
    - max_rotation: maximum allowed rotation (radians)
    - max_shear: allowable normalized deviation of stretch tensor from isotropy
    """
    a, b, tx, c, d, ty = coefficients
    A = np.array([[a, b], [c, d]], dtype=float)

    # SVD-based polar decomposition: A = R * S, with R rotation and S symmetric PD
    U, singular_values, Vt = np.linalg.svd(A)
    R = U @ Vt
    # Ensure proper rotation (determinant +1)
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = U @ Vt

    # True rotation angle from R (radians)
    rot_angle = np.arctan2(R[1, 0], R[0, 0])
    if np.abs(rot_angle) > max_rotation:
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
