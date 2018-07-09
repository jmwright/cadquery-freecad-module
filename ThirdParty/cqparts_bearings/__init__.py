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
__version__ = '0.1.0'

__title__ = 'cqparts_bearings'
__description__ = 'Bearings content library for cqparts'
__url__ = 'https://github.com/fragmuffin/cqparts'

__author__ = 'Peter Boin'
__email__ = 'peter.boin+cqparts@gmail.com'

__license__ = 'Apache Public License 2.0'

__keywords__ = ['cadquery', 'cad', '3d', 'modeling', 'bearings']

# not text-parsable
import datetime
_now = datetime.date.today()
__copyright__ = "Copyright {year} {author}".format(year=_now.year, author=__author__)


# =========================== Functional ===========================

from cqparts.search import (
    register as _register,
    search as _search,
    find as _find,
)
from cqparts.search import common_criteria

module_criteria = {
    'module': __name__,
}

register = common_criteria(**module_criteria)(_register)
search = common_criteria(**module_criteria)(_search)
find = common_criteria(**module_criteria)(_find)
