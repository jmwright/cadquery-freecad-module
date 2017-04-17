"""
This packages contains the available python widgets:

    - PyCodeEdit
    - PyInteractiveConsole

"""
from .code_edit import PyCodeEditBase, PyCodeEdit
from .interactive import PyInteractiveConsole
# todo PyOutlineTreeWidget is deprecated and should be removed soon.
from .outline import PyOutlineTreeWidget


__all__ = [
    'PyCodeEdit',
    'PyCodeEditBase',
    'PyInteractiveConsole',
    'PyOutlineTreeWidget'
]
