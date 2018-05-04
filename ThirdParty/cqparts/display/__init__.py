
__all__ = [
    'render_props',
    'RenderProps', 'RenderParam',

    # display methods
    'display',
    'freecad_display',
    'web_display',
]

# material
from .material import RenderProps, RenderParam
from .material import render_props

from .freecad import freecad_display
from .web import web_display

from cqparts.utils.env import get_env_name

def display(component):
    """
    Display the given component based on the
    :meth:`get_env_name() <cqparts.utils.env.get_env_name>`.
    """
    env_name = get_env_name()

    if env_name == 'freecad':
        freecad_display(component)
    else:
        web_display(component)
