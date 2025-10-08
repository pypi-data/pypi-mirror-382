### Rabbit example ###

import pkg_resources
from tiny_3d_engine.engine import Engine3D
from tiny_3d_engine.scene3d import load_file_as_scene


def spawnrabbit(shading, version=4):
    """Test the engine on the Standford rabbit"""

    if version == "4":
        rabbit = f"./bun_zipper_res4.ply"
    elif version == "3":
        rabbit = f"./bun_zipper_res3.ply"
    elif version == "2":
        rabbit = f"./bun_zipper_res2.ply"
    else:
        raise NotImplementedError()

    rabbitfile = pkg_resources.resource_filename(__name__, rabbit)
    scene = load_file_as_scene(rabbitfile)
    scene.add_axes()
    test = Engine3D(scene, title="The Standford Rabbit", shading=shading)
    test.clear()
    test.rotate("y", 45)
    test.rotate("x", 45)
    test.render()
    test.mainloop()


if __name__ == "__main__":
    spawnrabbit()
