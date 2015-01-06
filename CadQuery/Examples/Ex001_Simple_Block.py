# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# The dimensions of the box. These can be modified rather than changing the
# object's code directly.
length = 80.0
height = 60.0
thickness = 10.0

# Create a 3D box based on the dimension variables above
result = cadquery.Workplane("XY").box(length, height, thickness)

# Render the solid
show(result)
