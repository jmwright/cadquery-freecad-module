import os


def get_env_name():
    """
    Get the name of the currently running environment.

    :return: environment name
    :rtype: :class:`str`

    =========== =============
    Name        Environment
    =========== =============
    ``freecad`` freecad module
    ``cmdline`` directly in a python interpreter
    =========== =============

    These environments are intended to switch a script's behaviour from
    displaying models, or exporting them to file.

    For example::

        from cqparts.utils.env import get_env_name
        from cqparts.display import display

        my_model = SomeAssembly(foo=10, bar=-3)

        if get_env_name() == 'cmdline':
            with open('model.gltf', 'w') as fh:
                fh.write(my_model.get_export_gltf())
        else:
            display(my_model)
    """
    # FIXME: this is not a good test method, but it will do for now.
    if 'MYSCRIPT_DIR' in os.environ:
        return 'freecad'
    return 'cmdline'


env_name = get_env_name()  # it's unlikely to change
