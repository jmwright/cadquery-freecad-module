#This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

#Create a block with holes in each corner of a rectangle on that workplane
result = cadquery.Workplane("front").box(2, 2, 0.5).faces(">Z").workplane() \
    .rect(1.5, 1.5, forConstruction=True).vertices().hole(0.125)

#Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
