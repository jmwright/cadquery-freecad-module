#This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

#Make a basic prism
result = cadquery.Workplane("front").box(3, 2, 0.5)

#Workplane is offset from the object surface
result = result.faces("<X").workplane(offset=0.75)

#Create a disc
result = result.circle(1.0).extrude(0.5)

#Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
