#This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

#The dimensions of the model. These can be modified rather than changing the box's code directly.
plate_radius = 2.0
hole_pattern_radius = 0.25
thickness = 0.125

#Make the plate with 4 holes in it at various points
r = cadquery.Workplane("front").circle(plate_radius)        # Make the base
r = r.pushPoints([(1.5, 0), (0, 1.5), (-1.5, 0), (0, -1.5)])   # Now four points are on the stack
r = r.circle(hole_pattern_radius)                        	# Circle will operate on all four points
result = r.extrude(thickness)

#Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())