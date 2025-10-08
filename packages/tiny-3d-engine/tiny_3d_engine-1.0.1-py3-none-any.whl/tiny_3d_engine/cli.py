""" command line of Tiny 3D engine"""

import click
import tiny_3d_engine

from tiny_3d_engine.examples.geoload import spawngeo
from tiny_3d_engine.examples.rabbit import spawnrabbit
from tiny_3d_engine.examples.benchmark import benchmark


def add_version(f):
    """
    Add the version of the tool to the help heading.
    :param f: function to decorate
    :return: decorated function
    """
    doc = f.__doc__
    f.__doc__ = (
        "Package "
        + tiny_3d_engine.__name__
        + " v"
        + tiny_3d_engine.__version__
        + "\n\n"
        + doc
    )

    return f


@click.group()
@add_version
def main_cli():
    """---------------    TINY_3D_ENGINE  --------------------

    You are now using the Command line interface of Tiny 3D engine,
    a Python3 Tkinter lightweight 3D engine, created at CERFACS (https://cerfacs.fr).

    This package is mean to be used as a dependency of other packages,
    to provide a light 3D feedback for small 3D scenes <100 000 polygons.
    This CLI is given here for developers perusal and demonstrations.
    Find the script of these small tools in the /examples folder of the package.

    This is a python package currently installed in your python environement.
    See the full documentation at : https://tiny-3d-engine.readthedocs.io/en/latest/.

    DISCLAIMER: Tiny 3D engine is a brute force flat renderer.
    As it is NOT using your graphical card,
    do not excpect anything fancier than a 1980 video game.
    """
    pass


@click.command()
@click.argument("filename", nargs=1)
def load(filename):
    """Load a 3D scene from FILENAME.

    Currently ENSIGHT .geo files are supported,
    with elements bar2, tri3, quad4
    as well as .ply files , for triangles only.
    """
    spawngeo(filename)


main_cli.add_command(load)


@click.command()
def bench():
    """Run a short benchmark on your machine.

    The bench tests an increasing amount of elements bar2, tri3 and quad3,
    until the final rendering time is over .1 second.
    """
    benchmark()


main_cli.add_command(bench)


@click.command()
@click.option(
    "--shading",
    type=click.Choice(["none", "linear", "radial", "flat"], case_sensitive=False),
    default="flat",
)
@click.option(
    "--version",
    type=click.Choice(["4", "3", "2"]),
    default="4",
    help="Coarse resolution (4) to mild resolution (2).",
)
def rabbit(shading, version):
    """Run a demo with the Stanford Rabbit.

    (| (|\n
    ( -.-)\n
    o_(")(")\n

    SHADING flag will control the shading applied.

    VERSION: Three Standord rabbit versions are included:\n
        4 coarse resolution - 948 faces\n
        3 low resolution - 3851 faces\n
        2 mild resolution - 16301 faces\n

    the higest resolution circa 70000 faces was not included
    to keep the repository light enough.

    """
    spawnrabbit(shading, version)


main_cli.add_command(rabbit)
