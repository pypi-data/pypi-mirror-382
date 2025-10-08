"""

ensight .geo files loader:
==========================

Module reading ASCII geo files and returning numpy arrays.

"""

import numpy as np

__all__ = ["load_geo"]


def load_geo(geofile):
    """Read ascii geofiles.

    :param geofile: path to en Ensight .geo file

    Returns:
    --------
        out: dict with keys :

        out["conn"] = numpy floats (n,3), coordinates
        out["el_type"] = string, the type of element
        out[el_type] = numpy connectivity (m,v)

    """
    out = dict()
    with open(geofile, "r") as fin:
        geo_ = fin.readlines()

    raw_geo_str = " ".join([str_.strip() for str_ in geo_])
    raw_geo = raw_geo_str.split()
    # print(raw_geo)
    parts_index = list()
    for idx, item in enumerate(raw_geo):
        if item.startswith("part"):
            parts_index.append(idx)

    for i, _ in enumerate(parts_index):
        start = parts_index[i]
        part_name = raw_geo[start + 2]
        try:
            end = parts_index[i + 1]
            out[part_name] = read_part(raw_geo[start:end])
        except IndexError:
            out[part_name] = read_part(raw_geo[start:])
    return out


def read_coor(
    geo_list,
):
    """Read a table in geofile"""
    idx = geo_list.index("coordinates")
    len_ = int(geo_list[idx + 1])
    table_list = list()
    for coor_id in range(len_):
        table_list.append(float(geo_list[idx + 2 + coor_id]))
        table_list.append(float(geo_list[idx + 2 + coor_id + len_]))
        table_list.append(float(geo_list[idx + 2 + coor_id + len_ * 2]))
    table_np = np.reshape(np.array(table_list), (len_, 3))
    return table_np


def read_conn(geo_list, flag, chunk):
    """Read a table in geofile"""
    idx = geo_list.index(flag)
    len_ = int(geo_list[idx + 1])
    table_list = geo_list[idx + 2 : idx + 2 + chunk * len_]
    table_list = [int(item) - 1 for item in table_list]
    table_np = np.reshape(np.array(table_list), (len_, chunk))
    return table_np


def read_part(part_content):
    """Read a part in geo file"""
    out = dict()
    out["el_type"] = None
    out["coor"] = read_coor(part_content)
    elmt = "bar2"

    for elmt, nvtx in [
        ["point", 1],
        ["bar2", 2],
        ["tri", 3],
        ["tri3", 3],
        ["tria3", 3],
        ["quad4", 4],
    ]:
        if elmt in part_content:
            out[elmt] = read_conn(part_content, elmt, nvtx)
            out["el_type"] = elmt

    # fall back to points
    if out["el_type"] == None:
        out["el_type"] = "point"
        out["point"] = [(i,) for i in range(out["coor"].size)]

    return out
