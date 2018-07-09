#!/usr/bin/env python

import argparse
import os
import inspect
import csv

import cqparts
from cqparts.catalogue import JSONCatalogue

# TODO: import your library
# TODO: if you don't offer a catalogue for your library, then
#       remove this `scripts` folder.
import cqparts_template

from cqparts_template.clamp.peg import ClothesPeg

# ---------- Parameter Defaults ----------
_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def _relative_path_to(path_list, filename):
    """Get a neat relative path to files relative to the CWD"""
    return os.path.join(
        os.path.relpath(os.path.join(*path_list), os.getcwd()),
        filename
    )

DEFAULT_OUTPUT = _relative_path_to([_this_path, '..'], 'pegs.json')
DEFAULT_INPUT = _relative_path_to([_this_path], 'pegs.csv')

parser = argparse.ArgumentParser(
    prog='Build catalogue',  # TODO: change program name
)

parser.add_argument(
    '-o', '--output', dest='output',
    default=DEFAULT_OUTPUT, metavar="FILE",
    help='catalogue file to write',
)

parser.add_argument(
    '-i', '--input', dest='input',
    default=DEFAULT_INPUT, metavar="FILE",
    help='component parameters file',
)

args = parser.parse_args()


# ---------- Component Builders ----------
# TODO: build your own objects in whatever way suits your application.

def build_obj(cls, **kwargs):
    # Take any parameters relevent to the given class from kwargs
    #   (all other parameters ignored)
    class_params = cls.class_params()
    obj_kwargs = {
        key: kwargs.pop(key, param.default)
        for (key, param) in class_params.items()
    }

    return cls(**obj_kwargs)


# ---------- Create Catalogue ----------

catalogue = JSONCatalogue(args.output, clean=True)

with open(args.input, "rb" ) as csv_fileio:
    csv_reader = csv.DictReader(csv_fileio)
    for line in csv_reader:
        obj = build_obj(ClothesPeg, **line)
        criteria = {
            key: line[key]
            for key in line.keys()
            if (not hasattr(obj, key)) and (key not in ('ID',))
        }
        catalogue.add(id=line['ID'], obj=obj, criteria=criteria)
