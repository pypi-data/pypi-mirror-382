"""
Robust affine transform estimation using deterministic triplet iteration.

This module provides functionality to estimate affine transforms from feature matches
by iterating through match triplets (ordered by quality) and refining candidates
with supporting matches.
"""

import cv2
import numpy as np
from sklearn.neighbors import NearestNeighbors


def get_affine_from_triplet(src_pts, dst_pts):
    """
    Compute affine transform from 3 point correspondences.
    
    Args:
        src_pts: Array of shape (3, 2) - source points
        dst_pts: Array of shape (3, 2) - destination points
    
    Returns:
        affine_matrix: 2x3 affine transformation matrix
    """
    # Build linear system: [x', y', 1]^T = A @ [x, y, 1]^T
    # We need to solve for 6 unknowns (a, b, tx, c, d, ty)
    A_matrix = np.zeros((6, 6))
    b_vector = np.zeros(6)
    
    for i in range(3):
        x, y = src_pts[i]
        x_prime, y_prime = dst_pts[i]
        
        # Equation for x': x' = a*x + b*y + tx
        A_matrix[2*i, :] = [x, y, 1, 0, 0, 0]
        b_vector[2*i] = x_prime
        
        # Equation for y': y' = c*x + d*y + ty
        A_matrix[2*i+1, :] = [0, 0, 0, x, y, 1]
        b_vector[2*i+1] = y_prime
    
    # Solve for [a, b, tx, c, d, ty]
    coeffs = np.linalg.solve(A_matrix, b_vector)
    
    # Return as 2x3 affine matrix
    return np.array([[coeffs[0], coeffs[1], coeffs[2]],
                     [coeffs[3], coeffs[4], coeffs[5]]])


def validate_affine_transform(affine_matrix, 
                              max_rotation_deg=30, 
                              scale_range=(0.7, 1.3), 
                              scale_difference_threshold=0.15):
    """
    Validate affine transform based on geometric constraints using SVD decomposition.
    
    Uses polar decomposition via SVD to properly extract rotation and scale components,
    correctly handling shear and anisotropic transforms.
    
    Args:
        affine_matrix: 2x3 affine transformation matrix
        max_rotation_deg: Maximum allowed rotation in degrees
        scale_range: (min_scale, max_scale) tuple for allowed scale range
        scale_difference_threshold: Maximum allowed difference between x and y scales
    
    Returns:
        tuple: (is_valid, scale_x, scale_y, rotation_deg, determinant)
    """
    a, b = affine_matrix[0, 0], affine_matrix[0, 1]
    c, d = affine_matrix[1, 0], affine_matrix[1, 1]
    
    # Build 2x2 linear transformation matrix
    A = np.array([[a, b], [c, d]], dtype=float)
    
    # Check for flipping (determinant should be positive)
    det = np.linalg.det(A)
    if det <= 0:
        return False, None, None, None, det
    
    # SVD-based polar decomposition: A = R * S
    # where R is rotation and S contains scale information
    U, singular_values, Vt = np.linalg.svd(A)
    R = U @ Vt
    
    # Ensure proper rotation (determinant +1)
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = U @ Vt
    
    # Extract rotation angle from R
    rotation_rad = np.arctan2(R[1, 0], R[0, 0])
    rotation_deg = float(np.degrees(rotation_rad))
    
    # Singular values are the true scales
    scale_x = float(singular_values[0])
    scale_y = float(singular_values[1])
    
    # Check rotation constraint
    if abs(rotation_deg) > max_rotation_deg:
        return False, scale_x, scale_y, rotation_deg, det
    
    # Check if scales are positive and in reasonable range
    if scale_x <= 0 or scale_y <= 0:
        return False, scale_x, scale_y, rotation_deg, det
    
    if scale_x < scale_range[0] or scale_x > scale_range[1]:
        return False, scale_x, scale_y, rotation_deg, det
    
    if scale_y < scale_range[0] or scale_y > scale_range[1]:
        return False, scale_x, scale_y, rotation_deg, det
    
    # Check if scales are close to each other (anisotropy check)
    scale_ratio = max(scale_x, scale_y) / min(scale_x, scale_y)
    if (scale_ratio - 1) > scale_difference_threshold:
        return False, scale_x, scale_y, rotation_deg, det
    
    return True, scale_x, scale_y, rotation_deg, det


