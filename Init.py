"""FreeCAD init script of the CadQuery module"""
# (c) 2014-2016 Jeremy Wright Apache 2.0 License

#TODO: The FreeCAD devs like to put as much init code as possible in here so that the module can be used without the
#TODO: GUI if desired

import os
import sys
import module_locator

# Set up so that we can import from our embedded packages
module_base_path = module_locator.module_path()
libs_dir_path = os.path.join(module_base_path, 'Libs')
sys.path.insert(0, libs_dir_path)

# Tack on our CadQuery library git subtree
cq_lib_path = os.path.join(libs_dir_path, 'cadquery')
sys.path.insert(1, cq_lib_path)

# Make sure we get the right libs under the FreeCAD installation
fc_base_path = os.path.dirname(os.path.dirname(module_base_path))
fc_lib_path = os.path.join(fc_base_path, 'lib')
fc_bin_path = os.path.join(fc_base_path, 'bin')

# Make sure that the directories exist before we add them to sys.path
# This could cause problems or solve them by overriding what CQ is setting for the paths
if os.path.exists(fc_lib_path):
    sys.path.insert(1, fc_lib_path)
if os.path.exists(fc_bin_path):
    sys.path.insert(1, fc_bin_path)

# Need to set this for PyQode
os.environ['QT_API'] = 'pyside'