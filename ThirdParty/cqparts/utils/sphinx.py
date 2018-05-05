"""
This module is only to be referenced from your project's sphinx autodoc
configuration.

http://www.sphinx-doc.org/en/stable/ext/autodoc.html
"""

from ..params import ParametricObject, Parameter


def _add_lines(lines, new_lines, prepend=False, separator=True):
    # Adding / Removing Lines:
    #   sphinx callbacks require the passed ``lines`` parameter to have it's
    #   initial ``id(lines)``, so doing things like ``lines = ['new thing'] + lines``
    #   changes it's ``id`` (allocating new memory), and the new lines list is
    #   forgotten and garbage collected (... sigh).
    #
    #   So the only way to *prepend* / *append* text to the ``lines`` parameter is
    #   to use ``lines.insert(0, new_line)`` / ``lines.append(new_line`` respectively.
    #
    #   To remove lines, use ``del lines[0]``
    #
    #   If in doubt: ``id(lines)`` should return the same number at the start, and
    #   end of the function call.
    has_original_content = bool(lines)
    if prepend:
        # add to the beginning of __doc__
        for (i, new_line) in enumerate(new_lines):
            lines.insert(i, new_line)
        if separator and (new_lines and has_original_content):
            # add blank line between newly added lines and original content
            lines.insert(len(new_lines), '')
    else:
        # append to the end of __doc__
        if separator and (new_lines and has_original_content):
            # add blank line between newly added lines and original content
            lines.append('')
        for new_line in new_lines:
            lines.append(new_line)


def _cls_name(cls):
    return "{}.{}".format(cls.__module__, cls.__name__)


# -------------- autodoc-process-docstring --------------
def add_parametric_object_params(prepend=False, hide_private=True):
    """
    Add :class:`ParametricObject <cqparts.params.ParametricObject>` parameters
    in a list to the *docstring*.

    This is only intended to be used with *sphinx autodoc*.

    In your *sphinx* ``config.py`` file::

        from cqparts.utils.sphinx import add_parametric_object_params
        def setup(app):
            app.connect("autodoc-process-docstring", add_parametric_object_params())

    Then, when documenting your :class:`Part <cqparts.Part>` or
    :class:`Assembly <cqparts.Assembly>` the
    :class:`ParametricObject <cqparts.params.ParametricObject>` parameters
    will also be documented in the output.

    :param prepend: if True, parameters are added to the beginning of the *docstring*.
                    otherwise, they're appended at the end.
    :type prepend: :class:`bool`
    :param hide_private: if True, parameters with a ``_`` prefix are not documented.
    :type hide_private: :class:`bool`
    """

    from ..params import ParametricObject

    def param_lines(app, obj):
        params = obj.class_params(hidden=(not hide_private))

        # Header
        doc_lines = []
        if params:  # only add a header if it's relevant
            doc_lines += [
                ":class:`ParametricObject <cqparts.params.ParametricObject>` constructor parameters:",
                "",
            ]

        for (name, param) in sorted(params.items(), key=lambda x: x[0]):  # sort by name
            doc_lines.append(':param {name}: {doc}'.format(
                name=name, doc=param._param(),
            ))
            doc_lines.append(':type {name}: {doc}'.format(
                name=name, doc=param._type(),
            ))

        return doc_lines

    # Conditions for running above `param_lines` function (in order)
    conditions = [  # (all conditions must be met)
        lambda o: type(o) == type,
        lambda o: o is not ParametricObject,
        lambda o: issubclass(o, ParametricObject),
    ]

    def callback(app, what, name, obj, options, lines):
        # sphinx callback
        # (this method is what actually gets sent to the sphinx runtime)
        if all(c(obj) for c in conditions):
            new_lines = param_lines(app, obj)
            _add_lines(lines, new_lines, prepend=prepend)

    return callback


def add_search_index_criteria(prepend=False):
    """
    Add the search criteria used when calling :meth:`register() <cqparts.search.register>`
    on a :class:`Component <cqparts.Component>` as a table to the *docstring*.

    This is only intended to be used with *sphinx autodoc*.

    In your *sphinx* ``config.py`` file::

        from cqparts.utils.sphinx import add_search_index_criteria
        def setup(app):
            app.connect("autodoc-process-docstring", add_search_index_criteria())

    Then, when documenting your :class:`Part <cqparts.Part>` or
    :class:`Assembly <cqparts.Assembly>` the
    search criteria will also be documented in the output.

    :param prepend: if True, table is added to the beginning of the *docstring*.
                    otherwise, it's appended at the end.
    :type prepend: :class:`bool`
    """

    from ..search import class_criteria
    from .. import Component

    COLUMN_INFO = [
        # (<title>, <width>, <method>),
        ('Key', 50, lambda k, v: "``%s``" % k),
        ('Value', 10, lambda k, v: ', '.join("``%s``" % w for w in v)),
    ]  # note: last column width is irrelevant

    def param_lines(app, obj):
        doc_lines = []

        criteria = class_criteria.get(obj, {})
        row_seperator = ' '.join(('=' * w) for (_, w, _) in COLUMN_INFO)

        # Header
        if criteria:  # only add a header if it's relevant
            doc_lines += [
                "**Search Criteria:**",
                "",
                "This object can be found with :meth:`find() <cqparts.search.find>` ",
                "and :meth:`search() <cqparts.search.search>` using the following ",
                "search criteria.",
                "",
                row_seperator,
                ' '.join((("%%-%is" % w) % t) for (t, w, _) in COLUMN_INFO),
                row_seperator,
            ]

        # Add criteria
        for (key, value) in sorted(criteria.items(), key=lambda x: x[0]):
            doc_lines.append(' '.join(
                ("%%-%is" % w) % m(key, value)
                for (_, w, m) in COLUMN_INFO
            ))

        # Footer
        if criteria:
            doc_lines += [
                row_seperator,
                "",
            ]

        return doc_lines

    # Conditions for running above `param_lines` function (in order)
    conditions = [  # (all conditions must be met)
        lambda o: type(o) == type,
        lambda o: o is not Component,
        lambda o: issubclass(o, Component),
    ]

    def callback(app, what, name, obj, options, lines):
        # sphinx callback
        # (this method is what actually gets sent to the sphinx runtime)
        if all(c(obj) for c in conditions):
            new_lines = param_lines(app, obj)
            _add_lines(lines, new_lines, prepend=prepend)

    return callback


# -------------- autodoc-skip-member --------------
def skip_class_parameters():
    """
    Can be used with :meth:`add_parametric_object_params`, this removes
    duplicate variables cluttering the sphinx docs.

    This is only intended to be used with *sphinx autodoc*

    In your *sphinx* ``config.py`` file::

        from cqparts.utils.sphinx import skip_class_parameters
        def setup(app):
            app.connect("autodoc-skip-member", skip_class_parameters())
    """

    from ..params import Parameter

    def callback(app, what, name, obj, skip, options):
        if (what == 'class') and isinstance(obj, Parameter):
            return True  # yes, skip this object
        return None

    return callback
