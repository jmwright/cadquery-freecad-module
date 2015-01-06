# This example is meant to be used from within the CadQuery module of FreeCAD.
# From within FreeCAD, you can make changes to this script and then click
# CadQuery > Execute Script, or you can press F2.
# There are more examples in the Examples directory included with this module.
# Ex026_Lego_Brick.py is highly recommended as a great example of what CadQuery
# can do.
import cadquery
from Helpers import show

# The dimensions of the box. These can be modified rather than changing the
# object's code directly.
length = 2.0
height = 1.0
thickness = 1.0

# Create a 3D box based on the dimension variables above
result = cadquery.Workplane("XY").box(length, height, thickness)

# Render the solid
show(result)
