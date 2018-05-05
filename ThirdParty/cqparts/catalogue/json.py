
import tinydb
import os
import re
from distutils.version import LooseVersion

from .. import __version__
from .. import Component
from ..errors import SearchError, SearchNoneFoundError, SearchMultipleFoundError
from ..params import ParametricObject
from ..utils import property_buffered

from .catalogue import Catalogue


class JSONCatalogue(Catalogue):
    """
    Catalogue with JSON storage using :mod:`tinydb`.

    For more information, read :ref:`cqparts.catalogue`.
    """

    # database information:
    # remember: before aligning the above version, check information below...
    # if changes have been made to this class, the below version should
    # be incremented.
    _version = '0.1'
    _dbinfo_name = '_dbinfo'

    def __init__(self, filename, clean=False):
        """
        :param filename: name of catalogue file
        :type filename: :class:`str`
        :param clean: if set, catalogue is deleted, to be re-populatd from scratch
        :type clean: :class:`bool`

        If a new database is created, a ``_dbinfo`` table is added with
        version & module information to assist backward compatability.
        """
        self.filename = filename
        self.name = re.sub(
            r'[^a-z0-9\._\-+]', '_',
            os.path.splitext(os.path.basename(filename))[0],
            flags=re.IGNORECASE,
        )
        if clean and os.path.exists(self.filename):
            with open(self.filename, 'w'):
                pass  # remove file's content, then close
        self.db = tinydb.TinyDB(filename, default_table='items')
        self.items = self.db.table('items')

        if self._dbinfo_name not in self.db.tables():
            # info table does not exist; database is new.
            self._dbinfo_table.insert({
                'module': type(self).__module__,
                'name': type(self).__name__,
                'ver': self._version,
                'lib': 'cqparts',
                'lib_version': __version__,
            })

    def close(self):
        """
        Close the database, and commit any changes to file.
        """
        self.db.close()

    @property
    def _dbinfo_table(self):
        return self.db.table(self._dbinfo_name)

    @property
    def dbinfo(self):
        """
        Database information (at time of creation), mainly intended
        for future-proofing.

        :return: information about database's initial creation
        :rtype: :class:`dict`
        """

        return self._dbinfo_table.all()[0]

    def get_query(self):
        """
        Passthrough to return a :class:`tinydb.Query` instance.
        (mostly implemented so importing :mod:`tinydb` is not mandatory to
        search the catalogue)

        :return: :mod:`tinydb` query instance
        :rtype: :class:`tinydb.Query`
        """
        return tinydb.Query()

    # ------- Searching -------
    def search(self, *args, **kwargs):
        """
        Passthrough to :meth:`Table.search() <tinydb.database.Table.search>`
        for the ``items`` table.

        So ``catalogue.search(...)`` equivalent to
        ``catalogue.db.table('items').search(...)``.

        :return: entries in ``items`` table that positively match given search criteria.
        :rtype: :class:`list` of ``items`` table entries
        """
        return self.items.search(*args, **kwargs)

    def find(self, *args, **kwargs):
        """
        Performs the same action as :meth:`search` but asserts a single result.

        :return:

        :raises SearchNoneFoundError: if nothing was found
        :raises SearchMultipleFoundError: if more than one result is found
        """
        result = self.search(*args, **kwargs)

        if len(result) == 0:
            raise SearchNoneFoundError("nothing found")
        elif len(result) > 1:
            raise SearchMultipleFoundError("more than one result found")

        return result[0]

    # ------- Adding items -------
    def add(self, id, obj, criteria={}, force=False, _check_id=True):
        """
        Add a :class:`Component <cqparts.Component>` instance to the database.

        :param id: unique id of entry, can be anything
        :type id: :class:`str`
        :param obj: component to be serialized, then added to the catalogue
        :type obj: :class:`Component <cqparts.Component>`
        :param criteria: arbitrary search criteria for the entry
        :type criteria: :class:`dict`
        :param force: if ``True``, entry is forcefully overwritten if it already
                      exists. Otherwise an exception is raised
        :type force: :class:`bool`
        :param _check_id: if ``False``, duplicate ``id`` is not tested
        :type _check_id: :class:`bool`

        :raises TypeError: on parameter issues
        :raises ValueError: if a duplicate db entry is detected (and ``force``
                            is not set)

        :return: index of new entry
        :rtype: :class:`int`
        """
        # Verify component
        if not isinstance(obj, Component):
            raise TypeError("can only add(%r), component is a %r" % (
                Component, type(obj)
            ))

        # Serialize object
        obj_data = obj.serialize()

        # Add to database
        q = tinydb.Query()
        if (force or _check_id) and self.items.count(q.id == id):
            if force:
                self.items.remove(q.id == id)
            else:
                raise ValueError("entry with id '%s' already exists" % (id))

        index = self.items.insert({
            'id': id,  # must be unique
            'criteria': criteria,
            'obj': obj_data,
        })

        return index

    def iter_items(self):
        """
        Iterate through all items in the catalogue

        :return: iterator for each item
        :rtype: generator
        """
        for item in self.items.all():
            yield item

    # ------- Getting Items -------
    def deserialize_item(self, data):
        """
        Create a :class:`Component <cqparts.Component>` from a database
        search result.

        :param data: result from :meth:`find`, or an element of :meth:`search`
        :type data: :class:`dict`
        :return: deserialized object instance
        :rtype: :class:`Component <cqparts.Component>`
        """
        return ParametricObject.deserialize(data.get('obj'))

    def get(self, *args, **kwargs):
        """
        Combination of :meth:`find` and :meth:`deserialize_item`;
        the result from :meth:`find` is deserialized and returned.

        Input is a :mod:`tinydb` query.

        :return: deserialized object instance
        :rtype: :class:`Component <cqparts.Component>`
        """
        result = self.find(*args, **kwargs)
        return self.deserialize_item(result)
