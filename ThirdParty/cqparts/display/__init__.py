
__all__ = [
    'render_props',
    'RenderProps', 'RenderParam',

    # display
    'display',
    'get_display_environment',

    # environment
    'environment',
]

import functools

# material
from .material import RenderProps, RenderParam
from .material import render_props

# envionrment
from . import environment

# Specific Environments
from .freecad import FreeCADDisplayEnv
from .web import WebDisplayEnv
from .cqparts_server import CQPartsServerDisplayEnv


def get_display_environment():
    """
    Get the first qualifying display environment.

    :return: highest priority valid display environment
    :rtype: :class:`DisplayEnvironment <cqparts.display.environment.DisplayEnvironment>`

    see :meth:`@map_environment <cqparts.display.environment.map_environment>`
    for more information.

    This method is a common way to change script behaviour based on the
    environment it's running in.
    For example, if you wish to display a model when run in one environment, but
    export it to file when run in another, you could::

        from cqparts.display import get_display_environment, display
        from cqparts_misc.basic.primatives import Cube

        obj = Cube()

        env_name = get_display_environment().name
        if env_name == 'freecad':
            # Render the object in a FreeCAD window
            display(obj)
        else:
            # Export the object to a file.
            obj.exporter('gltf')('my_object.gltf')

    This is useful when creating a sort of "build environment" for your models.
    """
    for disp_env in environment.display_environments:
        if disp_env.condition():
            return disp_env
    return None


# Generic display funciton
def display(component, **kwargs):
    """
    Display the given component based on the environment it's run from.
    See :class:`DisplayEnvironment <cqparts.display.environment.DisplayEnvironment>`
    documentation for more details.

    :param component: component to display
    :type component: :class:`Component <cqparts.Component>`

    Additional parameters may be used by the chosen
    :class:`DisplayEnvironment <cqparts.display.environment.DisplayEnvironment>`
    """

    disp_env = get_display_environment()
    if disp_env is None:
        raise LookupError('valid display environment could not be found')

    disp_env.display(component, **kwargs)
