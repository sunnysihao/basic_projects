# _*_ coding=: utf-8 _*_
import numpy as np

def undistortion(image: np.ndarray, intrinsic: np.ndarray, d_coeffs: np.ndarray, method2=True):
    """
    :param image: (H, W, C)
    :param intrinsic: camera intrinsic, (3, 3)
    :param d_coeffs: distortion coefficients, (3, )
    :param method2:
    :return: undistorted image: (H, W, C)
    """
    H, W, C = image.shape

    # 1. build undistorted image uv coordinates
    us = np.arange(W).reshape(-1, 1).repeat(H, axis=1).flatten()
    vs = np.arange(H).reshape(1, -1).repeat(W, axis=0).flatten()
    uv_pinhole = np.stack([us, vs], axis=1)

    # 2. uv => point3d: (x, y, 1)
    f_uv = intrinsic[[0, 1], [0, 1]]
    c_uv = intrinsic[[0, 1], [2, 2]]

    xy = (uv_pinhole - c_uv) / f_uv

    # 3. point3d => fisheye camera image
    r = np.linalg.norm(xy, axis=1)
    if not method2:
        # 3.1 distortion: theta_d = theta(1 + k1*theta^2 + ...)
        theta = np.arctan2(r, 1)
        theta_powers = np.stack([
            np.power(theta, 2+i)
            for i in range(1, len(d_coeffs)*2, 2)
        ], axis=1)

        theta_d = theta_powers @ d_coeffs + theta
        xy_p = (theta_d / r)[:, None] * xy

    else:
        # 3.1 distortion: x_p = x(1 + k1*r^2 + ...)
        r_powers = np.stack([
            np.power(r, 2*i + 2)
            for i in range(len(d_coeffs))
        ], axis=1)

        xy_p = (r_powers @ d_coeffs + 1)[:, None] * xy

    # 3.2 project to image plane
    uv_fisheyey = (xy_p * f_uv + c_uv)
    uv_fisheyey = uv_fisheyey.round().astype(int)

    # 3.3 filter uvs that out of range
    mask = (
        (uv_fisheyey[:, 0] >= 0) & (uv_fisheyey[:, 0] < W) &
        (uv_fisheyey[:, 1] >= 0) & (uv_fisheyey[:, 1] < H)
    )
    uv_pinhole_v = uv_pinhole[mask]
    uv_fisheyey_v = uv_fisheyey[mask]

    # 4. build image
    undistorted_image = np.zeros((H, W, C), dtype=image.dtype)
    undistorted_image[uv_pinhole_v[:, 1], uv_pinhole_v[:, 0]] = image[uv_fisheyey_v[:, 1], uv_fisheyey_v[:, 0]]
    return undistorted_image