[<Back to Main](index.md)
## Developers

If you would like to contribute to this project, below is some information to help you get started.

### Table of Contents
- [Contribution Guidelines](developers.md#contribution-guidelines)
- [Manual Installation](developers.md#manual-installation)
- [Embedded Libraries](developers.md#embedded-libraries)
- [Updating cqparts](developers.md#updating-cqparts)
- [Compiling the Qt Resource File](developers.md#compiling-the-qt-resource-file)
- [Future Enhancements](developers.md#future-enhancements)

### Contribution Guidelines

Contribution guidelines can be found [here](https://github.com/jmwright/cadquery-freecad-module/blob/master/CONTRIBUTING.md). Please familiarize yourself with them as part of the process of getting involved.

### Manual Installation
Developers may need to run specific versions of this module which are not installed by FreeCAD's addons manager. There is a section in the installation documentation on [manual installation](installation.md#manual). This can be used to run any version or branch of the module that is needed.

### Embedded Libraries
All of the libraries that this module depends on reside in the `Libs` directory. Updated library versions should be downloaded manually, extracted, and placed in this directory. Libraries related to cqparts are updated through a script, and will be overwritten if updated manually.

### Updating cqparts
In the `Tools` directory of the repository is a utility named `update_dependencies.sh`. Any time that a new version of cqparts is released, that script should be run from within the `Tools` directory.
```
cd Tools
./update_dependencies.sh
```
This script will update some of the libraries in the `Libs` directory, as well as any relevant cqparts packages in the `ThirdParty` directory.

### Compiling the Qt Resource File
This is done to update the CadQuery logo.
1. Install the PySide development tools: `sudo apt-get install pyside-tools`
2. `cd` into the root directory of this module/workbench.
3. Run the following command: `pyside-rcc ./CQGui/Resources/CadQuery.qrc -o CadQuery_rc.py`

### Future Enhancements
Below are some future enhancements that contributors are welcome to take on.

#### Configuration File Settings
* Select a light or dark theme
* Set default directory for open/save dialogs
* ParametricParts.com user name
* Enable/disable experimental code. This would allow us to experiment with more difficult and far reaching features without affecting the non-power users, like adding CQ code to the editor by clicking a button in the GUI.
* Automatic save on execute
* User defined paths to the FreeCAD library. Matching feature request is [here](https://github.com/jmwright/cadquery-freecad-module/issues/48).

#### UI Features

* From [issue 28](https://github.com/jmwright/cadquery-freecad-module/issues/28) - Add a way to highlight the objects matched by a selector.
* From [issue 28](https://github.com/jmwright/cadquery-freecad-module/issues/28) - Add a way to visualize the negative space in a cut (something like openscad's debug operator).
* From [issue 28](https://github.com/jmwright/cadquery-freecad-module/issues/28) - Some limited mouse interaction; use to generate a direction selector based on the current view, for example.
* From [issue 19](https://github.com/jmwright/cadquery-freecad-module/issues/19) - Add interactive parameters like there are on ParametricParts.com.
