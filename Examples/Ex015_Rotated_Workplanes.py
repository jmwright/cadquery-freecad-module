# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# Create a rotated workplane and put holes in each corner of a rectangle on
# that workplane, producing angled holes in the face
result = cadquery.Workplane("front").box(4.0, 4.0, 0.25).faces(">Z") \
                 .workplane() \
                 .transformed(offset=(0, -1.5, 1.0), rotate=(60, 0, 0)) \
                 .rect(1.5, 1.5, forConstruction=True).vertices().hole(0.25)

# Render the solid
show(result)
