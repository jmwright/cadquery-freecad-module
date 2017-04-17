# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# Create a simple block with a hole through it that we can split
c = cadquery.Workplane("XY").box(1, 1, 1).faces(">Z").workplane() \
                            .circle(0.25).cutThruAll()

# Cut the block in half sideways
result = c.faces(">Y").workplane(-0.5).split(keepTop=True)

# Render the solid
show(result)
