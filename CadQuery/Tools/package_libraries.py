"""
Test if the zip file is working.

Usage:

- python test_zip_file.py gen
- python test_zip_file.py
"""
import sys
import os
ZIP = os.path.join(os.getcwd(), 'libs.zip')

if len(sys.argv) == 2 and sys.argv[1] == 'gen':
    #--- gen zip file
    import jedi, pep8, pyqode, pyqode.core, pyqode.python, pyqode.qt, pygments, frosted, pies, builtins, future, pyflakes, docutils, pint
    from qidle.system import embed_package_into_zip
    embed_package_into_zip([jedi, pep8, pyqode, pyqode.core, pyqode.python,
                            pyqode.qt, pygments, pyflakes, builtins, future, docutils, pint], ZIP)
else:
    # remove all pyqode path from sys.path (to make sure the package are
    # imported from the zip archive)
    for pth in list(sys.path):
        if 'pyqode' in pth:
            print('removing %s' % pth)
            sys.path.remove(pth)

    # importing a pyqode module should fail
    fail = False
    try:
        from pyqode.core.api import code_edit
    except ImportError:
        fail = True
    assert fail is True

    # mount zip file
    sys.path.insert(0, ZIP)
    print(sys.path)

    # test it!
    from pyqode.core.api import code_edit
    print(code_edit.__file__)
    assert ZIP in code_edit.__file__
