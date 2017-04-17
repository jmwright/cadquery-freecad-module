# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# 1.0 is the distance, not coordinate
r = cadquery.Workplane("front").hLine(1.0)

# hLineTo allows using xCoordinate not distance
r = r.vLine(0.5).hLine(-0.25).vLine(-0.25).hLineTo(0.0)

# Mirror the geometry and extrude
result = r.mirrorY().extrude(0.25)

# Render the solid
show(result)
