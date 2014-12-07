# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

# The dimensions of the model. These can be modified rather than changing the
# object's code directly.
width = 2.0
thickness = 0.25

# Extrude a plate outline made of lines and an arc
result = cadquery.Workplane("front").lineTo(width, 0) \
                                    .lineTo(width, 1.0) \
                                    .threePointArc((1.0, 1.5), (0.0, 1.0)) \
                                    .close().extrude(thickness)

# Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
