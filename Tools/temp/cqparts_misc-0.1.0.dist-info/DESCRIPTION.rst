====================================================
`cqparts` Content Library : Miscellaneous
====================================================

Components
-------------------------

Primative Shapes
^^^^^^^^^^^^^^^^^^^^

Primative shapes to build or test ideas quickly

* Cube
* Box
* Sphere
* Cylinder

Indicators
^^^^^^^^^^^^^^^^^^^^

These components can be used in assemblies during development as a means
to debug your part placement, and to demonstrate ``Mate`` coordinate systems.

* Coordinate System Indicator
* Planar Indicator

.. image:: https://fragmuffin.github.io/cqparts/media/img/misc/indicators.png


Examples
-------------------------

Use indicator on a primative
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To illustrate how an inciator can be used to show where a ``Mate`` is on a
``Part``, we'll create a simple ``Assembly``::

    import cqparts
    from cqparts.constraint import Fixed, Coincident

    from cqparts_misc.basic.indicators import CoordSysIndicator
    from cqparts_misc.basic.primatives import Box


    class MyAsm(cqparts.Assembly):
        def make_components(self):
            return {
                'box': Box(length=30, width=20, height=10),
                'indicator': CoordSysIndicator(),
            }

        def make_constraints(self):
            return [
                Fixed(self.components['box'].mate_origin),  # fix at world origin
                Coincident(
                    self.components['indicator'].mate_origin,
                    self.components['box'].mate_neg_y,
                ),
            ]


    from cqparts.display import display
    display(MyAsm())

.. image:: https://fragmuffin.github.io/cqparts/media/img/misc/example-coordsys-indicator.png

From this we can see that the ``mate_neg_y`` mate has:

* its Z-axis along the world -Y-axis, and
* its X-axis along the world Z-axis.


