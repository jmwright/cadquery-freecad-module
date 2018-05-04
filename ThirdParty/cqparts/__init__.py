# =========================== Package Information ===========================
# Version Planning:
#   0.1.x               - Development Status :: 2 - Pre-Alpha
#   0.2.x               - Development Status :: 3 - Alpha
#   0.3.x               - Development Status :: 4 - Beta
#   1.x                 - Development Status :: 5 - Production/Stable
#   <any above>.y       - developments on that version (pre-release)
#   <any above>*.dev*   - development release (intended purely to test deployment)
__version__ = '0.2.0'

__title__ = 'cqparts'
__description__ = 'Hierarchical and deeply parametric models using cadquery'
__url__ = 'https://github.com/fragmuffin/cqparts'

__author__ = 'Peter Boin'
__email__ = 'peter.boin+cqparts@gmail.com'

__license__ = 'GPLv3'

__keywords__ = ['cadquery', 'cad', '3d', 'modeling']

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
