
import os
import sys
import inspect
import tempfile
import shutil
import jinja2
import time

# web content
if sys.version_info[0] >= 3:
    # python 3.x
    import http.server as SimpleHTTPServer
    import socketserver as SocketServer
else:
    # python 2.x
    import SimpleHTTPServer
    import SocketServer
import threading
import webbrowser

import logging
log = logging.getLogger(__name__)

from ..utils import working_dir

# Get this file's location
_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# Set template web-content directory
# note: can be changed prior to calling web_display()
#
#   >>> from cqparts.display import web
#   >>> web.TEMPLATE_CONTENT_DIR = './my/alternative/template'
#   >>> web.web_display(some_thing)
#
# This would typically be used for testing, or development purposes.
TEMPLATE_CONTENT_DIR = os.path.join(_this_path, 'web-template')

SocketServer.TCPServer.allow_reuse_address = True  # stops crash on re-use of port


def web_display(component, port=9041):
    """
    Display given component in a browser window

    :param component: the component to render
    :type component: :class:`Component <cqparts.Component>`
    :param port: port to expose http service on
    :type port: :class:`int`

    This method exports the model, then exposes a http service on *localhost*
    for a browser to use.
    The http service does not know when the browser window has been closed, so
    it will continue to serve the model's data until the user halts the
    process with a :class:`KeyboardInterrupt` (by pressing ``Ctrl+C``)

    When run, you should see output similar to::

        >>> from cqparts.display import web_display
        >>> from cqparts_misc.basic.primatives import Cube
        >>> web_display(Cube())
        press [ctrl+c] to stop server
        127.0.0.1 - - [27/Dec/2017 16:06:37] "GET / HTTP/1.1" 200 -
        Created new window in existing browser session.
        127.0.0.1 - - [27/Dec/2017 16:06:39] "GET /model/out.gltf HTTP/1.1" 200 -
        127.0.0.1 - - [27/Dec/2017 16:06:39] "GET /model/out.bin HTTP/1.1" 200 -

    A new browser window should appear with a render that looks like:

    .. image:: /_static/img/web_display.cube.png

    Then, when you press ``Ctrl+C``, you should see::

        ^C[server shutdown successfully]

    and any further request on the opened browser window will return
    an errorcode 404 (file not found), because the http service has stopped.
    """
    # Verify Parameter(s)
    from .. import Component

    if not isinstance(component, Component):
        raise TypeError("given component must be a %r, not a %r" % (
            Component, type(component)
        ))

    # Create temporary file to host files
    temp_dir = tempfile.mkdtemp()
    host_dir = os.path.join(temp_dir, 'html')
    print("host temp folder: %s" % host_dir)

    # Copy template content to temporary location
    shutil.copytree(TEMPLATE_CONTENT_DIR, host_dir)

    # Export model
    exporter = component.exporter('gltf')
    exporter(
        filename=os.path.join(host_dir, 'model', 'out.gltf'),
        embed=False,
    )

    # Modify templated content
    # index.html
    with open(os.path.join(host_dir, 'index.html'), 'r') as fh:
        index_template = jinja2.Template(fh.read())
    with open(os.path.join(host_dir, 'index.html'), 'w') as fh:
        # camera location & target
        cam_t = [
            (((a + b) / 2.0) / 1000)  # midpoint (unit: meters)
            for (a, b) in zip(exporter.scene_min, exporter.scene_max)
        ]
        cam_p = [
            ((b - a) * 1.0) / 1000 + t  # max point * 200% (unit: meters)
            for (a, b, t) in zip(exporter.scene_min, exporter.scene_max, cam_t)
        ]

        # write
        xzy = lambda a: (a[0], a[2], -a[1])  # x,z,y coordinates (not x,y,z)
        fh.write(index_template.render(
            model_filename='model/out.gltf',
            camera_target=' '.join("%g" % (val) for val in xzy(cam_t)),
            camera_pos=' '.join("%g" % (val) for val in xzy(cam_p)),
        ))

    try:
        # Start web-service (loop forever)
        server = SocketServer.ThreadingTCPServer(
            server_address=("localhost", port),
            RequestHandlerClass=SimpleHTTPServer.SimpleHTTPRequestHandler,
        )
        server_addr = "http://%s:%i/" % server.server_address
        def thread_target():
            with working_dir(host_dir):
                server.serve_forever()

        print("serving: %s" % server_addr)
        sys.stdout.flush()
        server_thread = threading.Thread(target=thread_target)
        server_thread.daemon = True
        server_thread.start()

        # Open in browser
        print("opening in browser: %s" % server_addr)
        sys.stdout.flush()
        webbrowser.open(server_addr)

        # workaround for https://github.com/dcowden/cadquery/issues/211
        import signal
        def _handler_sigint(signum, frame):
            raise KeyboardInterrupt()
        signal.signal(signal.SIGINT, _handler_sigint)

        print("press [ctrl+c] to stop server")
        sys.stdout.flush()
        while True:  # wait for Ctrl+C
            time.sleep(1)

    except KeyboardInterrupt:
        log.info("\n[keyboard interrupt]")
        sys.stdout.flush()

    finally:
        # Stop web-service
        server.shutdown()
        server.server_close()
        server_thread.join()
        print("[server shutdown successfully]")

        # Delete temporary content
        if os.path.exists(os.path.join(host_dir, 'cqparts-display.txt')):
            # just making sure we're deleting the right folder
            shutil.rmtree(temp_dir)
