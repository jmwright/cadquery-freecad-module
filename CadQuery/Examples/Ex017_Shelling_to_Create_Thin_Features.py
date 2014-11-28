#This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

#Create a hollow box that's open on both ends with a thin wall
result = cadquery.Workplane("front").box(2, 2, 2).faces("+Z").shell(0.05)

#Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
