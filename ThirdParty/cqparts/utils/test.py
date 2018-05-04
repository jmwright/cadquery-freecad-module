import unittest
import re
import inspect

from .. import Component, Part, Assembly


class CatalogueTest(unittest.TestCase):

    catalogue = None

    @classmethod
    def create_from(cls, catalogue, add_to={}, id_mangler=None, include_cond=None, exclude_cond=None):
        """
        Create a testcase class that will run generic tests on each item
        in the given :class:`Catalogue <cqparts.catalogue.Catalogue>`.

        :param catalogue: catalogue to generatea tests from
        :type catalogue: :class:`Catalogue <cqparts.catalogue.Catalogue>`
        :param add_to: dict to add resulting class to (usually ``globals()``.
        :type add_to: :class:`dict`
        :param id_mangler: convert item id to a valid python method name
        :type id_mangler: :class:`function`
        :param include_cond: returns true if item should be tested
        :type include_cond: :class:`function`
        :param exclude_cond: returns true if item should not be tested
        :type exclude_cond: :class:`function`

        :return: a testcase class to be discovered and run by :mod:`unittest`
        :rtype: :class:`unittest.TestCase` sub-class (a class, **not** an instance)


        To create a test-case, and add the class with the catalogue's
        name to the ``globals()`` namespace::

            from cqparts.utils.test import CatalogueTest
            from cqparts.catalogue import JSONCatalogue

            catalogue = JSONCatalogue('my_catalogue.json')
            CatalogueTest.create_from(catalogue, add_to=globals())

        Alternatively, to control your class name a bit more traditionally::

            # alternatively
            MyTestCase = CatalogueTest.create_from(catalogue)


        **Test Names / Catalogue IDs**

        Each test is named for its item's ``id``. By default, to translate the
        ids into valid python method names, this is done by replacing any
        *non-alpha-numeric* characters with a ``_``.

        To illustrate with some examples:

        =============== =================== =======================
        id              mangled id          test name
        =============== =================== =======================
        ``abc123``      ``abc123`` (same)   ``test_abc123``
        ``3.14159``     ``3_14159``         ``test_3_14159``
        ``%$#*_yeah!``  ``_____yeah_``      ``test______yeah_``
        ``_(@@)yeah&``  ``_____yeah_``      ``test______yeah_``
        =============== =================== =======================

        So you can see why a python method name of ``test_%$#*_yeah!`` might be
        a problem, which is why this is done. But you may also spot that the
        last 2, although their IDs are unique, the test method names are
        the same.

        To change the way ID's are mangled into test method names, set the
        ``id_mangler`` parameter::

            def mangle_id(id_str):
                return id_str.replace('a', 'X')

            CatalogueTest.create_from(
                catalogue,  # as defined in the previous example
                add_to=globals(),
                id_mangler=mangle_id,
            )


        That would change the first test name to ``test_Xbc123``.


        **Include / Exclude Items**

        If you intend on *including* or *excluding* certain items from the
        testlist, you can employ the ``include_cond`` and/or ``exclude_cond``
        parameters::

            def include_item(item):
                # include item if it has a specific id
                return item.get('id') in ['a', 'b', 'c']

            def exclude_item(item):
                # exclude everything with a width > 100
                return item.get('obj').get('params').get('width', 0) > 100

            CatalogueTest.create_from(
                catalogue,  # as defined in the previous example
                add_to=globals(),
                include_cond=include_item,
                exclude_cond=exclude_item,
            )

        Tests will be created if the following conditions are met:

        =========== =========== =======================
        excluded    included    test case generated?
        =========== =========== =======================
        n/a         n/a         Yes : tests are generated if no include/exclude methods are set
        n/a         ``True``    Yes
        n/a         ``False``   No
        ``True``    n/a         No
        ``False``   n/a         Yes
        ``False``   ``False``   No : inclusion take precedence (or lack thereof)
        ``False``   ``True``    Yes
        ``True``    ``False``   No
        ``True``    ``True``    Yes : inclusion take precedence
        =========== =========== =======================


        """

        # runtime import?
        #   cqparts.utils is intended to be imported from any other cqparts
        #   module... circular dependency is likely, this mitigates that risk.
        from ..catalogue import Catalogue

        if not isinstance(catalogue, Catalogue):
            raise ValueError("invalid catalogue: %r" % catalogue)

        if id_mangler is None:
            id_mangler = lambda n: re.sub(r'[^a-z0-9]', '_', n, flags=re.I)

        # calling module
        caller_frame = inspect.stack()[1][0]
        caller_module = inspect.getmodule(caller_frame).__name__

        cls_body = {
            'catalogue': catalogue,
            '__module__': caller_module,
        }

        def mk_test_method(item_data):
            # Create test method run when test is executed
            def test_meth(self):
                obj = self.catalogue.deserialize_item(item_data)
                self.assertIsInstance(obj, Component)
                if isinstance(obj, Part):
                    obj.build()
                    self.assertGreater(obj.bounding_box.DiagonalLength, 0)
                elif isinstance(obj, Assembly):
                    obj.build()
                    self.assertTrue(bool(obj.components))  # has components

            return test_meth

        # Create 1 test per catalogue item
        for item in catalogue.iter_items():
            #item = <item dict>

            # determine if item requires a testcase
            add_test = not bool(include_cond)
            if exclude_cond and exclude_cond(item):
                add_test = False
            if include_cond and include_cond(item):
                add_test = True

            if add_test:
                # Define test method
                test_meth = mk_test_method(item)

                # Add test method to class body
                test_name = "test_{id}".format(
                    id=id_mangler(item.get('id')),
                )
                test_meth.__name__ = test_name
                cls_body[test_name] = test_meth

        sub_cls = type(
            'CatalogueTest_%s' % catalogue.name,
            (cls,),
            cls_body,
        )

        add_to[sub_cls.__name__] = sub_cls
        return sub_cls