def find_candidate_transforms(kp0, kp1, matches, n_candidates=3, 
                             max_rotation_deg=30,
                             scale_range=(0.7, 1.3),
                             scale_difference_threshold=0.15,
                             max_top_matches=50,
                             max_attempts=1000,
                             verbose=True):
    """
    Find candidate affine transforms by randomly sampling triplets from best matches.
    
    Args:
        kp0: List of cv2.KeyPoint for source image
        kp1: List of cv2.KeyPoint for destination image
        matches: List of cv2.DMatch (may contain multiple dst per src)
        n_candidates: Number of candidate transforms to find
        max_rotation_deg: Maximum allowed rotation in degrees
        scale_range: (min_scale, max_scale) tuple for allowed scale range
        scale_difference_threshold: Maximum allowed difference between x and y scales
        max_top_matches: Consider only the best N matches for sampling
        max_attempts: Maximum number of random triplet samples to try
        verbose: Print progress information
    
    Returns:
        list of candidate dicts, each containing:
            - affine_matrix: 2x3 affine transformation
            - triplet_indices: (i, j, k) indices of triplet
            - scale_x, scale_y, rotation_deg, determinant: transform properties
    """
    candidates = []
    n_matches = len(matches)
    
    if n_matches < 3:
        raise ValueError(f"Need at least 3 matches, got {n_matches}")
    
    # Sort matches by descriptor distance (ascending)
    matches_sorted = sorted(matches, key=lambda m: m.distance)
    
    # Limit to best matches for efficiency and quality
    n_top = min(max_top_matches, n_matches)
    top_matches = matches_sorted[:n_top]
    
    if verbose and n_top < n_matches:
        print(f"Sampling from top {n_top} matches (out of {n_matches})")
    
    # Pre-extract point arrays for efficiency
    def pt_from_kp_pair(m):
        return np.array(kp0[m.queryIdx].pt, dtype=float), np.array(kp1[m.trainIdx].pt, dtype=float)

    # Randomly sample triplets
    np.random.seed(42)  # For reproducibility
    attempts = 0
    
    while len(candidates) < n_candidates and attempts < max_attempts:
        attempts += 1
        
        # Randomly select 3 matches (distinct by src and by dst)
        indices = np.random.choice(n_top, size=3, replace=False)
        m0, m1, m2 = top_matches[indices[0]], top_matches[indices[1]], top_matches[indices[2]]
        
        # Enforce distinct src and distinct dst to avoid degeneracy
        src_ids = {m0.queryIdx, m1.queryIdx, m2.queryIdx}
        dst_ids = {m0.trainIdx, m1.trainIdx, m2.trainIdx}
        if len(src_ids) < 3 or len(dst_ids) < 3:
            continue
        
        # Build triplet point arrays
        src0, dst0 = pt_from_kp_pair(m0)
        src1, dst1 = pt_from_kp_pair(m1)
        src2, dst2 = pt_from_kp_pair(m2)
        triplet_src = np.vstack([src0, src1, src2])
        triplet_dst = np.vstack([dst0, dst1, dst2])
        
        # Check if points are not collinear (would make affine singular)
        # Use cross product to check collinearity
        v1 = triplet_src[1] - triplet_src[0]
        v2 = triplet_src[2] - triplet_src[0]
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        if abs(cross) < 1e-6:  # Nearly collinear
            continue
        
        try:
            # Compute affine transform
            affine_matrix = get_affine_from_triplet(triplet_src, triplet_dst)
            
            # Validate transform
            is_valid, scale_x, scale_y, rotation, det = validate_affine_transform(
                affine_matrix,
                max_rotation_deg=max_rotation_deg,
                scale_range=scale_range,
                scale_difference_threshold=scale_difference_threshold
            )
            
            if is_valid:
                candidates.append({
                    'affine_matrix': affine_matrix,
                    'triplet_matches': (m0, m1, m2),
                    'scale_x': scale_x,
                    'scale_y': scale_y,
                    'rotation_deg': rotation,
                    'determinant': det
                })
                if verbose:
                    print(f"Found candidate {len(candidates)}: src_ids={list(src_ids)}, dst_ids={list(dst_ids)}, "
                          f"scale_x={scale_x:.3f}, scale_y={scale_y:.3f}, "
                          f"rotation={rotation:.2f}°")
                    
        except (np.linalg.LinAlgError, ValueError):
            continue
    
    if verbose and len(candidates) < n_candidates:
        print(f"Warning: Only found {len(candidates)} candidates after {attempts} attempts")
    
    return candidates


