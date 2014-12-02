# This example is meant to be used from within the CadQuery module of FreeCAD.
# From within FreeCAD, you can make changes to this script and then click
# CadQuery > Execute Script, or you can press F2.
import cadquery
import Part

# The dimensions of the box. These can be modified rather than changing the
# box's code directly.
length = 2.0
height = 1.0
thickness = 1.0

# Create a 3D box based on the dimension variables above
result = cadquery.Workplane("XY").box(length, height, thickness)

# Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
