# (c) 2014-2016 Jeremy Wright Apache 2.0 License

def show(cqObject, rgba=(204, 204, 204, 0.0)):
    import FreeCAD
    from random import random

    #Convert our rgba values
    r = rgba[0] / 255.0
    g = rgba[1] / 255.0
    b = rgba[2] / 255.0
    a = int(rgba[3] * 100.0)

    ad = FreeCAD.activeDocument()

    # If we've got a blank shape name, we have to create a random ID
    if not cqObject.val().label:
        #Generate a random name for this shape in case we are doing multiple shapes
        newName = "Shape" + str(random())
    else:
        # We're going to trust the user to keep labels unique between shapes
        newName = cqObject.val().label

    #Set up the feature in the tree so we can manipulate its properties
    newFeature = ad.addObject("Part::Feature", newName)

    #Change our shape's properties accordingly
    newFeature.ViewObject.ShapeColor = (r, g, b)
    newFeature.ViewObject.Transparency = a
    newFeature.Shape = cqObject.toFreecad()

    ad.recompute()
