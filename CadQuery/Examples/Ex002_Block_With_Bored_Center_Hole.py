#This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
import Part

#The dimensions of the box. These can be modified rather than changing the box's code directly.
length = 80.0
height = 60.0
thickness = 10.0
center_hole_dia = 22.0

#Create a 3D box based on the dimension variables above and add a 22mm center hole
result = cadquery.Workplane("XY").box(length, height, thickness) \
    .faces(">Z").workplane().hole(center_hole_dia)

#Boiler plate code to render our solid in FreeCAD's GUI
Part.show(result.toFreecad())