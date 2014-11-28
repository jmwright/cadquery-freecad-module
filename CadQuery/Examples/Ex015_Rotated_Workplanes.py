#This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from cadquery import Vector
import Part

#Create a rotated workplane and put holes in each corner of a rectangle on that workplane, producing angled holes
#in the face
result = cadquery.Workplane("front").box(4.0, 4.0, 0.25).faces(">Z").workplane()  \
    .transformed(offset=Vector(0, -1.5, 1.0), rotate=Vector(60, 0, 0)) \
    .rect(1.5, 1.5, forConstruction=True).vertices().hole(0.25)

#Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())
