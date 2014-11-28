#This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

#Create a plate with 4 rounded corners in the Z-axis
result = cadquery.Workplane("XY").box(3, 3, 0.5).edges("|Z").fillet(0.125)

#Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
