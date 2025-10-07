import numpy as np
import pydicom
from matplotlib import pyplot as plt
from PIL import Image

from rtnls_registration.evaluation import get_score
from rtnls_registration.transformation import get_affine_transform


def open_image(filename):
    try:
        return np.array(Image.open(filename))
    except:
        return pydicom.dcmread(filename, force=True).pixel_array


def get_gray_scale(array):
    assert array.dtype == np.uint8, f"Expected uint8, got {array.dtype}"
    if len(array.shape) == 3:
        return array[:, :, 1]  # green channel
    elif len(array.shape) == 2:
        return array
    else:
        raise ValueError("Unknown image format")


def rescale(image, resolution=1024):
    """
    Rescale image to resolution x resolution
    """
    h, w = image.shape[:2]
    in_size = h, w
    s = min(resolution / h, resolution / w)
    rotate = 0
    scale = s, s
    center = h // 2, w // 2
    init_transform = get_affine_transform(in_size, resolution, rotate, scale, center)
    im_scaled = init_transform.warp(image, out_size=(resolution, resolution))
    return init_transform, im_scaled


def to_uint8(image):
    image = np.clip(image, 0, 1)
    return (image * 255).astype(np.uint8)


def luminance(image):
    """
    Convert RGB image to grayscale using luminance
    """
    if image.ndim == 2:
        return image
    elif image.ndim == 3 and image.shape[2] == 3:
        return (
            image[:, :, 0] * 0.2989 + image[:, :, 1] * 0.5870 + image[:, :, 2] * 0.1140
        ).astype(np.uint8)
    else:
        raise ValueError("Unknown image format")


def normalize(image):
    """
    Normalize image to [0, 1]
    """
    return (image - image.min()) / (image.max() - image.min())

def get_red_blue(image0, image1):
    rb = np.zeros(image0.shape)
    lum0 = normalize(luminance(image0))
    lum1 = normalize(luminance(image1))
    rb[:, :, 0] = lum0
    rb[:, :, 1] = lum1
    rb[:, :, 2] = lum1
    return rb

def plot_matches(register, figsize=(8, 8)):
    fig, axes = plt.subplots(2, 1, figsize=figsize)

    # Use the function with your data
    matches = register.all_matches
    kp0 = register.features0.kp_hc
    kp1 = register.features1.kp_hc

    # Extract matched keypoint coordinates
    src_pts = np.array([kp0[m.queryIdx].pt for m in matches])
    dst_pts = np.array([kp1[m.trainIdx].pt for m in matches])

    inliers = register.inliers

    im0 = register.preprocess_result0.bounds.image[:, :, 1]
    im1 = register.preprocess_result1.bounds.image[:, :, 1]

    h0, w0 = im0.shape
    h1, w1 = im1.shape

    # Create side-by-side image
    combined_img = np.zeros((max(h0, h1), w0 + w1), dtype=np.uint8)
    combined_img[:h0, :w0] = im0
    combined_img[:h1, w0:] = im1

    # Display the combined image
    axes[0].imshow(combined_img, cmap="gray")
    axes[1].imshow(combined_img, cmap="gray")

    ax = axes[0]

    # Adjust destination points by adding width of first image for display
    dst_pts_adjusted = dst_pts.copy()
    dst_pts_adjusted[:, 0] += w0

    # Show inliers in green, outliers in red
    for i, (src_pt, dst_pt) in enumerate(zip(src_pts, dst_pts_adjusted)):
        if len(matches) > 1000 and not inliers[i]:
            continue
        color = "lime" if inliers[i] else "red"
        ax.plot(
            [src_pt[0], dst_pt[0]],
            [src_pt[1], dst_pt[1]],
            color,
            alpha=0.5,
            linewidth=1,
        )

    ax.set_title(f"Original matches ({len(src_pts)} pairs)")
    ax.axis("off")

    matched_ixs = set(m.queryIdx for m in matches)
    matched_pts = np.array([p.pt for i, p in enumerate(kp0) if i in matched_ixs])
    non_matched_pts = np.array(
        [p.pt for i, p in enumerate(kp0) if i not in matched_ixs]
    )
    ax.scatter(matched_pts[:, 0], matched_pts[:, 1], c="cyan", s=10, alpha=1)
    ax.scatter(non_matched_pts[:, 0], non_matched_pts[:, 1], c="blue", s=10, alpha=0.01)

    matched_ixs = set(m.trainIdx for m in matches)
    matched_pts = np.array([p.pt for i, p in enumerate(kp1) if i in matched_ixs])
    non_matched_pts = np.array(
        [p.pt for i, p in enumerate(kp1) if i not in matched_ixs]
    )
    ax.scatter(matched_pts[:, 0] + w0, matched_pts[:, 1], c="cyan", s=10, alpha=1)
    ax.scatter(
        non_matched_pts[:, 0] + w0, non_matched_pts[:, 1], c="blue", s=10, alpha=0.01
    )

    ax = axes[1]
    final_matches = register.final_matches
    kp0 = register.features0.kp
    kp1 = register.features1.kp
    src_pts = np.array([kp0[m.queryIdx].pt for m in final_matches])
    dst_pts = np.array([kp1[m.trainIdx].pt for m in final_matches])
    ax.imshow(combined_img, cmap="gray")
    ax.axis("off")
    ax.set_title(f"Final matches ({len(src_pts)} pairs)")
    alpha = 0.01
    for i, (src_pt, dst_pt) in enumerate(zip(src_pts, dst_pts)):
        ax.plot([src_pt[0], dst_pt[0] + w0], [src_pt[1], dst_pt[1]], "lime", alpha=alpha)

    ax.scatter(src_pts[:, 0], src_pts[:, 1], c="cyan", s=10, alpha=alpha)
    ax.scatter(dst_pts[:, 0] + w0, dst_pts[:, 1], c="cyan", s=10, alpha=alpha)

    plt.tight_layout()



def plot_points(item, query, refer, figsize=(8, 8)):
    transform = item["transform"]
    score = get_score(item)
    for k, v in score.items():
        print(f"{k:20}: {v:.3f}")
    
    refer_pts = item["refer_points"]
    query_pts_pred = transform.apply(item["query_points"])
    query_transformed = transform.warp(query, refer.shape[:2])

    fig, axes = plt.subplots(2, 2, figsize=figsize)
    for ax in axes.flatten():
        ax.axis("off")
    axes[0, 0].imshow(refer)
    axes[0, 1].imshow(query)
    
    red_blue = get_red_blue(refer, query_transformed)
    
    axes[1, 0].imshow(red_blue)
    axes[1, 1].imshow(refer, alpha=0.5)
    axes[1, 1].imshow(query_transformed, alpha=0.5)

    axes[1, 1].scatter(
        refer_pts[:, 0],
        refer_pts[:, 1],
        marker="o",
        facecolor="none",
        edgecolor="w",
        s=50,
        linewidth=1,
        label="Reference"
    )
    axes[1, 1].scatter(
        query_pts_pred[:, 0], query_pts_pred[:, 1], marker="x", c="w", s=50, linewidth=1, label="Query warped"
    )
    axes[1, 1].legend()
    distances = np.linalg.norm(refer_pts - query_pts_pred, axis=1)
    for i, distance in enumerate(distances):
        axes[1, 1].text(
            query_pts_pred[i, 0] + 50,
            query_pts_pred[i, 1],
            f"{distance:.2f}",
            c="w",
            fontsize=8,
        )
    plt.show()