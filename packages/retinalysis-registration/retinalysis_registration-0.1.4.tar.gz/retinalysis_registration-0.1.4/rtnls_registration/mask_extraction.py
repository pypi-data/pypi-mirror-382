import cv2
import numpy as np
from scipy.ndimage import sobel
from sklearn.linear_model import RANSACRegressor

from rtnls_registration.cfi_bounds import CFIBounds, RectBounds
from rtnls_registration.circle_fit import circle_fit, find_circle
from rtnls_registration.utils import get_gray_scale, rescale

RESOLUTION = 256
CENTER = RESOLUTION // 2
MAX_R = RESOLUTION // 1.8
MIN_R = RESOLUTION // 4
INLIER_DIST_THRESHOLD = RESOLUTION // 256

# masks for the rectangular ROI
# to be used in combination with edge points to mask the 4 quadrants
r = np.arange(RESOLUTION)
q = RESOLUTION // 8
f = 0.3
rect_masks = {
    "bottom": (q < r) & (r < 3 * q),
    "top": (5 * q < r) & (r < 7 * q),
    "right": (r < (1 - f) * q) | (r > (7 + f) * q),
    "left": ((3 + f) * q < r) & (r < (5 - f) * q),
}
corner_mask = np.ones(RESOLUTION, dtype=bool)
for mask in rect_masks.values():
    corner_mask &= ~mask

# some constants used for shortest path calculation
n = RESOLUTION - MIN_R
COST_DIST = 0.01 * np.subtract.outer(np.arange(n), np.arange(n)) ** 2
th = np.arange(RESOLUTION) * 2 * np.pi / RESOLUTION
COST_TH = np.cos(th)
SIN_TH = np.sin(th)


ys, xs = np.mgrid[:RESOLUTION, :RESOLUTION] - ((RESOLUTION - 1) / 2)
r = np.sqrt(xs**2 + ys**2)
im_corners = r > 1.1 * (RESOLUTION / 2)


def shortest_path(edge_image_horizontal):
    # vertical cut through polar representation of the edges

    costs = np.copy(edge_image_horizontal)
    resolution = costs.shape[0]

    # Initialize the path array with zeros
    path = np.zeros_like(costs, dtype=int)

    for y in range(1, resolution):
        # Add the distance cost to the cost array and get the minimum and its index over the columns
        total_costs = costs[y - 1] + COST_DIST
        min_costs = np.min(total_costs, axis=1)
        min_indices = np.argmin(total_costs, axis=1)
        costs[y] += min_costs
        path[y] = min_indices

    # Find the pixel with the minimum cost in the last row
    min_index = np.argmin(costs[-1])

    # Backtrack to get the path
    actual_path = [min_index]
    for i in range(resolution - 2, -1, -1):
        min_index = path[i + 1, min_index]
        actual_path.append(min_index)

    # Reverse the path to get it from top to bottom
    return np.array(actual_path[::-1])


def get_edge_points(image):
    # convert to polar coordinates (with max radius MAX_R)
    polar_image = cv2.linearPolar(
        image, (CENTER, CENTER), MAX_R, cv2.WARP_FILL_OUTLIERS
    )
    # crop (assuming radius > MIN_R)
    edge_region = polar_image[:, MIN_R:]

    # horizontal edge detection
    gx = sobel(edge_region / edge_region.max(), 1)

    # cut a line from top to bottom with least cost
    p = shortest_path(gx)

    # convert back to cartesian coordinates
    radii = MIN_R + p
    r = MAX_R * radii / RESOLUTION
    xs = CENTER + r * COST_TH
    ys = CENTER + r * SIN_TH

    # return list of points [n = RESOLUTION] on the edge of the ROI
    return xs, ys


def find_line(pts_x, pts_y, random_state=42):
    # fit a line to the points using RANSAC

    ransac = RANSACRegressor(
        residual_threshold=INLIER_DIST_THRESHOLD, random_state=random_state
    )
    ransac.fit(pts_x.reshape(-1, 1), pts_y)
    a, b = ransac.estimator_.coef_[0], ransac.estimator_.intercept_

    inlier_mask = ransac.inlier_mask_

    xs = np.array([0, RESOLUTION])
    ys = a * xs + b
    pts = np.array([xs, ys]).T

    # return the line (p0, p1) and support fraction
    return pts, np.mean(inlier_mask)


def find_lines(xs, ys, random_state=42):
    result = {}
    for location in ["left", "right"]:
        mask = rect_masks[location]
        line, support = find_line(ys[mask], xs[mask], random_state=random_state)
        if support > 0.5:
            p0, p1 = line
            result[location] = p0[::-1], p1[::-1]
    for location in ["top", "bottom"]:
        mask = rect_masks[location]
        line, support = find_line(xs[mask], ys[mask], random_state=random_state)
        if support > 0.5:
            result[location] = line
    return result


def inverse_tranform(bounds, init_transform):
    result = {}
    if "center" in bounds:
        result["center"] = init_transform.apply_inverse([bounds["center"]])[0]
    if "radius" in bounds:
        result["radius"] = bounds["radius"] / init_transform.M[0, 0]

    for position in ("top", "bottom", "left", "right"):
        if position in bounds:
            result[position] = init_transform.apply_inverse(bounds[position])
    return result


def get_mask(image, random_state=42):
    image_gray = get_gray_scale(image)
    T0, image_scaled = rescale(image_gray, resolution=RESOLUTION)

    check_corners = image_scaled[im_corners]
    # heuristic to check if image has no ROI
    if check_corners.mean() > 10:
        result = {
            "top": [(0, 0), (RESOLUTION, 0)],
            "bottom": [(0, RESOLUTION), (RESOLUTION, RESOLUTION)],
            "left": [(0, 0), (0, RESOLUTION)],
            "right": [(RESOLUTION, 0), (RESOLUTION, RESOLUTION)],
        }
        return inverse_tranform(result, T0)
    xs, ys = get_edge_points(image_scaled)

    try:
        radius, center, inliers = find_circle(
            xs,
            ys,
            MIN_R,
            MAX_R,
            inlier_dist_threshold=INLIER_DIST_THRESHOLD,
            random_state=random_state,
        )
        circle_fraction = np.sum(inliers) / RESOLUTION
    except ValueError:
        circle_fraction = 0

    if circle_fraction > 0.85:
        # assume no rectangluar roi
        result = {}
    else:
        if circle_fraction < 0.3:
            # not enough inliers for circle fit
            # fit circle through corners only
            pts = np.array([xs[corner_mask], ys[corner_mask]]).T
            radius, center = circle_fit(pts)
            # compensate for soft edge
            radius = 0.95 * radius

        # find rectangular bounds
        result = find_lines(xs, ys, random_state=random_state)

    result["center"] = center
    result["radius"] = radius

    return inverse_tranform(result, T0)



def get_cfi_bounds(image):
    mask = get_mask(image)
    if "center" not in mask:
        x_min = mask["left"][0][0]
        x_max = mask["right"][0][0]
        y_min = mask["top"][0][1]
        y_max = mask["bottom"][0][1]
        return RectBounds(image, x_min, x_max, y_min, y_max)

    cx, cy = mask["center"]
    radius = mask["radius"]
    lines = {k: mask[k] for k in ["top", "bottom", "left", "right"] if k in mask}
    return CFIBounds(image, cx, cy, radius, lines)
