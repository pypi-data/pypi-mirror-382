"""

e.ply  files loader:
==========================

Module reading ASCII .ply files and returning numpy arrays.

..warning:
    ok, I only implemented triangles here.
"""

import sys
import numpy as np

__all__ = ["load_ply"]


def load_ply(plyfile):
    """Read ascii plyfiles.

    :param plyfile: path to a .ply file

    Returns:
    --------
        out: dict with keys :

        out["conn"] = numpy floats (n,3), coordinates
        out["el_type"] = string, the type of element
        out[el_type] = numpy connectivity (m,v)

    """
    out = dict()
    with open(plyfile, "r") as fin:
        ply_ = [line.strip() for line in fin.readlines()]

    for i, line in enumerate(ply_):
        if line.startswith("element vertex"):
            vtx = int(line.split(" ")[-1])
        if line.startswith("element face"):
            elt = int(line.split(" ")[-1])
        if line.startswith("end_header"):
            start = i + 1

    out = {
        "plypart": {
            "el_type": "tri3",
            "coor": read_coor(ply_[start : start + vtx]),
            "tri3": read_conn(ply_[start + vtx : start + vtx + elt]),
        }
    }
    return out


def read_coor(ply_list):
    """Read a table in plyfile"""
    table_list = list()
    for line in ply_list:
        coor = [float(i) for i in line.split()[0:3]]
        table_list.append(coor)
    table_np = np.array(table_list)
    # print("shape coor:", table_np.shape)
    return table_np


def read_conn(ply_list):
    """Read a table in plyfile"""
    table_list = list()
    for line in ply_list:
        coor = [int(i) for i in line.split()[1:4]]
        table_list.append(coor)
    table_np = np.array(table_list)
    # print("shape conn:", table_np.shape)
    return table_np


if __name__ == "__main__":
    load_ply(sys.argv[1])
