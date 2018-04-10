The CadQuery Module for FreeCAD
=======================
[![GitHub version](https://d25lcipzij17d.cloudfront.net/badge.svg?id=gh&type=6&v=1.1.0&x2=0)](https://github.com/jmwright/cadquery-freecad-module/releases/tag/v1.1.0)
[![License](https://img.shields.io/badge/license-LGPL-lightgrey.svg)](https://github.com/jmwright/cadquery-freecad-module/blob/master/LICENSE)

## Introduction

Module that adds a tabbed CadQuery editor to FreeCAD. Please see the [wiki](https://github.com/jmwright/cadquery-freecad-module/wiki) for more detailed information on getting started.

![Module User Interface](http://innovationsts.com/images/Version_1_0_0_1_and_Later_Interface.png)

## Install Through FreeCAD-Addons

  1. Follow the instructions [here](https://github.com/FreeCAD/FreeCAD-addons/blob/master/README.md) to install and execute the FreeCAD-Addons macro.
  2. Choose `cadquery_module` from the list in the datalog box and click Install/Update.
  3. Restart FreeCAD.
  
You can use the Install/Update button periodically to get the latest changes to this module.

## Manual Installation
**Requires FreeCAD 0.14 or newer**

Installation is handled slightly differently whether you are installing version 1.0.0.1 and earlier, or a later version.

### Installing v1.0.0.1 and Earlier

Download the [latest released version](https://github.com/jmwright/cadquery-freecad-module/releases), extract the archive file, and copy the `CadQuery` subdirectory to FreeCAD's `Mod` directory on your system. 

### Installing v1.0.0.2 and Later

Download the [latest released version](https://github.com/jmwright/cadquery-freecad-module/releases), extract the archive file, and copy the entire extracted directory to FreeCAD's `Mod` directory on your system. You can optionally rename the directory to something like `CadQuery`.

## Typical Installation Locations
The module should show up in the 'Workbenches' drop down the next time you start FreeCAD. Some typical `Mod` directory locations are as follows.

### Linux
* /usr/lib/freecad/Mod
* /usr/local/lib/freecad/Mod
* ~/.FreeCAD/Mod

If you are running Ubuntu Linux, be sure to run the following line in a terminal before using this module.
```
sudo apt-get install python-pyside.qtnetwork
```

### Windows
* C:\Program Files\FreeCAD 0.14\Mod
* C:\Program Files (x86)\FreeCAD 0.14\Mod
* C:\Users\[your_user_name]\Application Data\FreeCAD\Mod

### Mac
* /Applications/FreeCAD.app/Contents/Mod
* /Applications/FreeCAD.app/Mod
* /Users/[your_user_name]/Library/Preferences/FreeCAD/Mod
* ~/Library/Preferences/FreeCAD/Mod

## It's Installed, Now What?
For getting started information and troubleshooting steps, please see the [wiki](https://github.com/jmwright/cadquery-freecad-module/wiki)
