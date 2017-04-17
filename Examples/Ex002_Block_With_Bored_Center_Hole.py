# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# The dimensions of the box. These can be modified rather than changing the
# object's code directly.
length = 80.0
height = 60.0
thickness = 10.0
center_hole_dia = 22.0

# Create a box based on the dimensions above and add a 22mm center hole
result = cadquery.Workplane("XY").box(length, height, thickness) \
    .faces(">Z").workplane().hole(center_hole_dia)

# Render the solid
show(result)
