""" The benchmarking example file"""

import time
import math
import sys
from tiny_3d_engine.engine import Engine3D
from tiny_3d_engine.scene3d import Scene3D, load_file_as_scene


import matplotlib.pyplot as plt


__all__ = ["benchmark"]


def benchmark(max_time=0.1):
    """Benchmark on speed"""
    print(
        """
*********************
 Benchmark on speed
*********************

"""
    )

    engine3d = Engine3D(None, title="Benchmark")

    size = 4
    perf = 0.0

    results = {
        "size": list(),
        "bar2": list(),
        "tri3": list(),
        "quad4": list(),
        "ref": list(),
    }
    while perf < max_time:
        size = int(size * math.sqrt(2))
        results["size"].append(size * size)
        print("## size is " + str(size * size))
        for elmt in ["bar2", "tri3", "quad4"]:
            scene = gen_bench_square(size, elmt)
            perf = render_bench(engine3d, scene)
            results[elmt].append(1 / perf)

        results["ref"].append(30000.0 / (size * size))

    engine3d.mainloop()

    plot_bench_results(results)


def render_bench(engine3d, scene, trials=5):

    engine3d.update(scene)
    # perf_list = list()
    # for i in range(trials):
    #     start = time.time()
    #     self.rotate('y', 1.)
    #     end = time.time()
    #     perf_list.append(end-start)

    # perf = sum(perf_list) / len(perf_list)
    # print(".   Rotate", str(round(1000*perf, 3)) + " ms")
    perf_list = list()
    for i in range(trials):
        start = time.time()
        engine3d.clear()
        engine3d.render()
        end = time.time()
        perf_list.append(end - start)

    perf = sum(perf_list) / len(perf_list)

    return perf


def gen_bench_square(size, elmt):
    """replace scene with a square for bench"""
    LENGTH = 200.0
    points = list()
    conn = list()
    dx = LENGTH / size
    for i in range(size):
        for j in range(size):
            index = len(points)
            points.append([i * dx, j * dx, 0])
            points.append([(i + 1) * dx, j * dx, 0])
            points.append([i * dx, (j + 1) * dx, 0])
            points.append([(i + 1) * dx, (j + 1) * dx, 0])
            if elmt == "bar2":
                conn.append([index, index + 1])
            elif elmt == "tri3":
                conn.append([index, index + 1, index + 2])
            elif elmt == "quad4":
                conn.append([index, index + 1, index + 3, index + 2])
            else:
                raise RunTimeError(elmt + " is nort in bar2/tri3/quad4")
    scene = Scene3D()
    scene.update("square_bench", points, conn, color="#0000ff")
    return scene


def plot_bench_results(results):
    """Plot the reults with matplotlib"""
    try:
        import matplotlib.pyplot as plt
    except ImportError as err:
        print(err)
        print("Please install matplotlib...")

    plt.loglog(results["size"], results["bar2"], label="bar2")
    plt.loglog(results["size"], results["tri3"], label="tri3")
    plt.loglog(results["size"], results["quad4"], label="quad4")
    plt.loglog(results["size"], results["ref"], label="30000/poly")
    plt.legend()
    plt.grid(True)
    plt.xlabel("Nb of elements")
    plt.ylabel("FPS")
    plt.show()


if __name__ == "__main__":
    benchmark(max_time=0.1)
