cadquery-freecad-module
=======================
[![GitHub version](https://badge.fury.io/gh/jmwright%2Fcadquery-freecad-module.svg)](https://github.com/jmwright/cadquery-freecad-module/releases)
[![License](https://img.shields.io/badge/license-LGPL-lightgrey.svg)](https://github.com/jmwright/cadquery-freecad-module/blob/master/LICENSE)

## Introduction

Module that adds a tabbed CadQuery editor to FreeCAD. Please see the [wiki](https://github.com/jmwright/cadquery-freecad-module/wiki) for more detailed information on getting started.

![Module User Interface](http://innovationsts.com/images/Version_1_0_0_1_and_Later_Interface.png)

## Installation
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

If you are running Ubuntu Linux, be sure to run the following line in a terminal before using this module.
```
sudo apt-get install python-pyside.qtnetwork
```

### Windows
* C:\Program Files\FreeCAD 0.14\Mod
* C:\Program Files (x86)\FreeCAD 0.14\Mod

### Mac
* /Applications/FreeCAD.app/Contents/Mod
* /Applications/FreeCAD.app/Mod
* /Users/<user>/Library/Preferences/FreeCAD/Mod

## It's Installed, Now What?
For getting started information and troubleshooting steps, please see the [wiki](https://github.com/jmwright/cadquery-freecad-module/wiki)
