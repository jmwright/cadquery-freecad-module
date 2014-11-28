#This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

#The workplane we want to create the spline on to extrude
s = cadquery.Workplane("XY")

#The points that the spline will pass through
sPnts = [
    (2.75, 1.5),
    (2.5, 1.75),
    (2.0, 1.5),
    (1.5, 1.0),
    (1.0, 1.25),
    (0.5, 1.0),
    (0, 1.0)
]

#Generate our plate with the spline feature and make sure it's a closed entity
r = s.lineTo(3.0, 0).lineTo(3.0, 1.0).spline(sPnts).close()

#Extrude to turn the wire into a plate
result = r.extrude(0.5)

#Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())