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

[<Back to Main](index.md)
