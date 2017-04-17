# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# The dimensions of the model. These can be modified rather than changing the
# object's code directly.
circle_radius = 50.0
rectangle_width = 13.0
rectangle_length = 19.0
thickness = 13.0

# Extrude a cylindrical plate with a rectangular hole in the middle of it
result = cadquery.Workplane("front").circle(circle_radius) \
                                    .rect(rectangle_width, rectangle_length) \
                                    .extrude(thickness)

# Render the solid
show(result)
