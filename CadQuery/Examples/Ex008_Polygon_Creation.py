# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# The dimensions of the model. These can be modified rather than changing the
# object's code directly.
width = 3.0
height = 4.0
thickness = 0.25
polygon_sides = 6
polygon_dia = 1.0

# Create a plate with two polygons cut through it
result = cadquery.Workplane("front").box(width, height, thickness) \
                                    .pushPoints([(0, 0.75), (0, -0.75)]) \
                                    .polygon(polygon_sides, polygon_dia) \
                                    .cutThruAll()

# Render the solid
show(result)
