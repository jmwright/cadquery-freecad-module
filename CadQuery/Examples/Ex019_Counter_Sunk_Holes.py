# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

# Create a plate with 4 counter-sunk holes in it
result = cadquery.Workplane(cadquery.Plane.XY()).box(4, 2, 0.5).faces(">Z") \
    .workplane().rect(3.5, 1.5, forConstruction=True)\
    .vertices().cskHole(0.125, 0.25, 82.0, depth=None)

# Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
