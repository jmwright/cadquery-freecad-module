=========================================
`cqparts` Content Library : Bearings
=========================================

Components
-------------------------

* Ball Bearings
* Tapered Roller Bearings

Examples
-------------------------

`BallBearing`
^^^^^^^^^^^^^^^^^^^^^^^

Create a ball bearing with::

    from cqparts_bearings.ball import BallBearing

    bearing = BallBearing(
        # outer edges
        inner_diam=8,
        outer_diam=20,
        width=5,

        # internal rolling elements
        ball_count=6,
        ball_diam=4,
    )

    # display [optional]
    from cqparts.display import display
    display(bearing)

    # export model to file, various formats available [optional]
    bearing.exporter('gltf')('bearing.gltf')

.. image:: https://fragmuffin.github.io/cqparts/media/img/bearings/ball-example.png

All `BallBearing` parameters are documented
`here <https://fragmuffin.github.io/cqparts/doc/api/cqparts_bearings.html#cqparts_bearings.ball.BallBearing>`_.

The bearing is generated in the following hierarchy:

::

    >>> print(bearing.tree_str())
    <BallBearing: angle=0.0, ball_count=6, ball_diam=4.0, ball_min_gap=0.4, inner_diam=8.0, inner_width=2.0, outer_diam=20.0, outer_width=2.0, rolling_radius=7.0, tolerance=0.001, width=5.0>
     ├○ inner_ring
     ├○ outer_ring
     └─ rolling_elements
         ├○ ball_000
         ├○ ball_001
         ├○ ball_002
         ├○ ball_003
         ├○ ball_004
         └○ ball_005


