from qidle.system import embed_package_into_zip

import jedi
import pep8
import pyqode
import pyqode.core
import pyqode.python
import pyqode.qt
import qidle
import frosted
import pies
import cadquery

embed_package_into_zip([jedi, pep8, pyqode.core, pyqode.python, pyqode.qt, qidle, frosted, pies, cadquery],
                       zip_path='/home/jwright/Documents/Projects/CadQuery/cadquery-freecad-module/CadQuery/Tools/libraries.zip')