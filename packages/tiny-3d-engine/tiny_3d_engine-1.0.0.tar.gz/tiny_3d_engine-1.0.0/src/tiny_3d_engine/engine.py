"""
3D interaction engine
---------------------

This module load a **Scene3D** object, 
pass to a **ViewField** object** 
(i.e the coordinates of the scene transformed with
respect to the user POV),
and dialog with the **Screen** Object.

"""

import numpy as np
from tkinter import ttk, IntVar
from loguru import logger

from tiny_3d_engine.viewfield import ViewField
from tiny_3d_engine.screen import Screen
from tiny_3d_engine.scene3d import Scene3D
from tiny_3d_engine.color import hex_to_rgb, rgb_arr_to_hex_list, rgb_shade

__all__ = ["Engine3D"]

ROTATE_ANGLE = 33.333333333


class Engine3D:
    """3D engine.

    :param scene: scene to be loaded.

    :param root: Tk window to graft the engine

    :param width: integer in pix the view width.

    :param height: integer in pix the view height.

    :param shading: str. the shading (flat|radial|linear|none)

    :param background: str. the backgound color in Hex (#000000)

    :param title: the title of the engine window

    .. note:
        The engine does not render at startup.
        Use Engine3d.render() to get your image.

        The engine is not starting user interaction at startup.
        Use Engine3d.mainloop() to get the show running.

    """

    def __init__(
        self,
        scene: Scene3D = None,
        root: ttk.Frame = None,
        width: int = 1000,
        height: int = 700,
        shading: str = "flat",
        background: str = "#666699",
        title: str = "Tiny 3D Engine",
    ):
        """Startup class."""
        self.title = title
        self.shading = shading
        self.view = ViewField(width, height)
        self.screen = Screen(width, height, background, root=root, title=self.title)
        self.back_color = hex_to_rgb(background)
        self.scene = None
        self.screen.can.bind("<B1-Motion>", self.__drag)
        self.screen.can.bind("<ButtonRelease>", self.__resetDrag)
        self.screen.can.bind("<Shift-B1-Motion>", self.__shiftdrag)
        self.screen.can.bind("<Button-2>", self.__hide_by_tag)
        self.screen.can.bind("<Shift-Button-2>", self.__hide_by_tag_all)
        self.__dragprev = []

        # Define buttons replacing the Mac key bindings
        buttons = [
            ("Zoom In   ", self.__zoom_in),
            ("Zoom Out. ", self.__zoom_out),
            ("Fish In   ", self.__dist_in),
            ("Fish Out  ", self.__dist_out),
            ("Rot. Up   ", self.__rotate_up),
            ("Rot. Down ", self.__rotate_down),
            ("Rot. Left ", self.__rotate_left),
            ("Rot. Right", self.__rotate_right),
            ("Spin Clock", self.__spin_clockwise),
            ("Spin AntiC", self.__spin_anticlockwise),
            ("Reset All ", self._reset_view),
            ("Reset View", self._refocus),
            ("Chge Bkgd", self.__switchBackground),
        ]

        # Create and pack each button
        for label, command in buttons:
            b = ttk.Button(
                self.screen.control_panel, text=label, command=command, width=7
            )
            b.pack(side="top", padx=1, pady=1)

        self.autofit = IntVar()
        autofit = ttk.Checkbutton(
            self.screen.control_panel, text="autofit", variable=self.autofit, width=7
        )
        autofit.pack(side="top", padx=1, pady=1)

        if scene is not None:
            self.update(scene)

    def update(self, scene: Scene3D):
        """Update the scene to show."""
        if scene.is_void():
            self.scene = None
            self.clear()
        else:
            self.scene = scene
            self.conn = scene.conn()
            self.tags = scene.tags()
            self.screen.update(scene.colors())
            shade = self._compute_shade()
            self.shaded_colors = rgb_arr_to_hex_list(
                rgb_shade(self.scene.color_arrays(), self.back_color, shade)
            )
            self._reset_view()
            self.screen.add_tags_bindings(scene.parts())

    def rotate(self, axis: str, angle: float):
        """rotate model around axis"""
        if self.scene is not None:
            self.view.rotate(axis, angle)

    def translate(self, axis: str, angle: float):
        """rotate model around axis"""
        if self.scene is not None:
            self.view.translate(axis, angle)

    def render(self, motion: bool = False):
        """Render the viewfield on screen."""
        if self.scene is None:
            return

        # get elements in order from back to front
        # only if visible
        if motion:
            mask = self.mot_visible
        else:
            mask = self.stat_visible

        current_points = self.view.pts[self.conn[mask, 0], :]

        autofit = self.autofit.get() == 1
        if autofit:
            self.view.update(self.view.pts, mask=self.conn[mask, 0])
        ordered_z_indices = np.flip(
            #    np.argsort(self.view.pts[self.conn[mask, 0], 2])
            np.argsort(current_points[:, 2])
        )

        reordered_conn = self.conn[mask, :][ordered_z_indices]
        reordered_colors = self.shaded_colors[mask][ordered_z_indices]
        reordered_tags = self.tags[mask][ordered_z_indices]

        n_vertices = self.conn.shape[1]
        m_elements = ordered_z_indices.shape[0]

        # get the serie of polygons, in z order
        # store the shape of connectivity
        # calculate flattened coordinates (x_pix, y_pix)
        projxy = self.view.flatten(self.distance, self.scale)

        poly_coords = np.take(projxy, reordered_conn.ravel(), axis=0).reshape(
            m_elements, n_vertices, 2
        )

        for elmt, tag, color in zip(
            poly_coords.tolist(),
            reordered_tags.tolist(),
            reordered_colors.tolist(),
        ):
            # adujsting polyline to nb of vertices seem slower on my tests
            self.screen.createShape(
                elmt,
                tag,
                color,
            )

    def clear(self):
        """clear display"""
        self.screen.clear()

    def after(self, time, function):
        """call screen after() method, for animations"""
        self.screen.after(time, function)

    def mainloop(self):
        """call screen mainloop() method to stay interactive"""
        self.screen.mainloop()

    def dump(self, fname: str):
        """Dump the scene into a file."""
        if self.scene is not None:
            self.scene.dump(fname)
        else:
            raise ValueError("No scene to dump...")

    def _reset_view(self, all_visibles=True):

        if self.scene is not None:
            self.view.update(self.scene.points())

        if self.view.size is None:
            return
        self.scale = float(self.view.init_scale)
        self.distance = 64
        m_elements = self.conn.shape[0]

        rotate_max = 2000
        stat_max = 100000

        if all_visibles:
            self.mot_visible = np.full((m_elements), True)
            self.stat_visible = np.full((m_elements), True)

            if m_elements > rotate_max:
                p = rotate_max / m_elements
                self.mot_visible = np.random.choice(
                    a=[True, False], size=(m_elements), p=[p, 1 - p]
                )

            if m_elements > stat_max:
                p = stat_max / m_elements
                self.stat_visible = np.random.choice(
                    a=[True, False], size=(m_elements), p=[p, 1 - p]
                )

        self.clear()
        self.render()

    def _refocus(self):
        self._reset_view(all_visibles=False)

    def _compute_shade(self):
        """compute the shading of the scene"""
        light = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        norm = np.linalg.norm(light)
        light /= norm
        pts = self.scene.points()

        if self.conn.shape[1] < 3:
            logger.debug("No polygons, Switch to radial shading...")
            self.shading = "radial"

        if self.shading == "flat":
            vect1 = pts[self.conn[:, 1], :] - pts[self.conn[:, 0], :]
            vect2 = pts[self.conn[:, 2], :] - pts[self.conn[:, 1], :]
            normal = np.cross(vect1, vect2)
            norm = np.clip(np.linalg.norm(normal, axis=1), 1e-8, None)
            normal = normal / (norm[:, np.newaxis])
            align = np.dot(normal, light)
        elif self.shading == "linear":
            axis = np.dot(pts[self.conn[:, 0], :], light)
            align = 2.0 * (axis - axis.min()) / (axis.max() - axis.min()) - 1.0
        elif self.shading == "radial":
            radial = np.linalg.norm(pts[self.conn[:, 0], :] - light, axis=1)
            align = 2.0 * (radial - radial.min()) / (radial.max() - radial.min()) - 1.0
        elif self.shading == "none":
            align = np.zeros(self.conn.shape[0])
        elif self.shading == "gouraud":
            raise NotImplementedError(
                "As if I could implement gouraud shading from Tkinter!"
            )
        else:
            raise RuntimeError("Shading " + str(self.shading) + " not implemented")

        align *= 0.8
        return align

    def __drag(self, event):
        """handler for mouse drag event"""
        if self.__dragprev:  # and self.screen.motion_allowed:
            self.rotate("y", -(event.x - self.__dragprev[0]) / 3)
            self.rotate("x", -(event.y - self.__dragprev[1]) / 3)
            self.clear()
            self.render(motion=True)
        self.__dragprev = [event.x, event.y]

    def __shiftdrag(self, event):
        """handler for mouse drag event"""
        if self.__dragprev:  # and self.screen.motion_allowed:
            self.translate("x", -(event.x - self.__dragprev[0]) / 350)
            self.translate("y", -(event.y - self.__dragprev[1]) / 350)
            self.clear()
            self.render(motion=True)
        self.__dragprev = [event.x, event.y]

    def __resetDrag(self, event):
        """reset mouse drag handler"""
        self.__dragprev = []
        self.render()

    def __random_calback(self, event):
        """reset mouse drag handler"""
        print(event)

    def __hide_by_tag(self, event, hide_family: bool = False):
        """reset mouse drag handler"""
        if self.view.size is None:
            return

        tag = self.screen.current_tag
        if tag is not None:
            if hide_family:
                root = tag.split(".")[0]
                logger.warning(
                    f"Hiding tag '{tag}' and all its family '{root}'. Use 'Reset All' to show it back."
                )
                tohide = np.invert(np.char.startswith(self.tags, root))
            else:
                logger.warning(f"Hiding tag '{tag}'. Use 'Reset All' to show it back.")
                tohide = np.invert(np.char.equal(self.tags, tag))
            self.stat_visible = np.logical_and(self.stat_visible, tohide)
            self.mot_visible = np.logical_and(self.mot_visible, tohide)
            # self.screen.motion_allowed = True
            self.screen.current_tag = None
            self.screen.can.delete("info")
            self.clear()
            self.render()

    def __hide_by_tag_all(self, event):
        self.__hide_by_tag(event, hide_family=True)

    def __zoom_in(self):
        if self.view.size is None:
            return
        self.scale *= 1.2
        self.clear()
        self.render()

    def __zoom_out(self):
        if self.view.size is None:
            return
        if self.scale > 20:
            self.scale /= 1.2
        self.clear()
        self.render()

    def __dist_in(self):
        if self.view.size is None:
            return
        if self.distance > 2:
            self.distance /= 2
        self.clear()
        self.render()

    def __dist_out(self):
        if self.view.size is None:
            return
        if self.distance < 128:
            self.distance *= 2
        self.clear()
        self.render()

    def __rotate_left(self):
        if self.view.size is None:
            return
        self.rotate("y", ROTATE_ANGLE)
        self.clear()
        self.render()

    def __rotate_right(self):
        if self.view.size is None:
            return
        self.rotate("y", -ROTATE_ANGLE)
        self.clear()
        self.render()

    def __rotate_up(self):
        if self.view.size is None:
            return
        self.rotate("x", ROTATE_ANGLE)
        self.clear()
        self.render()

    def __rotate_down(self):
        if self.view.size is None:
            return
        self.rotate("x", -ROTATE_ANGLE)
        self.clear()
        self.render()

    def __spin_clockwise(self):
        if self.view.size is None:
            return
        self.rotate("z", ROTATE_ANGLE)
        self.clear()
        self.render()

    def __spin_anticlockwise(self):
        if self.view.size is None:
            return
        self.rotate("z", -ROTATE_ANGLE)
        self.clear()
        self.render()

    def __switchBackground(self):
        self.screen.update_background_color()
