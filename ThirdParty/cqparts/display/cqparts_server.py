# generate the files and notify the cqparts server
# look at https://github.com/zignig/cqparts-server
# copied and edited from web.py
# Copyright 2018 Peter Boin
# and Simon Kirkby 2018

import os
import sys
import inspect
import time
import requests
import tempfile

import logging
log = logging.getLogger(__name__)

from .environment import map_environment, DisplayEnvironment


ENVVAR_SERVER = 'CQPARTS_SERVER'


@map_environment(
    name='cqparts_server',
    order=50,
    condition=lambda: ENVVAR_SERVER in os.environ,
)
class CQPartsServerDisplayEnv(DisplayEnvironment):
    """
    Display given component in a
    `cqps-server <https://github.com/zignig/cqparts-server>`_ window.
    """
    @classmethod
    def _mkdir(cls, *path_parts):
        # Make a new directory, if it doesn't exist already
        dir_path = os.path.join(*path_parts)
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        return dir_path

    def display_callback(self, component):
        """
        :param component: the component to render
        :type component: :class:`Component <cqparts.Component>`
        """
        # Check environmental assumptions
        if ENVVAR_SERVER not in os.environ:
            raise KeyError("environment variable '%s' not set" % ENVVAR_SERVER)

        # Verify Parameter(s)
        # check that it is a component
        from .. import Component
        if not isinstance(component, Component):
            raise TypeError("given component must be a %r, not a %r" % (
                Component, type(component)
            ))

        cp_name = type(component).__name__

        # create temporary folder
        temp_dir = self._mkdir(tempfile.gettempdir(), 'cqpss')
        temp_dir = self._mkdir(tempfile.gettempdir(), 'cqpss', cp_name)

        # export the files to the name folder
        exporter = component.exporter('gltf')
        exporter(
            filename=os.path.join(temp_dir, 'out.gltf'),
            embed=False,
        )

        # get the server from the environment
        server_url = os.environ[ENVVAR_SERVER]

        # notify the cq parts server
        resp = requests.post(server_url + '/notify', data={
            'name': cp_name,
        })
