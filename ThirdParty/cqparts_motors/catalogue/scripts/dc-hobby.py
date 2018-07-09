#!/usr/bin/env python

# Catalogue Usage example:
#   >>> from cqparts.catalogue import JSONCatalogue
#   >>> import cqparts_motors
#   >>> filename = os.path.join(
#   ...     os.path.dirname(cqparts_motors.__file__),
#   ...     'catalogue', 'dcmotor.json',
#   ... )
#   >>> catalogue = JSONCatalogue(filename)
#   >>> item = catalogue.get_query()
#   >>> dc = catalogue.get(item.criteria.size == 304)
#   >>> from cqparts.display import display
#   >>> display(dc)

import os

import cqparts
from cqparts.catalogue import JSONCatalogue

# DC Motor 
from cqparts_motors.dc import DCMotor


CATALOGUE_NAME = 'dcmotor.json'

# DC Motor hobby examples
# example only
DC_HOBBY = {
    '130': 
    {
        "profile": "flat",
        "diam": 20.4,
        "shaft_length": 11.55,
        "cover_height": 0.0,
        "thickness": 15.4,
        "bush_height": 1.6,
        "shaft_diam": 2.0,
        "bush_diam": 6.15,
        "height": 25.1
    },
    'R140':
    {
        "profile": "circle",
        "diam": 20.4,
        "shaft_length": 11.55,
        "cover_height": 0.0,
        "step_diam": 12.0,
        "thickness": 15.4,
        "bush_height": 1.6,
        "step_height": 1,
        "shaft_diam": 2.0,
        "bush_diam": 6.15,
        "height": 25.1
    },
    'slotcar':
    {
        "profile": "rect",
        "diam": 23,
        "shaft_length": 8,
        "cover_height": 0.0,
        "step_diam": 12.0,
        "thickness": 15.4,
        "bush_height": 1.6,
        "step_height": 0.0,
        "shaft_diam": 2.0,
        "bush_diam": 4,
        "height": 17
    },
    'flat':
    {
        "profile": "circle",
        "diam": 20.4,
        "shaft_length": 6,
        "cover_height": 0.0,
        "step_diam": 12.0,
        "thickness": 15.4,
        "bush_height": 0.4,
        "step_height": 0.0,
        "shaft_diam": 2.0,
        "bush_diam": 6.15,
        "height": 10
    }
}

# Generate Catalogue
catalogue = JSONCatalogue(
    filename=os.path.join('..', CATALOGUE_NAME),
    clean=True,  # starts fresh
)

# Create Motors 
for (name, params) in DC_HOBBY.items():
    catalogue.add(
        id= name,
        obj=DCMotor(**params),
        criteria={
            'type': 'motor',
            'class': 'dc',
            'diam': params['diam'],
        },
    )
