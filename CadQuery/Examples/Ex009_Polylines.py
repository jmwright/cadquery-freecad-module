# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

# Set up our Length, Height, Width, and thickness of the beam
(L, H, W, t) = (100.0, 20.0, 20.0, 1.0)

# Define the locations that the polyline will be drawn to/thru
pts = [
    (0, H/2.0),
    (W/2.0, H/2.0),
    (W/2.0, (H/2.0 - t)),
    (t/2.0, (H/2.0-t)),
    (t/2.0, (t - H/2.0)),
    (W/2.0, (t - H/2.0)),
    (W/2.0, H/-2.0),
    (0, H/-2.0)
]

# We generate half of the I-beam outline and then mirror it to create the full
# I-beam
result = cadquery.Workplane("front").polyline(pts).mirrorY().extrude(L)

# Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
