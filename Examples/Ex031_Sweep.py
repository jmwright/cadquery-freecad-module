# This example is meant to be used from within the CadQuery module for FreeCAD
import cadquery
from Helpers import show

# Points we will use to create spline and polyline paths to sweep over
pts = [
    (0, 1),
    (1, 2),
    (2, 4)
]

# Spline path generated from our list of points (tuples)
path = cadquery.Workplane("XZ").spline(pts)

# Sweep a circle with a diameter of 1.0 units along the spline path we just created
defaultSweep = cadquery.Workplane("XY").circle(1.0).sweep(path)

# Sweep defaults to making a solid and not generating a Frenet solid. Setting Frenet to True helps prevent creep in
# the orientation of the profile as it is being swept
frenetShell = cadquery.Workplane("XY").circle(1.0).sweep(path, makeSolid=False, isFrenet=True)

# We can sweep shapes other than circles
defaultRect = cadquery.Workplane("XY").rect(1.0, 1.0).sweep(path)

# Switch to a polyline path, but have it use the same points as the spline
path = cadquery.Workplane("XZ").polyline(pts)

# Using a polyline path leads to the resulting solid having segments rather than a single swept outer face
plineSweep = cadquery.Workplane("XY").circle(1.0).sweep(path)

# Switch to an arc for the path
path = cadquery.Workplane("XZ").threePointArc((1.0, 1.5), (0.0, 1.0))

# Use a smaller circle section so that the resulting solid looks a little nicer
arcSweep = cadquery.Workplane("XY").circle(0.5).sweep(path)

# Translate the resulting solids so that they do not overlap and display them left to right
show(defaultSweep)
show(frenetShell.translate((5, 0, 0)))
show(defaultRect.translate((10, 0, 0)))
show(plineSweep.translate((15, 0, 0)))
show(arcSweep.translate((20, 0, 0)))