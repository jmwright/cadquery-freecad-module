""" generate the files and notify the cqparts server
 look at https://github.com/zignig/cqparts-server
 copied and edited from web.py
 Copyright 2018 Peter Boin
 and Simon Kirkby 2018
"""

import os
import time
import tempfile
import shutil

import logging
import requests

from .environment import map_environment, DisplayEnvironment

log = logging.getLogger(__name__)



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

    def display_callback(self, component, **kwargs):
        """
        :param component: the component to render
        :type component: :class:`Component <cqparts.Component>`
        """
        # Check environmental assumptions
        if ENVVAR_SERVER not in os.environ:
            raise KeyError("environment variable '%s' not set" % ENVVAR_SERVER)

        # get the server from the environment
        server_url = os.environ[ENVVAR_SERVER]

        # Verify Parameter(s)
        # check that it is a component
        from .. import Component
        if not isinstance(component, Component):
            raise TypeError("given component must be a %r, not a %r" % (
                Component, type(component)
            ))

        # check that the server is running
        try:
            requests.get(server_url + '/status')
            #TODO inspect response for actual status and do stuff
        except requests.exceptions.ConnectionError:
            print('cqpart-server unavailable')
            return

        # get the name of the object
        cp_name = type(component).__name__

        # create temporary folder
        temp_dir = tempfile.mkdtemp()
        base_dir = self._mkdir(temp_dir, cp_name)

        try:
            # export the files to the name folder
            start_time = time.time()
            exporter = component.exporter('gltf')
            exporter(
                filename=os.path.join(base_dir, 'out.gltf'),
                embed=False,
            )
            finish_time = time.time()
            duration = finish_time - start_time

            # create the list of files to upload
            file_list = os.listdir(base_dir)
            file_load_list = []
            for i in file_list:
                # path of file to upload
                file_name = os.path.join(base_dir, i)
                # short reference to file
                file_ref = os.path.join(cp_name, i)
                # make dict for file upload
                file_load_list.append(
                    ('objs', (file_ref, open(file_name, 'rb')))
                )

            # upload the files as multipart upload
            requests.post(server_url + '/upload', files=file_load_list)
            # notify the cq parts server
            # TODO more data in post, bounding box , other data
            requests.post(server_url + '/notify', data={
                'duration': duration,
                'name': cp_name,
            })

        finally:
            # finally check that it's sane and delete
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)
