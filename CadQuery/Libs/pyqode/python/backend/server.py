#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main server script for a pyqode.python backend. You can directly use this
script in your application if it fits your needs or use it as a starting point
for writing your own server.

::

    usage: server.py [-h] [-s [SYSPATH [SYSPATH ...]]] port

    positional arguments:
      port                  the local tcp port to use to run the server

    optional arguments:
      -h, --help            show this help message and exit
      -s [SYSPATH [SYSPATH ...]], --syspath [SYSPATH [SYSPATH ...]]

"""
import argparse
import logging
import sys


if __name__ == '__main__':
    """
    Server process' entry point
    """
    logging.basicConfig()
    # setup argument parser and parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="the local tcp port to use to run "
                        "the server")
    parser.add_argument('-s', '--syspath', nargs='*')
    args = parser.parse_args()

    # add user paths to sys.path
    if args.syspath:
        for path in args.syspath:
            print('append path %s to sys.path' % path)
            sys.path.append(path)

    from pyqode.core import backend
    from pyqode.python.backend.workers import JediCompletionProvider

    # setup completion providers
    backend.CodeCompletionWorker.providers.append(JediCompletionProvider())
    backend.CodeCompletionWorker.providers.append(
        backend.DocumentWordsProvider())

    # starts the server
    backend.serve_forever(args)
