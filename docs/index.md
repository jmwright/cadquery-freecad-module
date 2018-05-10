## CadQuery Module for FreeCAD

### Table of Contents
- [Installation](installation.md)
- [Usage](usage.md)
- [Developers](developers.md)

### Introduction
This project adds a workbench to FreeCAD that makes it easy to get started using the [CadQuery API](http://dcowden.github.io/cadquery/).

![User Interface](cqfm_user_interface.png)

There are two philosophies that are probably the most influential in the design of this project.

1. _"Batteries Included"_ - A user should not have to install a lot of requirements to get started.
2. _Flexibility_ - A user should be able to customize this workbench for their workflow. Being able to use an external code editor is an example.

A stock code editor is included, along with examples showing everything from basic to advanced CadQuery scripting. This workbench also includes [cqparts](https://github.com/fragmuffin/cqparts), which is a library that adds support for parts and assemblies with constraints on top of CadQuery.

Customizable settings are available, including settings that allow the use of an external code editor, if desired.
