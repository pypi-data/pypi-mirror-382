# heavy example
from tiny_3d_engine.scene3d import Scene3D
from tiny_3d_engine.engine import Engine3D

scene = Scene3D()

SIZE = 2
LENGTH = 200.0
points = list()
conn = list()
dx = LENGTH / SIZE

for i in range(SIZE):
    for j in range(SIZE):
        index = len(points)
        points.append([i * dx, j * dx, 0])
        points.append([(i + 1) * dx, j * dx, 0])
        points.append([i * dx, (j + 1) * dx, 0])
        points.append([(i + 1) * dx, (j + 1) * dx, 0])
        # conn.append([index, index+1, index+2])
        # conn.append([index+3, index+1, index+2])
        conn.append([index, index + 1])
        conn.append([index + 3, index + 1])
scene.update("square1", points, conn, color="#0000ff")

points = list()
conn = list()
for i in range(SIZE):
    for j in range(SIZE):
        index = len(points)
        points.append([i * dx, j * dx, LENGTH])
        points.append([(i + 1) * dx, j * dx, LENGTH])
        points.append([i * dx, (j + 1) * dx, LENGTH])
        points.append([(i + 1) * dx, (j + 1) * dx, LENGTH])
        conn.append([index, index + 1, index + 3, index + 2])
scene.update("square2", points, conn, color="#ff0000")

scene.add_axes()
test = Engine3D(scene)
test.rotate("x", 45)
test.rotate("y", 45)
test.render()
# test.bench_speed()
test.mainloop()