def refine_candidate_transform(candidate_affine, 
                               src_pts, dst_pts, 
                               des0, des1,
                               max_feature_distance,
                               pixel_distance_threshold=10,
                               n_neighbors=10):
    """
    Refine a candidate transform by finding supporting matches.
    Similar to Registration.refine_transform method.
    
    Args:
        candidate_affine: 2x3 affine matrix to refine
        src_pts: All source points (N, 2)
        dst_pts: All destination points (M, 2)
        des0: Descriptors for source points (N, D)
        des1: Descriptors for destination points (M, D)
        max_feature_distance: Maximum descriptor distance for matches
        pixel_distance_threshold: Maximum pixel distance for spatial matching
        n_neighbors: Number of neighbors to consider
    
    Returns:
        tuple: (refined_affine_matrix, supporting_match_indices, num_inliers)
            - refined_affine_matrix: 2x3 refined affine matrix
            - supporting_match_indices: list of (src_idx, dst_idx) tuples
            - num_inliers: number of supporting matches
    """
    # Convert 2x3 affine to 3x3 for transformation
    M = np.vstack([candidate_affine, [0, 0, 1]])
    
    # Map source points through current transform
    src_homogeneous = np.hstack([src_pts, np.ones((len(src_pts), 1))])
    mapped_src_pts = (M @ src_homogeneous.T).T[:, :2]
    
    # Find nearest neighbors in destination space
    neighbor_index = NearestNeighbors(n_neighbors=min(n_neighbors, len(dst_pts))).fit(dst_pts)
    neighbor_distances, neighbor_indices = neighbor_index.kneighbors(mapped_src_pts)
    
    # Collect supporting matches
    supporting_indices = []
    src_inliers = []
    dst_inliers = []
    max_feature_distance_squared = max_feature_distance ** 2
    
    for src_idx in range(len(src_pts)):
        # Filter neighbors by pixel distance
        candidate_indices = [
            dst_idx
            for dist, dst_idx in zip(neighbor_distances[src_idx], neighbor_indices[src_idx])
            if dist < pixel_distance_threshold
        ]
        
        if not candidate_indices:
            continue
        
        # Choose best by descriptor distance
        candidate_descriptor_distances = [
            np.sum((des0[src_idx] - des1[dst_idx]) ** 2)
            for dst_idx in candidate_indices
        ]
        
        best_candidate_idx = int(np.argmin(candidate_descriptor_distances))
        best_descriptor_distance = candidate_descriptor_distances[best_candidate_idx]
        
        # Enforce descriptor distance threshold
        if best_descriptor_distance > max_feature_distance_squared:
            continue
        
        best_dst_idx = candidate_indices[best_candidate_idx]
        
        supporting_indices.append((src_idx, best_dst_idx))
        src_inliers.append(src_pts[src_idx])
        dst_inliers.append(dst_pts[best_dst_idx])
    
    num_inliers = len(src_inliers)
    
    if num_inliers < 6:  # Need at least 6 points for robust affine estimation
        return candidate_affine, supporting_indices, num_inliers
    
    # Re-estimate affine transform with all supporting matches
    src_inliers = np.array(src_inliers, dtype=np.float32)
    dst_inliers = np.array(dst_inliers, dtype=np.float32)
    
    # Use cv2 for robust estimation
    refined_affine, inlier_mask = cv2.estimateAffinePartial2D(
        src_inliers, dst_inliers, method=cv2.LMEDS
    )
    
    if refined_affine is None:
        return candidate_affine, supporting_indices, num_inliers
    
    # Filter supporting_indices based on inlier_mask
    if inlier_mask is not None:
        supporting_indices = [
            supporting_indices[i] 
            for i in range(len(supporting_indices)) 
            if inlier_mask[i]
        ]
        num_inliers = len(supporting_indices)
    
    return refined_affine, supporting_indices, num_inliers


