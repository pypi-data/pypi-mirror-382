"""
Module containing the CFIBounds class for calculating and manipulating bounds of a color fundus image.

Classes:
- CFIBounds: Represents the bounds, including a circle and lines.
"""

from abc import ABC, abstractmethod
from functools import cached_property, lru_cache

import numpy as np
from scipy.ndimage import gaussian_filter

from rtnls_registration.transformation import ProjectiveTransform, exact_affine_coefficients, get_affine_transform
from rtnls_registration.utils import to_uint8


class BoundsBase(ABC):
    def __init__(self, image):
        self.image = image

    @abstractmethod
    def warp(self, transform, out_size=None):
        pass

    @abstractmethod
    def crop(self, target_diameter):
        pass

    @abstractmethod
    def make_binary_mask(self, **kwargs):
        pass

    @abstractmethod
    def make_mirrored_image(self, image=None, **kwargs):
        pass



class RectBounds(BoundsBase):
    def __init__(self, image, x_min, x_max, y_min, y_max):
        super().__init__(image)
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def warp(self, transform, out_size=None):
        if out_size is None:
            w, h = transform.get_dsize(self.image, None)
            out_size = (h, w)

        image_warped = transform.warp(self.image, out_size=out_size)
        x_min_warped, y_min_warped = transform.apply([[self.x_min, self.y_min]])[0]
        x_max_warped, y_max_warped = transform.apply([[self.x_max, self.y_max]])[0]
        return RectBounds(
            image_warped, x_min_warped, x_max_warped, y_min_warped, y_max_warped
        )

    def crop(self, target_diameter):
        h, w = self.image.shape[:2]
        pts_target = np.array(
            [[0, 0], [0, target_diameter], [target_diameter, target_diameter]]
        )
        pts_orig = np.array(
            [
                [self.x_min, self.y_min],
                [self.x_min, self.y_max],
                [self.x_max, self.y_max],
            ]
        )
        
        a, b, c, d, e, f = exact_affine_coefficients(pts_orig, pts_target)
        M = np.array([[a, b, c], [d, e, f], [0, 0, 1]])
        T = ProjectiveTransform(M)
        
        return T, self.warp(T, out_size=(target_diameter, target_diameter))

    def make_binary_mask(self):
        h, w = self.image.shape[:2]
        mask = np.zeros((h, w), dtype=bool)
        mask[int(self.y_min):int(self.y_max), int(self.x_min):int(self.x_max)] = True
        return mask

    def make_mirrored_image(self, image=None):
        if image is None:
            image = self.image
        result = np.copy(image)
        h, w = result.shape[:2]
        y_min, y_max = int(self.y_min), int(self.y_max)
        x_min, x_max = int(self.x_min), int(self.x_max)
        
        result[:y_min] = result[2 * y_min - 1: y_min - 1: -1]
        result[y_max:] = result[y_max: 2 * y_max - h: -1]
        result[:, :x_min] = result[:, 2 * x_min - 1: x_min - 1: -1]
        result[:, x_max:] = result[:, x_max: 2 * x_max - w: -1]
        return result

