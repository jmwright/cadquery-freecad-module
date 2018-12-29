"""
Copyright 2018 Peter Boin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# =========================== Package Information ===========================
# Version Planning:
#   0.1.x               - Development Status :: 2 - Pre-Alpha
#   0.2.x               - Development Status :: 3 - Alpha
#   0.3.x               - Development Status :: 4 - Beta
#   1.x                 - Development Status :: 5 - Production/Stable
#   <any above>.y       - developments on that version (pre-release)
#   <any above>*.dev*   - development release (intended purely to test deployment)
__version__ = '0.2.1'

__title__ = 'cqparts'
__description__ = 'Hierarchical and deeply parametric models using cadquery'
__url__ = 'https://github.com/fragmuffin/cqparts'

__author__ = 'Peter Boin'
__email__ = 'peter.boin+cqparts@gmail.com'

__license__ = 'GPLv3'

__keywords__ = ['cadquery', 'cad', '3d', 'modeling']

# package_data
import inspect as _inspect
import os as _os
_this_path = _os.path.dirname(_os.path.abspath(_inspect.getfile(_inspect.currentframe())))

__package_data__ = []
# append display/web-templates (recursive)
_web_template_path = _os.path.join(_this_path, 'display', 'web-template')
for (root, subdirs, files) in _os.walk(_web_template_path):
    dir_name = _os.path.relpath(root, _this_path)
    __package_data__.append(_os.path.join(dir_name, '*'))


# not text-parsable
import datetime
_now = datetime.date.today()
__copyright__ = "Copyright {year} {author}".format(year=_now.year, author=__author__)


# =========================== Imports ===========================
__all__ = [
    # Sub-modules
    # bringing scope closer to cqparts for commonly used classes
    'Component',
    'Part',
    'Assembly',

    # Modules
    'catalogue',
    'codec',
    'constraint',
    'display',
    'errors',
    'params',
    'search',
    'utils',
]

# Sub-modules
from .component import Component
from .part import Part
from .assembly import Assembly

from . import catalogue
from . import codec
from . import constraint
from . import display
from . import errors
from . import params
from . import search
from . import utils
