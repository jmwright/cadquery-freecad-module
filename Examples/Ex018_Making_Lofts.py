# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# Create a lofted section between a rectangle and a circular section
result = cadquery.Workplane("front").box(4.0, 4.0, 0.25).faces(">Z") \
                 .circle(1.5).workplane(offset=3.0) \
                 .rect(0.75, 0.5).loft(combine=True)

# Render the solid
show(result)
