[<Back to Main](index.md)
## Developers

If you would like to contribute to this project, below is some information to help you get started.

### Table of Contents
- [Contribution Guidelines](developers.md#contribution-guidelines)
- [Manual Installation](developers.md#manual-installation)
- [CadQuery Installation](developers.md#cadquery-installation)
- [Compiling the Qt Resource File](developers.md#compiling-the-qt-resource-file)

### Contribution Guidelines

Contribution guidelines can be found [here](https://github.com/CadQuery/cadquery-freecad-workbench/blob/master/CONTRIBUTING.md). Please familiarize yourself with them as part of the process of getting involved.

### Manual Installation

Developers may need to run specific versions of this module which are not installed by FreeCAD's addons manager. There is a section in the installation documentation on [manual installation](installation.md#manual). This can be used to run any version or branch of the module that is needed.

### CadQuery Installation

When installing from outside the `Addon manager`, the CadQuery dependency will not be installed. To fix this, the following can be run from within FreeCAD's Python console.

```python
import subprocess
import sys
subprocess.run(["python", "-m", "pip", "install", "--upgrade", "git+https://github.com/CadQuery/cadquery.git"], capture_output=True)
```

The `master` version of CadQuery must currently be used to avoid version conflicts with the embedded FreeCAD packages. If you are reading this after CadQuery's 2.5.0 release, the stable version can be installed.

### Compiling the Qt Resource File
**NOTE:** It is unclear whether this is still needed with FreeCAD 1.0 or not. You can most likely skip this for now.

This is done to update the CadQuery logo.
1. Install the PySide development tools: `sudo apt-get install pyside-tools`
2. `cd` into the root directory of this module/workbench.
3. Run the following command: `pyside-rcc ./CQGui/Resources/CadQuery.qrc -o CadQuery_rc.py`

Newer versions of FreeCAD use Pyside2, and so `pyside2-rcc` is needed instead:
```bash
sudo add-apt-repository ppa:thopiekar/pyside-git
sudo apt-get update
```

[<Back to Main](index.md)