class CFIBounds(BoundsBase):

    def __init__(self, image, cx, cy, radius, lines={}):
        """

        Args:
        - image: numpy array (h, w, rgb) uint8, representing the color fundus image.
        - cx: The x-coordinate of the center of the circle.
        - cy: The y-coordinate of the center of the circle.
        - radius: The radius of the circle.
        - lines: A dictionary containing the coordinates of lines (each line optional):
            - 'top': [(x0, y0), (x1, y1)]
            - 'bottom': [(x0, y0), (x1, y1)]
            - 'left': [(x0, y0), (x1, y1)]
            - 'right': [(x0, y0), (x1, y1)]
        """
        super().__init__(image)
        h, w = image.shape[:2]
        center = cx, cy
        self.h = h
        self.w = w
        self.cy = cy
        self.cx = cx
        self.radius = radius
        self.lines = lines
        self.min_y = max(0, int(np.floor(cy - radius)))
        self.max_y = min(h, int(np.ceil(cy + radius)))
        self.min_x = max(0, int(np.floor(cx - radius)))
        self.max_x = min(w, int(np.ceil(cx + radius)))

        def intersects(location):
            if location not in lines:
                return
            p0, p1 = lines[location]
            intersects = line_circle_intersection(p0, p1, center, radius)
            if len(intersects) == 2:
                return intersects

        # find intersection points of each line with circle
        # update min and max y and x values to represent the inscribed rectangle
        line_bottom = intersects('bottom')
        if line_bottom:
            ((_, y0), (_, y1)) = line_bottom
            self.max_y = min(self.max_y, int(np.floor(min(y0, y1))))
        line_top = intersects('top')
        if line_top:
            ((_, y0), (_, y1)) = line_top
            self.min_y = max(self.min_y, int(np.ceil(max(y0, y1))))

        line_left = intersects('left')
        if line_left:
            ((x0, _), (x1, _)) = line_left
            self.min_x = max(self.min_x, int(np.ceil(max(x0, x1))))
        line_right = intersects('right')
        if line_right:
            ((x0, _), (x1, _)) = line_right
            self.max_x = min(self.max_x, int(np.floor(min(x0, x1))))

    @cached_property
    def mask(self):
        return self.make_binary_mask()

    @cached_property
    def contrast_enhanced_2(self):
        # constrast enhanced with 2% of the radius
        return self.make_contrast_enhanced_res256(0.02)

    @cached_property
    def contrast_enhanced_5(self):
        # constrast enhanced with 5% of the radius
        return self.make_contrast_enhanced_res256(0.05)

    @cached_property
    def contrast_enhanced_10(self):
        # constrast enhanced with 10% of the radius
        return self.make_contrast_enhanced_res256(0.1)

    @cached_property
    def sharpened_5(self):
        return self.make_contrast_enhanced_res256(0.05, contrast_factor=2, sharpen=True)

    @cached_property
    def mirrored_image(self):
        return self.make_mirrored_image()

    def make_contrast_enhanced_res256(self, sigma_fraction, contrast_factor=4, sharpen=False):
        '''
        contrast enhance by blurring the image and subtracting 
        the blurred image from the original image

        works at a resolution of 256x256 (for speed)
        Args:
        - sigma_fraction: the fraction of the radius to use for the gaussian blur
        - contrast_factor: the factor to multiply the difference between the original and blurred image
        - sharpen: 
            True: sharpen the original image (difference with original), 
            False: contrast enhance (default)
        '''

        ce_resolution = 256
        T = self.get_cropping_transform(ce_resolution)
        bounds_warped = self.warp(T)
        image_warped = bounds_warped.mirrored_image / 255
        sigma_warped = sigma_fraction * bounds_warped.radius
        blurred_warped = gaussian_filter(
            image_warped, (sigma_warped, sigma_warped, 0))
        # blurred image at original resolution
        blurred = T.warp_inverse(blurred_warped, (self.h, self.w))
        ce = unsharp_masking(self.image / 255, blurred,
                             contrast_factor, sharpen)
        return to_uint8(ce)

    def contrast_enhance(self, sigma=None, contrast_factor=4):
        '''
        contrast enhance by blurring the image and subtracting 
        the blurred image from the original image

        For a faster implementation check make_contrast_enhanced_res256

        Args:
            - sigma: the standard deviation of the gaussian blur
            By default, sigma is set to 0.05 times the radius

        '''
        if sigma is None:
            sigma = 0.05 * self.radius
        image = self.mirrored_image / 255
        blurred = gaussian_filter(image, sigma=(sigma, sigma, 0))
        ce = unsharp_masking(image, blurred, contrast_factor)
        return to_uint8(ce)

    def make_binary_mask(self, shrink_ratio=0.01):
        """
        creates a binary image of the bounds (circle and rectangle)
        Does not (yet) include the lines (top, bottom, left, right)
        """
        _, _, r_squared_norm = self.get_coordinates(shrink_ratio)
        d = int(np.round(shrink_ratio * self.radius))

        mask = r_squared_norm < 1
        mask[:self.min_y+d] = False
        mask[self.max_y-d:] = False
        mask[:, :self.min_x+d] = False
        mask[:, self.max_x-d:] = False
        return mask

    @lru_cache(maxsize=1)
    def get_coordinates(self, shrink_ratio=0.01):
        '''
        Args:
        - shrink_ratio: the fraction of the radius to shrink the circle by

        Returns:
        - dx, dy: the x and y coordinates of the circle
        - r_squared_norm: the normalized squared distance from the center of the circle
        r_squared_norm is one at the circle outline
        '''
        dx = np.arange(self.w)[None, :] - self.cx
        dy = np.arange(self.h)[:, None] - self.cy

        r = (1 - shrink_ratio) * self.radius
        dx_norm = dx / r
        dy_norm = dy / r
        r_squared_norm = dx_norm**2 + dy_norm**2
        return dx, dy, r_squared_norm

    def make_mirrored_image(self, image=None, shrink_ratio=0.02):
        """
        mirrors pixels around the box and circle defined by bounds
        Can be used in combination with contrast_enhance to avoid the bright boundary around the rim
        """
        if image is None:
            image = self.image
        cy, cx = self.cy, self.cx
        h, w = self.h, self.w

        # start with a copy of the original image
        result = np.copy(image)

        # shrink by d pixels (to avoid artifacts at the boundary)
        d = int(np.round(shrink_ratio * self.radius))
        min_y, max_y = self.min_y + d, self.max_y - d
        min_x, max_x = self.min_x + d, self.max_x - d

        # below min_y mirrored to above min_y
        result[:min_y] = result[2 * min_y - 1: min_y - 1: -1]
        # above max_y mirrored to below max_y
        result[max_y:] = result[max_y: 2 * max_y - h: -1]

        # left of min_x mirrored to right of min_x
        result[:, :min_x] = result[:, 2 * min_x - 1: min_x - 1: -1]
        # right of max_x mirrored to left of max_x
        result[:, max_x:] = result[:, max_x: 2 * max_x - w: -1]

        dx, dy, r_squared_norm = self.get_coordinates(shrink_ratio)

        # pixels outside the circle
        mask_outside = r_squared_norm > 1
        y0, x0 = np.where(mask_outside)

        # scale factor to be applied to reflect coordinates in circle outline
        scale = 1 / r_squared_norm[mask_outside]

        # round to nearest pixel
        x1 = np.round(cx + dx[0, x0] * scale).astype(int)
        y1 = np.round(cy + dy[y0, 0] * scale).astype(int)
        x1 = np.clip(x1, 0, w - 1)
        y1 = np.clip(y1, 0, h - 1)

        # assing pixel values outside the circle their mirrored values
        result[y0, x0] = result[y1, x1]

        return result

    def get_cropping_transform(self, target_diameter, patch_size=None):
        '''
        Returns a transform that crops the bounds to a target diameter
        '''
        if patch_size is None:
            patch_size = target_diameter

        scale = target_diameter / (2 * self.radius)
        in_size = self.h, self.w
        center = self.cy, self.cx
        return get_affine_transform(in_size, patch_size, scale=scale, center=center)

    def warp(self, transform, out_size=None):
        cx_warped, cy_warped = transform.apply([[self.cx, self.cy]])[0]
        # radius_warped = self.radius * transform.scale
        r_warped_x, _ = transform.apply([[self.cx + self.radius, self.cy]])[0]
        _, r_warped_y = transform.apply([[self.cx, self.cy + self.radius]])[0]
        rx = np.abs(r_warped_x - cx_warped)
        ry = np.abs(r_warped_y - cy_warped)
        if (rx - ry) / np.mean([rx, ry]) > 0.01:
            print(f"Warning: Radius warped is not symmetric: {rx} != {ry}")
        radius_warped = np.mean([rx, ry])
        
        
        image_warped = transform.warp(self.image, out_size=out_size)
        lines_warped = {k: transform.apply(v) for k, v in self.lines.items()}
        return CFIBounds(image_warped, cx_warped, cy_warped, radius_warped, lines_warped)

    def crop(self, target_diameter):
        T = self.get_cropping_transform(target_diameter)
        return T, self.warp(T, out_size=(target_diameter, target_diameter))

    def _repr_markdown_(self):
        result = f"""
        #### CFIBounds:

        - Center: ({self.cx}, {self.cy})
        - Radius: {self.radius}
        - Top: {self.min_y}
        - Bottom: {self.max_y}
        - Left: {self.min_x}
        - Right: {self.max_x}
        """
        return result.strip()

    def plot(self):
        from matplotlib import pyplot as plt
        plt.imshow(self.image)
        plt.scatter(self.cx, self.cy, c='w', s=2)
        plt.gca().add_artist(plt.Circle((self.cx, self.cy), self.radius, fill=False, color='w'))
        for k in ['top', 'bottom', 'left', 'right']:
            if k in self.lines:
                p0, p1 = self.lines[k]
                plt.plot([p0[0], p1[0]], [p0[1], p1[1]], c='w')

        plt.xlim(0, self.w)
        plt.ylim(self.h, 0)
        plt.show()

    def to_dict(self):
        return {
            'center': (self.cx, self.cy),
            'radius': self.radius,
            'lines': {k: (v.tolist() if isinstance(v, np.ndarray) else list(v)) for k, v in self.lines.items()},
        }

    def to_list(self):
        result = [self.cx, self.cy, self.radius]
        for line in ['top', 'bottom', 'left', 'right']:
            if line in self.lines:
                (x0, y0), (x1, y1) = self.lines[line]
                result.extend([x0, y0, x1, y1])
            else:
                result.extend([None, None, None, None])
        return result

    list_names = ['cx', 'cy', 'radius', 'top_x0', 'top_y0', 'top_x1', 'top_y1',
                  'bottom_x0', 'bottom_y0', 'bottom_x1', 'bottom_y1',
                  'left_x0', 'left_y0', 'left_x1', 'left_y1',
                  'right_x0', 'right_y0', 'right_x1', 'right_y1']

    @classmethod
    def from_dict(cls, image, d):
        return CFIBounds(image, d['center'][0], d['center'][1], d['radius'], d['lines'])


def line_circle_intersection(P0, P1, C, r):
    # Convert inputs to numpy arrays for vector operations
    P0, P1, C = np.array(P0), np.array(P1), np.array(C)

    # Define the line as a vector equation
    d = P1 - P0

    # Coefficients for the quadratic equation
    a = d.dot(d)
    b = 2 * d.dot(P0 - C)
    c = P0.dot(P0) + C.dot(C) - 2 * P0.dot(C) - r**2

    # Calculate the discriminant
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        # The line and circle do not intersect
        return []
    else:
        # The line and circle intersect at one or two points
        sqrt_discriminant = np.sqrt(discriminant)
        t = [(-b + sqrt_discriminant) / (2*a),
             (-b - sqrt_discriminant) / (2*a)]
        return [P0 + ti*d for ti in t]


def unsharp_masking(image, blurred, contrast_factor=4, sharpen=False):
    if sharpen:
        return np.clip(contrast_factor * (image - blurred) + image, 0, 1)
    else:
        return np.clip(contrast_factor * (image - blurred) + 0.5, 0, 1)
