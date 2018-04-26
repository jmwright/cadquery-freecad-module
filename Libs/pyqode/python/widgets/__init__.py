"""
This packages contains the available python widgets:

    - PyCodeEdit
    - PyInteractiveConsole

"""
from .code_edit import PyCodeEditBase, PyCodeEdit
from .interactive import PyInteractiveConsole
# todo PyOutlineTreeWidget is deprecated and should be removed soon.
from .outline import PyOutlineTreeWidget
from .console import PyConsole

__all__ = [
    'PyCodeEdit',
    'PyConsole',
    'PyCodeEditBase',
    'PyInteractiveConsole',
    'PyOutlineTreeWidget'
]
