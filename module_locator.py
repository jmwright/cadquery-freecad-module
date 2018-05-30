# (c) 2014-2016 Jeremy Wright Apache 2.0 License
import os, sys

def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")

def module_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(str(sys.executable))
    return os.path.dirname(str(__file__))
