# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

# Create a simple block with a hole through it that we can split
c = cadquery.Workplane("XY").box(1, 1, 1).faces(">Z").workplane() \
                            .circle(0.25).cutThruAll()

# Cut the block in half sideways
result = c.faces(">Y").workplane(-0.5).split(keepTop=True)

# Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
