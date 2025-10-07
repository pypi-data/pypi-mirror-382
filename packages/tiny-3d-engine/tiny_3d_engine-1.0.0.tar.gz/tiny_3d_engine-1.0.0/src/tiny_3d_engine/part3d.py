"""part3d generator

module to generat part3d 
"""

from typing import Tuple, List
from arnica.utils.vector_actions import renormalize, rotate_vect_around_axis
import numpy as np

__all__ = ["Part3D"]


def conn_flatten_to_edges(conn: List[Tuple[float]]) -> List[Tuple[float]]:
    new_conn = []
    for element in conn:
        if len(element) <= 2:
            new_conn.append(element)
        elif len(element) == 3:
            new_conn.append([element[0], element[1]])
            new_conn.append([element[1], element[2]])
            new_conn.append([element[2], element[0]])
        elif len(element) == 4:
            new_conn.append([element[0], element[1]])
            new_conn.append([element[1], element[2]])
            new_conn.append([element[2], element[3]])
            new_conn.append([element[3], element[0]])
        else:
            raise RuntimeError(f"Element {element} of size unexpected")
    return new_conn


class Part3D:
    """create a part3d object"""

    def __init__(self):
        """startup class"""
        self.points = list()
        self.conn = list()

    def _add_pt(self, pos0: Tuple[float]) -> int:
        if pos0 in self.points:
            next_ptid = self.points.index(pos0)
        else:
            self.points.append(pos0)
            next_ptid = len(self.points) - 1
        return next_ptid

    def _add_conn(self, conn: Tuple[int]):
        if self.conn:
            if len(self.conn[-1]) != len(conn):
                raise ValueError(
                    f"Cannot add a {len(conn)} pts connectivity to a {len(self.conn[-1])} pts part3d object"
                )

        if conn not in self.conn:
            self.conn.append(conn)

    def add_point(self, pos0: Tuple[float]):
        """Add a single point"""
        ptid = self._add_pt(pos0)

        self._add_conn((ptid,))

    def add_line(self, pos0: Tuple[float], pos1: Tuple[float], npts: int):
        """Add a line from pos0 to pos1"""
        from_ptid = self._add_pt(pos0)
        for i in range(0, npts - 1):
            p_t = tuple(
                pos0[j] + (pos1[j] - pos0[j]) * 1.0 * (i + 1) / (npts - 1)
                for j in range(3)
            )

            to_ptid = self._add_pt(p_t)
            self._add_conn((from_ptid, to_ptid))
            from_ptid = to_ptid

    def switch_to_edges(self):
        """Transform triangles and quads to edges"""
        self.conn = conn_flatten_to_edges(self.conn)

    def add_triangle(self, pos0: Tuple[float], pos1: Tuple[float], pos2: Tuple[float]):
        """Add a single triangle"""
        id0 = self._add_pt(pos0)
        id1 = self._add_pt(pos1)
        id2 = self._add_pt(pos2)
        self._add_conn((id0, id1, id2))

    def add_quad(
        self,
        pos0: Tuple[float],
        pos1: Tuple[float],
        pos2: Tuple[float],
        pos3: Tuple[float],
    ):
        """Add a quad, using two triangles"""
        id0 = self._add_pt(pos0)
        id1 = self._add_pt(pos1)
        id2 = self._add_pt(pos2)
        id3 = self._add_pt(pos3)
        self._add_conn((id0, id1, id2, id3))

    def add_parallelogram(
        self,
        pos0: Tuple[float],
        pos1: Tuple[float],
        pos2: Tuple[float],
        n_i: int = 2,
        n_j: int = 2,
    ):
        """Add a paralelogram made of quads"""
        pt0 = np.array(pos0)
        pt1 = np.array(pos1)
        pt2 = np.array(pos2)
        vec_i = pt1 - pt0
        vec_j = pt2 - pt0
        for i in range(n_i):
            for j in range(n_j):
                corner0 = pt0 + vec_i * (i / n_i) + vec_j * (j / n_j)
                corner1 = pt0 + vec_i * ((i + 1) / n_i) + vec_j * (j / n_j)
                corner2 = pt0 + vec_i * ((i + 1) / n_i) + vec_j * ((j + 1) / n_j)
                corner3 = pt0 + vec_i * (i / n_i) + vec_j * ((j + 1) / n_j)
                self.add_quad(
                    tuple(corner0),
                    tuple(corner1),
                    tuple(corner2),
                    tuple(corner3),
                )

    def add_plane(
        self,
        pos0: Tuple[float],
        normal: Tuple[float],
        ref_len: float,
        n_i: int = 2,
        n_j: int = 2,
    ):
        """Create a plane with the normal , the direction and a size"""

        nml = renormalize(np.array(normal))
        center = np.array(pos0)
        x_dir = np.array([1, 0, 0])
        if np.allclose(normal, x_dir):
            tg1 = np.array([0, 1, 0])
            tg2 = np.array([0, 0, 1])
        else:
            tg1 = renormalize(np.cross(nml, x_dir))
            tg2 = np.cross(nml, tg1)

        corner_0 = center - 0.5 * ref_len * tg1 - 0.5 * ref_len * tg2
        corner_1 = center - 0.5 * ref_len * tg1 + 0.5 * ref_len * tg2
        corner_2 = center + 0.5 * ref_len * tg1 - 0.5 * ref_len * tg2
        self.add_parallelogram(corner_0, corner_1, corner_2, n_i, n_j)

    def add_disc(
        self,
        pos0: Tuple[float],
        normal: Tuple[float],
        radius: float,
        inner_radius: float = None,
        n_0_1: int = 4,
        n_0_pi: int = 12,
    ):
        """Create a disc with the normal , the direction and a radius (or two)"""
        if inner_radius is None:
            inner_radius = radius / 100

        axis_vect = renormalize(np.array(normal))
        center = np.array(pos0)
        x_dir = np.array([1, 0, 0])
        if np.allclose(axis_vect, x_dir):
            tg1 = np.array([0, 1, 0])
        else:
            tg1 = renormalize(np.cross(axis_vect, x_dir))

        delta_angle = 360.0 / n_0_pi
        gen_vect = (center + tg1 * radius) - (center + tg1 * inner_radius)
        gen0 = center + tg1 * inner_radius
        for longi in range(n_0_1):
            corner0 = gen0 + gen_vect * (longi / (n_0_1))
            corner1 = gen0 + gen_vect * ((longi + 1) / (n_0_1))
            corner2 = center + rotate_vect_around_axis(
                corner1 - center, [axis_vect, delta_angle]
            )
            corner3 = center + rotate_vect_around_axis(
                corner0 - center, [axis_vect, delta_angle]
            )
            self.add_quad(
                tuple(corner0), tuple(corner1), tuple(corner2), tuple(corner3)
            )
            for azimuth in range(n_0_pi - 1):
                corner0 = center + rotate_vect_around_axis(
                    corner0 - center, [axis_vect, delta_angle]
                )
                corner1 = center + rotate_vect_around_axis(
                    corner1 - center, [axis_vect, delta_angle]
                )
                corner2 = center + rotate_vect_around_axis(
                    corner2 - center, [axis_vect, delta_angle]
                )
                corner3 = center + rotate_vect_around_axis(
                    corner3 - center, [axis_vect, delta_angle]
                )
                self.add_quad(
                    tuple(corner0), tuple(corner1), tuple(corner2), tuple(corner3)
                )

    def add_cartbox(
        self,
        pos0: Tuple[float],
        pos1: Tuple[float],
        n_i: int = 2,
        n_j: int = 2,
        n_k: int = 2,
    ):
        """add a cartesianbox from two corners"""
        pt0 = np.array(pos0)
        pt1 = np.array(pos1)
        extent_vect = pt1 - pt0
        i_extent_vect = np.array((extent_vect[0], 0, 0))
        j_extent_vect = np.array((0, extent_vect[1], 0))
        k_extent_vect = np.array((0, 0, extent_vect[2]))

        self.add_parallelogram(
            tuple(pt0),
            tuple(pt0 + i_extent_vect),
            tuple(pt0 + j_extent_vect),
            n_i=n_i,
            n_j=n_j,
        )
        self.add_parallelogram(
            tuple(pt0 + k_extent_vect),
            tuple(pt0 + i_extent_vect + k_extent_vect),
            tuple(pt0 + j_extent_vect + k_extent_vect),
            n_i=n_i,
            n_j=n_j,
        )

        self.add_parallelogram(
            tuple(pt0),
            tuple(pt0 + i_extent_vect),
            tuple(pt0 + k_extent_vect),
            n_i=n_i,
            n_j=n_k,
        )
        self.add_parallelogram(
            tuple(pt0 + j_extent_vect),
            tuple(pt0 + i_extent_vect + j_extent_vect),
            tuple(pt0 + k_extent_vect + j_extent_vect),
            n_i=n_i,
            n_j=n_k,
        )

        self.add_parallelogram(
            tuple(pt0),
            tuple(pt0 + j_extent_vect),
            tuple(pt0 + k_extent_vect),
            n_i=n_j,
            n_j=n_k,
        )
        self.add_parallelogram(
            tuple(pt0 + i_extent_vect),
            tuple(pt0 + j_extent_vect + i_extent_vect),
            tuple(pt0 + k_extent_vect + i_extent_vect),
            n_i=n_j,
            n_j=n_k,
        )

    def add_frustum(
        self,
        pos0: Tuple[float],
        pos1: Tuple[float],
        r_0: float,
        r_1: float,
        n_0_1: int = 4,
        n_0_pi: int = 12,
    ):
        """Add a quad, using two triangles"""
        pt0 = np.array(pos0)
        pt1 = np.array(pos1)
        axis_vect = renormalize(pt1 - pt0)
        if axis_vect[2] == 1.0:
            _ref = np.array((1.0, 0.0, 0.0))
        else:
            _ref = np.array((0.0, 0.0, 1.0))

        rad_vec = renormalize(np.cross(axis_vect, _ref))
        gen0 = pt0 + rad_vec * r_0
        gen1 = pt1 + rad_vec * r_1
        gen_vect = gen1 - gen0

        delta_angle = 360.0 / n_0_pi

        for longi in range(n_0_1):
            corner0 = gen0 + gen_vect * (longi / (n_0_1))
            corner1 = gen0 + gen_vect * ((longi + 1) / (n_0_1))
            corner2 = pt0 + rotate_vect_around_axis(
                corner1 - pt0, [axis_vect, delta_angle]
            )
            corner3 = pt0 + rotate_vect_around_axis(
                corner0 - pt0, [axis_vect, delta_angle]
            )
            self.add_quad(
                tuple(corner0), tuple(corner1), tuple(corner2), tuple(corner3)
            )

            for azimuth in range(n_0_pi - 1):
                corner0 = pt0 + rotate_vect_around_axis(
                    corner0 - pt0, [axis_vect, delta_angle]
                )
                corner1 = pt0 + rotate_vect_around_axis(
                    corner1 - pt0, [axis_vect, delta_angle]
                )
                corner2 = pt0 + rotate_vect_around_axis(
                    corner2 - pt0, [axis_vect, delta_angle]
                )
                corner3 = pt0 + rotate_vect_around_axis(
                    corner3 - pt0, [axis_vect, delta_angle]
                )
                self.add_quad(
                    tuple(corner0), tuple(corner1), tuple(corner2), tuple(corner3)
                )
