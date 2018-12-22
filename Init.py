"""FreeCAD init script of the CadQuery module"""
# (c) 2014-2018 Jeremy Wright Apache 2.0 License
import os
import sys
try:
    from . import module_locator
except:
    import module_locator

# Set up so that we can import from our embedded packages
module_base_path = module_locator.module_path()
libs_dir_path = os.path.join(module_base_path, 'Libs')
sys.path.insert(0, libs_dir_path)

# Tack on our CadQuery library git subtree
cq_lib_path = os.path.join(libs_dir_path, 'cadquery')
sys.path.insert(1, cq_lib_path)

# Add our third party libraries so that they can be used in scripts
third_party_path = os.path.join(module_base_path, 'ThirdParty')
sys.path.append(third_party_path)

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

# Set sane defaults for FreeCAD-stored settings if they haven't been set yet
has_run_before = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").GetBool("runBefore")

if not has_run_before:
	FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetInt("fontSize", 12)
	FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetString("executeKeybinding", "F9")
	FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetBool("executeOnSave", True)
	FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetBool("showLineNumbers", True)
	# FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetBool("useExternalEditor", False)

	# Make sure we don't overwrite someone's existing settings
	FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetBool("runBefore", True)