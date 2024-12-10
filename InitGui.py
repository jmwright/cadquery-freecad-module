# (c) 2014-2024 CadQuery Developers Apache 2.0 License

"""
CadQuery GUI init module for FreeCAD
This adds a workbench with a scripting editor to FreeCAD's GUI.
"""

import Part, FreeCAD, FreeCADGui
from CQGui.Command import CadQueryHelp, CadQueryClearOutput


class CadQueryWorkbench (Workbench):
    """CadQuery workbench for FreeCAD"""
    """CadQuery workbench for FreeCAD"""
      
    MenuText = "CadQuery"
    ToolTip = "CadQuery workbench"

    def Initialize(self):
        self.appendMenu('CadQuery', ['CadQueryClearOutput', 'CadQueryHelp'])

    def Activated(self):
        # Define the show_object function which CadQuery execution environments need to provide
        def show_object(cq_object, options=None):
            from PySide import QtGui

            # Create the object that the BRep data will be read into
            from io import BytesIO
            brep_stream = BytesIO()

            # Get the title of the current document so that we can create/find the FreeCAD part window
            doc_name = "untitled"
            mw = FreeCADGui.getMainWindow()
            mdi_area = mw.findChild(QtGui.QMdiArea)
            active_subwindow = mdi_area.activeSubWindow()
            if active_subwindow:
                doc_name = active_subwindow.windowTitle().split(".py")[0]

            # Create or find the document that corresponds to this code pane
            # If the matching 3D view has been closed, we need to open a new one
            try:
                FreeCAD.getDocument(doc_name)
            except NameError:
                FreeCAD.newDocument(doc_name)
            ad = FreeCAD.activeDocument()

            # Convert the CadQuery object to a BRep string and then into a FreeCAD part shape
            rv = cq_object.val().exportBrep(brep_stream)
            brep_string = brep_stream.getvalue().decode('utf-8')
            part_shape = Part.Shape()
            part_shape.importBrepFromString(brep_string)

            # options={"alpha":0.5, "color": (64, 164, 223)}

            # If the user wanted to use a specific name in the tree, use it
            feature_name = doc_name
            if cq_object.val().label:
                feature_name = cq_object.val().label

            # Find the feature in the document, if it exists
            cur_feature = None
            for feat in ad.Objects:
                if feat.Name == feature_name or feat.Label == feature_name:
                    cur_feature = feat
                    break

            # Decide whether to create a new object or update an existing one
            if cur_feature:
                # Update the existing object
                cur_feature = ad.getObject(feature_name)
                cur_feature.Shape = part_shape
            else:
                cur_feature = ad.addObject("Part::Feature", feature_name)
                cur_feature.Label = feature_name
                cur_feature.Shape = part_shape

            # Apply any options to the imported shape
            if options:
                # Handle a transparency change, if requested
                if "alpha" in options:
                    # Make sure that the alpha is scaled between 0 and 255
                    alpha = int(options["alpha"] * 100)
                    cur_feature.ViewObject.Transparency = alpha

                # Handle a color change, if requested
                if "color" in options:
                    cur_feature.ViewObject.ShapeColor = options["color"]

            # Make sure the document updates
            ad.recompute()

        # Register the show_object function as a global function
        globals()['show_object'] = show_object


    def Deactivated(self):
        pass


FreeCADGui.addCommand('CadQueryClearOutput', CadQueryClearOutput())
FreeCADGui.addCommand('CadQueryHelp', CadQueryHelp())

FreeCADGui.addWorkbench(CadQueryWorkbench())
