[<Back to Main](index.md) | [Usage>](usage.md)
## Installation

### Table of Contents
- [Via Addon manager](installation.md#automated)
- [Manual](installation.md#manual)

### Automated
This workbench can be install via FreeCAD's `Addon manager`.
1. Run the FreeCAD Addon Manager by clicking `Tools->Addon manager`
![Addon manager menu item](images/addon_manager_menu_item.png)
2. Scroll down and click on `CadQuery`
![cadquery_module addon item](images/cadquery_module_addon_manager_item.png)
3. Click the `Install / update` button
3. Restart FreeCAD
4. Confirm that CadQuery is in the drop down menu of available workbenches

![cadquery workbench item](images/cadquery_workbench_item.png)

This process can be repeated to update the module every time changes are pushed to the master branch on GitHub.

### Manual
Sometimes a different version or branch of the workbench may be needed, other than what is installed using the addon manager. The steps below outline the steps to manually install the workbench.
1. Download the [latest released version](https://github.com/CadQuery/cadquery-freecad-workbench/releases)
2. Extract the archive file
3. Copy the entire extracted directory to FreeCAD's `Mod` directory on your system. Typical `Mod` directory locations are listed below.

**Linux Mod Locations**
- /usr/lib/freecad/Mod
- /usr/local/lib/freecad/Mod
- ~/.FreeCAD/Mod
- ~/.local/share/FreeCAD/Mod

**Windows Mod Locations**
- C:\Program Files\FreeCAD 0.14\Mod
- C:\Program Files (x86)\FreeCAD 0.14\Mod
- C:\Users\[your_user_name]\Application Data\FreeCAD\Mod

**Mac Mod Locations**
- /Applications/FreeCAD.app/Contents/Mod
- /Applications/FreeCAD.app/Mod
- /Users/[your_user_name]/Library/Preferences/FreeCAD/Mod
- ~/Library/Preferences/FreeCAD/Mod

[<Back to Main](index.md) | [Usage>](usage.md)
