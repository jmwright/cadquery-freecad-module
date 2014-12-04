#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains the worker classes/functions executed on the server side.
"""
import logging
import os
import tempfile
import jedi


def _logger():
    """
     Returns the module's logger
    """
    return logging.getLogger(__name__)


def calltips(request_data):
    """
    Worker that returns a list of calltips.

    A calltips is a tuple made of the following parts:
      - module_name: name of the module of the function invoked
      - call_name: name of the function that is being called
      - params: the list of parameter names.
      - index: index of the current parameter
      - bracket_start

    :returns tuple(module_name, call_name, params)
    """
    code = request_data['code']
    line = request_data['line'] + 1
    column = request_data['column']
    path = request_data['path']
    # encoding = request_data['encoding']
    encoding = 'utf-8'
    # use jedi to get call signatures
    script = jedi.Script(code, line, column, path, encoding)
    signatures = script.call_signatures()
    for sig in signatures:
        results = (str(sig.module_name), str(sig.name),
                   [p.description for p in sig.params], sig.index,
                   sig.bracket_start, column)
        # todo: add support for multiple signatures, for that we need a custom
        # widget for showing calltips.
        return results
    return []


def goto_assignments(request_data):
    """
    Go to assignements worker.
    """
    code = request_data['code']
    line = request_data['line'] + 1
    column = request_data['column']
    path = request_data['path']
    # encoding = request_data['encoding']
    encoding = 'utf-8'
    script = jedi.Script(code, line, column, path, encoding)
    try:
        definitions = script.goto_assignments()
    except jedi.NotFoundError:
        pass
    else:
        ret_val = [(d.module_path, d.line - 1 if d.line else None,
                    d.column, d.full_name)
                   for d in definitions]
        return ret_val


_old_definitions = {}


class Definition(object):
    """
    Represents a defined name in a python source code (import, function, class,
    method). Definition usually form a tree limited to 2 levels (we stop at the
    method level).
    """
    def __init__(self, name='', icon='', line=1, column=0, full_name=''):
        #: Icon resource name associated with the definition, can be None
        self.icon = icon
        #: Definition name (name of the class, method, variable)
        self.name = name
        #: The line of the definition in the current editor text
        self.line = line
        #: The column of the definition in the current editor text
        self.column = column
        #: Symbol name + parent name (for methods and class variables)
        self.full_name = full_name
        #: Possible list of children (only classes have children)
        self.children = []
        if self.full_name == "":
            self.full_name = self.name

    def add_child(self, definition):
        """
        Adds a child definition
        """
        self.children.append(definition)

    def to_dict(self):
        """
        Serialises a definition to a dictionary, ready for json.

        Children are serialised recursively.
        """
        ddict = {'name': self.name, 'icon': self.icon,
                 'line': self.line, 'column': self.column,
                 'full_name': self.full_name, 'children': []}
        for child in self.children:
            ddict['children'].append(child.to_dict())
        return ddict

    def from_dict(self, ddict):
        """
        Deserialise the definition from a simple dict.
        """
        self.name = ddict['name']
        self.icon = ddict['icon']
        self.line = ddict['line']
        self.column = ddict['column']
        self.full_name = ddict['full_name']
        self.children[:] = []
        for child_dict in ddict['children']:
            self.children.append(Definition().from_dict(child_dict))
        return self

    def __repr__(self):
        return 'Definition(%r, %r, %r, %r)' % (self.name, self.icon,
                                               self.line, self.column)


def _extract_def(d):
    d_line, d_column = d.start_pos
    # use full name for import type
    if d.type == 'function':
        try:
            params = [p.name for p in d.params]
            name = d.name + '(' + ', '.join(params) + ')'
        except AttributeError:
            name = d.name
    else:
        name = d.name
    definition = Definition(name, icon_from_typename(d.name, d.type),
                            d_line - 1, d_column, d.full_name)
    # check for methods in class or nested methods/classes
    if d.type == "class" or d.type == 'function':
        try:
            sub_definitions = d.defined_names()
            for sub_d in sub_definitions:
                if (d.type == 'function' and sub_d.type == 'function') or \
                        d.type == 'class':
                    definition.add_child(_extract_def(sub_d))
        except AttributeError:
            pass
    return definition


def defined_names(request_data):
    """
    Returns the list of defined names for the document.
    """
    global _old_definitions
    ret_val = []
    path = request_data['path']
    toplvl_definitions = jedi.defined_names(
        request_data['code'], path, 'utf-8')
    for d in toplvl_definitions:
        definition = _extract_def(d)
        if d.type != 'import':
            ret_val.append(definition)
    _logger().debug("Document structure changed %s")
    ret_val = [d.to_dict() for d in ret_val]
    return ret_val


def quick_doc(request_data):
    """
    Worker that returns the documentation of the symbol under cursor.
    """
    code = request_data['code']
    line = request_data['line'] + 1
    column = request_data['column']
    path = request_data['path']
    # encoding = 'utf-8'
    encoding = 'utf-8'
    script = jedi.Script(code, line, column, path, encoding)
    try:
        definitions = script.goto_definitions()
    except jedi.NotFoundError:
        return []
    else:
        ret_val = [d.doc for d in definitions]
        return ret_val


def run_pep8(request_data):
    """
    Worker that run the pep8 tool on the current editor text.

    :returns a list of tuples (msg, msg_type, line_number)
    """
    import pep8
    from pyqode.python.backend.pep8utils import CustomChecker
    WARNING = 1
    code = request_data['code']
    path = request_data['path']
    # setup our custom style guide with our custom checker which returns a list
    # of strings instread of spitting the results at stdout
    pep8style = pep8.StyleGuide(parse_argv=False, config_file=True,
                                checker_class=CustomChecker)
    try:
        results = pep8style.input_file(path, lines=code.splitlines(True))
    except Exception:
        _logger().exception('Failed to run PEP8 analysis with data=%r'
                            % request_data)
        return []
    else:
        messages = []
        for line_number, offset, code, text, doc in results:
            messages.append(('[PEP8] %s' % text, WARNING, line_number - 1))
        return messages


def run_frosted(request_data):
    """
    Worker that run a frosted (the fork of pyflakes) code analysis on the
    current editor text.
    """
    global prev_results
    from frosted import checker
    import _ast
    WARNING = 1
    ERROR = 2
    ret_val = []
    code = request_data['code']
    path = request_data['path']
    encoding = request_data['encoding']
    if not encoding:
        encoding = 'utf-8'
    if not path:
        path = os.path.join(tempfile.gettempdir(), 'temp.py')
    if not code:
        return []
    else:
        # First, compile into an AST and handle syntax errors.
        try:
            tree = compile(code.encode(encoding), path, "exec",
                           _ast.PyCF_ONLY_AST)
        except SyntaxError as value:
            msg = '[pyFlakes] %s' % value.args[0]
            (lineno, offset, text) = value.lineno - 1, value.offset, value.text
            # If there's an encoding problem with the file, the text is None
            if text is None:
                # Avoid using msg, since for the only known case, it
                # contains a bogus message that claims the encoding the
                # file declared was unknown.s
                _logger().warning("[SyntaxError] %s: problem decoding source",
                                  path)
            else:
                ret_val.append((msg, ERROR, lineno))
        else:
            # Okay, it's syntactically valid.  Now check it.
            w = checker.Checker(tree, os.path.split(path)[1])
            w.messages.sort(key=lambda m: m.lineno)
            for warning in w.messages:
                msg = "[pyFlakes] %s: %s" % (
                    warning.type.error_code, warning.message.split(':')[-1])
                line = warning.lineno - 1
                status = (WARNING if warning.type.error_code.startswith('W')
                          else ERROR)
                ret_val.append((msg, status, line))
    prev_results = ret_val
    return ret_val


def icon_from_typename(name, icon_type):
    """
    Returns the icon resource filename that corresponds to the given typename.

    :param name: name of the completion. Use to make the distinction between
        public and private completions (using the count of starting '_')
    :pram typename: the typename reported by jedi

    :returns: The associate icon resource filename or None.
    """
    ICONS = {'CLASS': ':/pyqode_python_icons/rc/class.png',
             'IMPORT': ':/pyqode_python_icons/rc/namespace.png',
             'STATEMENT': ':/pyqode_python_icons/rc/var.png',
             'FORFLOW': ':/pyqode_python_icons/rc/var.png',
             'MODULE': ':/pyqode_python_icons/rc/namespace.png',
             'KEYWORD': ':/pyqode_python_icons/rc/keyword.png',
             'PARAM': ':/pyqode_python_icons/rc/var.png',
             'ARRAY': ':/pyqode_python_icons/rc/var.png',
             'INSTANCEELEMENT': ':/pyqode_python_icons/rc/var.png',
             'INSTANCE': ':/pyqode_python_icons/rc/var.png',
             'PARAM-PRIV': ':/pyqode_python_icons/rc/var.png',
             'PARAM-PROT': ':/pyqode_python_icons/rc/var.png',
             'FUNCTION': ':/pyqode_python_icons/rc/func.png',
             'DEF': ':/pyqode_python_icons/rc/func.png',
             'FUNCTION-PRIV': ':/pyqode_python_icons/rc/func_priv.png',
             'FUNCTION-PROT': ':/pyqode_python_icons/rc/func_prot.png'}
    ret_val = None
    icon_type = icon_type.upper()
    # jedi 0.8 introduced NamedPart class, which have a string instead of being
    # one
    if hasattr(name, "string"):
        name = name.string
    if icon_type == "FORFLOW" or icon_type == "STATEMENT":
        icon_type = "PARAM"
    if icon_type == "PARAM" or icon_type == "FUNCTION":
        if name.startswith("__"):
            icon_type += "-PRIV"
        elif name.startswith("_"):
            icon_type += "-PROT"
    if icon_type in ICONS:
        ret_val = ICONS[icon_type]
    elif icon_type:
        _logger().warning("Unimplemented completion icon_type: %s", icon_type)
    return ret_val


class JediCompletionProvider:
    """
    Provides code completion using the awesome `jedi`_  library

    .. _`jedi`: https://github.com/davidhalter/jedi
    """

    @staticmethod
    def complete(code, line, column, path, encoding, prefix):
        """
        Completes python code using `jedi`_.

        :returns: a list of completion.
        """
        ret_val = []
        try:
            script = jedi.Script(code, line + 1, column, path, encoding)
            completions = script.completions()
            print('completions: %r' % completions)
        except jedi.NotFoundError:
            completions = []
        for completion in completions:
            ret_val.append({
                'name': completion.name,
                'icon': icon_from_typename(
                    completion.name, completion.type),
                'tooltip': completion.description})
        return ret_val
