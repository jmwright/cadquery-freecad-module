# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

# Make a basic prism
result = cadquery.Workplane("front").box(3, 2, 0.5)

# Select the lower left vertex and make a workplane
result = result.faces(">Z").vertices("<XY").workplane()

# Cut the corner out
result = result.circle(1.0).cutThruAll()

# Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
