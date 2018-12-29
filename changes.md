Changes
=======

v1.3.0 (unreleased)
-----
    * PyQode editor has been replaced by a custom editor due to compatibility problems with Qt5/PySide2
    * Settings have now been moved into FreeCAD user parameters
    * Settings dialog has been added under CadQuery->Settings
    * Execute-on-save setting is now on by default
    * Execute-script key has been changed to F9 to avoid conflicts with FreeCAD's F2, but key is still configurable
    * New code editor automatically reloads contents of script file if changed on disk, enabling use of external editor by default
    * Setting added to show/hide line numbers in code editor
    * Default font size for code editor changed to 12, but size is still configurable

v1.2.0
-----
    * Made a copy of the PyQode editor which is abandoned, so that a custom version can be maintained here
    * Fixed Qt5 bugs, particularly ones that were effecting macOS
    * Added infrastructure to support third party add-on libraries
    * Integrated the cqparts library as an add-on in the ThirdParty directory - https://github.com/fragmuffin/cqparts
    * Created a script to update third-party libraries to aid in maintenance
    * An option was added to Settings.py which reports script execution time to the Report View
    * Created a Docs directory to lay the ground work for a documentation revamp.

v1.1.0
-----
    * Updated to the v1.1.0 version of the CadQuery library

v1.0.0.2
-----
    * Added support for the CadQuery Gateway Interface (CQGI), which is a way to make scripts portable

v1.0.0.1
-----
    * Added example (Ex033) using logical operators in a string selector (thanks @adam-urbanczyk)
    * Fixed a bug in Helpers.show() that would clear the 3D view each time it was called
    * Fixed a bug that required there to be an open script window, disallowing the use of macros

v1.0.0
-----
    * Embedded pyparsing package as a supporting library for new selector syntax
    * Added a check to remove any disallowed characters from the document name when executing a script
    * Added advanced example of 3D printer extruder support (thanks @adam-urbanczyk)
    * Made the switch to tabbed editing

v0.5.1
-----
    * Version updates for CadQuery v0.4.0, v0.4.1, v0.5.0-stable and v0.5.1
    * Updated CadQuery license to Apache 2.0

v0.3.0
-----
    * Converted thickness setting to thickness boolean in the Lego brick example (thanks @galou) #59
    * Improved parametric enclosure (Ex023) example (thanks @galou) #61
    * Added braille and NumPy examples (thanks @galou) #61
    * Embedded CadQuery library as a git subtree to lessen maintenance issues
    * Embedded Pint library for units handling
    * Fixed version number in InitGui.py
    * Added BoundingBox centerOption example (Ex030) (thanks @huskier) #66
    * Made change to leave the 3D render in place when switching to another workbench
    * Now use a user provided CadQuery shape label to label rendered FreeCAD objects

v0.2.0
-----
    * Added a license badge to the readme
    * Updated the CadQuery library
    * Updated the PyQode libraries

v0.1.8
-----
    * Initial commit
