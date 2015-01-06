# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# Create a hollow box that's open on both ends with a thin wall
result = cadquery.Workplane("front").box(2, 2, 2).faces("+Z").shell(0.05)

# Render the solid
show(result)
