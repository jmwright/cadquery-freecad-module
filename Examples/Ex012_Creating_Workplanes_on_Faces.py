# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# Make a basic prism
result = cadquery.Workplane("front").box(2, 3, 0.5)

# Find the top-most face and make a hole
result = result.faces(">Z").workplane().hole(0.5)

# Render the solid
show(result)
