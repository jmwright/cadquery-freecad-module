#!/usr/bin/env python

# Catalogue Usage example:
#   >>> from cqparts.catalogue import JSONCatalogue
#   >>> import cqparts_motors
#   >>> filename = os.path.join(
#   ...     os.path.dirname(cqparts_motors.__file__),
#   ...     'catalogue', 'stepper-nema.json',
#   ... )
#   >>> catalogue = JSONCatalogue(filename)
#   >>> item = catalogue.get_query()
#   >>> stepper = catalogue.get(item.criteria.size == 17)
#   >>> from cqparts.display import display
#   >>> display(stepper)

import os

import cqparts
from cqparts.catalogue import JSONCatalogue

# Stepper
from cqparts_motors.stepper import Stepper


CATALOGUE_NAME = 'stepper-nema.json'

# Sized motors , build into collection
# http://www.osmtec.com/stepper_motors.htm is a good reference
# sizes 8, 11, 14, 16, 17, 23, 24, 34, 42
# Stepper.class_params().keys()

NEMA_SIZES = {
    8 :  {
        'shaft_length': 10.0,
        'hole_spacing': 15.4,
        'hole_size': 2.0,
        'length': 28.0,
        'width': 20.3,
        'boss_size': 16.0,
        'shaft_diam': 4.0,
        'boss_length': 1.5,
    },
    11 : {
        'shaft_length': 20.0,
        'hole_spacing': 23.0,
        'hole_size': 2.5,
        'length': 31.5,
        'width': 28.2,
        'boss_size': 22.0,
        'shaft_diam': 4.0,
        'boss_length': 2.0,
    },
    14 : {
        'shaft_length': 24.0,
        'hole_spacing': 26.0,
        'hole_size': 3.0,
        'length': 28.0,
        'width': 35.2,
        'boss_size': 22.0,
        'shaft_diam': 5.0,
        'boss_length': 2.0,
    },
    17 : {
        'shaft_length': 24.0,
        'hole_spacing': 31.0,
        'hole_size': 3.0,
        'length': 50.0,
        'width': 42.0,
        'boss_size': 22.0,
        'shaft_diam': 5.0,
        'boss_length': 2.0,
    },
    23 : {
        'shaft_length': 21.0,
        'hole_spacing': 47.0,
        'hole_size': 5.0,
        'length': 56.0,
        'width': 57.0,
        'boss_size': 38.0,
        'shaft_diam': 6.35,
        'boss_length': 1.6,
    },
}


# Generate Catalogue
catalogue = JSONCatalogue(
    filename=os.path.join('..', CATALOGUE_NAME),
    clean=True,  # starts fresh
)

# Create Steppers
for (size, params) in NEMA_SIZES.items():
    catalogue.add(
        id='NEMA_Stepper_%i' % size,
        obj=Stepper(**params),
        criteria={
            'type': 'motor',
            'class': 'stepper',
            'size': size,
        },
    )