def estimate_robust_affine(kp0, kp1, des0, des1, matches,
                           n_candidates=3,
                           max_rotation_deg=30,
                           scale_range=(0.7, 1.3),
                           scale_difference_threshold=0.15,
                           pixel_distance_threshold=10,
                           n_neighbors=10,
                           max_top_matches=100,
                           max_attempts=10000,
                           verbose=True):
    """
    Estimate robust affine transforms from keypoint matches.
    
    Main API function that takes keypoints, descriptors, and matches,
    and returns refined candidate affine transforms.
    
    Args:
        kp0: List of cv2.KeyPoint for source image
        kp1: List of cv2.KeyPoint for destination image
        des0: Descriptors for source keypoints (N, D)
        des1: Descriptors for destination keypoints (M, D)
        matches: List of cv2.DMatch objects (should be pre-filtered, e.g., by ratio test)
        n_candidates: Number of candidate transforms to find
        max_rotation_deg: Maximum allowed rotation in degrees
        scale_range: (min_scale, max_scale) tuple for allowed scale range
        scale_difference_threshold: Maximum allowed difference between x and y scales
        pixel_distance_threshold: Maximum pixel distance for spatial matching during refinement
        n_neighbors: Number of neighbors to consider during refinement
        max_top_matches: Consider only the best N matches for triplet sampling
        max_attempts: Maximum number of random triplet samples to try
        verbose: Print progress information
    
    Returns:
        list of refined candidate dicts, each containing:
            - affine_matrix: 2x3 refined affine transformation
            - n_inliers: number of supporting matches
            - supporting_matches: list of (src_idx, dst_idx) tuples
            - original_candidate: dict with initial triplet information
    """
    # Extract point correspondences from matches
    src_pts = np.array([kp0[m.queryIdx].pt for m in matches], dtype=np.float32)
    dst_pts = np.array([kp1[m.trainIdx].pt for m in matches], dtype=np.float32)
    
    # All keypoints and descriptors for refinement
    all_src_pts = np.array([kp.pt for kp in kp0], dtype=np.float32)
    all_dst_pts = np.array([kp.pt for kp in kp1], dtype=np.float32)
    
    if verbose:
        print(f"Finding {n_candidates} candidate transforms from {len(matches)} matches...")
    
    # Step 1: Find initial candidate transforms from triplets
    candidates = find_candidate_transforms(
        kp0, kp1, matches,
        n_candidates=n_candidates,
        max_rotation_deg=max_rotation_deg,
        scale_range=scale_range,
        scale_difference_threshold=scale_difference_threshold,
        max_top_matches=max_top_matches,
        max_attempts=max_attempts,
        verbose=verbose
    )
    
    if len(candidates) == 0:
        raise ValueError("No valid candidate transforms found")
    
    # Compute max feature distance from the input matches
    max_feature_distance = max(m.distance for m in matches)
    
    if verbose:
        print(f"\nRefining {len(candidates)} candidates...")
    
    # Step 2: Refine each candidate
    refined_candidates = []
    for i, candidate in enumerate(candidates):
        if verbose:
            print(f"\nRefining candidate {i+1}/{len(candidates)}...")
        
        refined_affine, supporting_matches, n_inliers = refine_candidate_transform(
            candidate['affine_matrix'],
            all_src_pts, all_dst_pts,
            des0, des1,
            max_feature_distance=max_feature_distance,
            pixel_distance_threshold=pixel_distance_threshold,
            n_neighbors=n_neighbors
        )
        
        if verbose:
            print(f"  Found {n_inliers} supporting matches")
        
        refined_candidates.append({
            'affine_matrix': refined_affine,
            'n_inliers': n_inliers,
            'supporting_matches': supporting_matches,
            'original_candidate': candidate
        })
    
    # Sort by number of inliers (descending)
    refined_candidates.sort(key=lambda x: x['n_inliers'], reverse=True)
    
    if verbose:
        print(f"\nBest candidate has {refined_candidates[0]['n_inliers']} inliers")
    
    return refined_candidates

