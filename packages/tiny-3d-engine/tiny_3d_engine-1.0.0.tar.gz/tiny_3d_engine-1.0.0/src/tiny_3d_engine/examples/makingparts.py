from tiny_3d_engine.part3d import Part3D
from tiny_3d_engine.scene3d import Scene3D
from tiny_3d_engine.engine import Engine3D


# p3d.add_point((0.0,0.0,0.0))
# p3d.add_point((1.0,0.0,0.0))
# p3d.add_point((0.0,1.0,0.0))
# p3d.add_point((0.0,0.0,1.0))


# p3d.add_line( (0.0,0.0,0.0), (1.0,1.0,1.0), 3)
# p3d.add_line( (2.0,2.0,2.0), (1.0,1.0,1.0), 3)

# p3d.add_frustum((0.0,0.0,0.0), (0.0,0.0, 1.0), 0.5, 0.5)


p3d1 = Part3D()
p3d1.add_cartbox((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), n_i=12, n_j=3, n_k=6)

p3d2 = Part3D()
p3d2.add_parallelogram(
    (2.0, 0.0, 0.0), (2.0, 0.0, 1.0), (2.0, 1.0, 0.0), n_i=10, n_j=10
)

scn = Scene3D()
scn.update("cartbox", p3d1.points, p3d1.conn, color="#ffffff")
scn.update("parallogram", p3d2.points, p3d2.conn, color="#ffffff")
scn.add_axes()
# scn.dump("dummy")
test = Engine3D(scn)
test.rotate("x", 45)
test.rotate("y", 45)
test.render()
# test.bench_speed()
test.mainloop()
