def show(cqObject, rgba=(204, 204, 204, 0.0)):
    import FreeCAD
    from random import random

    #Convert our rgba values
    r = rgba[0] / 255.0
    g = rgba[1] / 255.0
    b = rgba[2] / 255.0
    a = int(rgba[3] * 100.0)

    ad = FreeCAD.activeDocument()

    #Generate a random name for this shape in case we are doing multiple shapes
    newName = "Shape" + str(random())

    #Set up the feature in the tree so we can manipulate its properties
    newFeature = ad.addObject("Part::Feature", newName)

    #Change our shape's properties accordingly
    newFeature.ViewObject.ShapeColor = (r, g, b)
    newFeature.ViewObject.Transparency = a
    newFeature.Shape = cqObject.toFreecad()

    ad.recompute()
