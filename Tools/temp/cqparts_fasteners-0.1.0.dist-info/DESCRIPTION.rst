=========================================
`cqparts` Content Library : Fasteners
=========================================

Components
-------------------------

**Base Components**

Few of these are useful on their own, they're used to build more complex parts.

Heads
^^^^^^^^^^^^^^^^^

* Counter-sunk varieties
* Cylindrical varieties
* Externally Driven (eg: hex head)

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/heads-assorted.png

Drive Types
^^^^^^^^^^^^^^^^^

* Cruciform varieties (eg: phillips, frearson)
* Hex (aka: alan) varieties
* Square varieties (eg: single, double, triple square)
* Slotted
* Tamper Resistant varieties

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/drives-assorted.png

Threads
^^^^^^^^^^^^^^^^^^

Standard threads included:

* ISO68 (standard for metric bolts)
* Triangular (eg: for woodscrews)
* Ball Screw

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/threads-assorted.png

Any custom thread can be built by creating a *profile* as a ``Wire`` from within
an object inheriting from the base ``Thread`` class.
(`read more here <https://fragmuffin.github.io/cqparts/doc/api/cqparts_fasteners.solidtypes.threads.html?highlight=build_profile#cqparts_fasteners.solidtypes.threads.base.Thread>`_)

.. note::

    Threads currently bugged by `issue #1 <https://github.com/fragmuffin/cqparts/issues/1>`_.

    Threads are currently simplified to a cylinder until this is fixed.

    Warning when using for 3d printing, threads will not form correctly until the
    bug is fixed... please ``+1`` the issue if you'd like to use properly formed
    threads.

Male Fastener Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Bolts
* Screws

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/male-assorted.png

Female Fastener Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Nuts

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/female-assorted.png

Utilities
-------------------------

The ``Fasteners`` utility assembly can be used to automatically apply fasteners
to arbitrary materials.


For example, with the following 2 detatched blocks:

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/fastener-detatched.png

A ``Fastener`` can be applied to these two blocks to hold them together in a
variety of ways, with varied parameters, such as these 2 exmples:

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/fastener-assorted.png

More detailed examples of customizing a ``Fastener`` are
`documented here <https://fragmuffin.github.io/cqparts/doc/cqparts_fasteners/>`_.

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/fastener-custom-assorted.png


Catalogue(s)
-------------------------

**BoltDepot**

`boltdepot.com <https://www.boltdepot.com/>`_ has an exceptional website for
details of their products, enough to build 3d models accurate enough for most
applications.

At this time, the catalogue you get with this library contains some of the
products for `boltdepot.com <https://www.boltdepot.com/>`_ in the categories:

* Bolts : ``boltdepot-bolts.json``
* Nuts : ``boltdepot-nuts.json``
* Woodscrews : ``boltdepot-woodscrews.json``

**Other Suppliers**

With increased interest in this library I would like to see this list grow, but
at this time, it's just the catalogues listed above.


Examples
-------------------------

Machine Screw
^^^^^^^^^^^^^^^^^^^^^^^

We can create a fastener with many tuned parameters, for this example we'll create
an M3 machine screw, 4mm long, with a domed cheese head, and a 2mm hex drive::

    from cqparts_fasteners.male import MaleFastenerPart

    screw = MaleFastenerPart(
        head=('cheese', {
            'diameter': 4.5,
            'height': 1.5,
            'domed': True,
            'dome_ratio': 0.5,
        }),
        drive=('hex', {
            'depth': 1,
            'width': 2,
        }),
        thread=('iso68', {
            'diameter': 3,  # M3
        }),
        length=4,
    )

    from cqparts.display import display
    display(screw)

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/example-screw.png

Catalogue ``Bolt``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With use of a ``JSONCatalogue`` we can search for all fasteners within that
catalogue that suit certain parameters, such as length, diameter, anything used
as a parameter to build the part.

For this example, we'll explicitly define the product's ``id``, guarenteeing
only one result is returned::

    import os

    from cqparts.catalogue import JSONCatalogue
    import cqparts_fasteners

    catalogue_filename = os.path.join(
        os.path.dirname(cqparts_fasteners.__file__),
        'catalogue',
        'boltdepot-bolts.json',
    )
    catalogue = JSONCatalogue(catalogue_filename)
    item = catalogue.get_query()
    bolt = catalogue.get(item.id == '221')

    from cqparts.display import display
    display(bolt)

This should generate an accurate model for BoltDepot's
`product #221 <https://www.boltdepot.com/Product-Details.aspx?product=221>`_.

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/example-catalogue.png


