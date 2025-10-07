"""Color utils"""

import numpy as np

__all__ = ["hex_to_rgb", "rgb_to_hex", "rgb_arr_to_hex_list"]


def hex_to_rgb(value):
    """Express a hex string into rgb tuple/list."""
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_hex(rgb):
    """Express a rgb tuple/list into hex string."""
    return "#%02x%02x%02x" % rgb


def rgb_arr_to_hex_list(rgb_array):
    """Express a rgb array into hex string np array."""
    list_ = list()
    for rgb in rgb_array:
        list_.append(rgb_to_hex(tuple(rgb.tolist())))
    out = np.array(list_, dtype=np.bytes_)

    return out


def rgb_shade(rgb_array, dark_rgb, shade):
    """Shade an rgb array of colors.

    rgb_array: nparray of n colors
        shape(n, 3)
    dark_rgb: dark background
        tuble of 3 int in [0., 255]
    shade; array of n shades
        shape(n, 3) (floats in [-1, 1)
        shade = 1 : white
        shade = 0 : no_shading
        shade = -1 : back color

    Chage is done in places
    """

    light_rgb = np.array([255, 255, 255])
    dark_rgb = np.array(dark_rgb)

    light_ = np.clip(shade, 0.0, 1.0)
    dark_ = np.clip(shade, -1.0, 0.0)
    a = (dark_[:, np.newaxis] * rgb_array).astype(np.int64)

    out = np.array(rgb_array)
    out += (dark_[:, np.newaxis] * (rgb_array - dark_rgb[np.newaxis, :])).astype(
        np.int16
    )
    out += (light_[:, np.newaxis] * (light_rgb[np.newaxis, :] - rgb_array)).astype(
        np.int16
    )
    return out
