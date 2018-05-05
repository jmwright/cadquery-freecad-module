
class Catalogue(object):

    def iter_items(self):
        """
        Iterate through every item in the catalogue.

        :return: iterator for every item
        :rtype: generator

        .. note::

            Must be overridden by inheriting class
        """
        raise NotImplementedError("iter_items not implemented for %r" % type(self))
