""" The Basic script to import a geo or ply file"""

import sys
from tiny_3d_engine.engine import Engine3D
from tiny_3d_engine.scene3d import load_file_as_scene

__all__ = ["spawngeo"]


def spawngeo(file_):
    """Script to import a file"""

    scene = load_file_as_scene(file_, prefix="essa1", color="#ffffff")
    scene.add_axes()
    test = Engine3D(scene, title=str(file_))
    test.render()
    test.mainloop()


if __name__ == "__main__":
    spawngeo(sys.argv[1])
