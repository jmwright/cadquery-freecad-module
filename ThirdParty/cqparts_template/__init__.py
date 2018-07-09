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

__release_ready__ = False  # TODO: remove to stop blocking build

__title__ = "cqparts_<lib_name>"  # TODO
__description__ = "<brief description>"  # TODO
__url__ = "<library url>"  # TODO

__version__ = "0.1.0"
__author__ = "<your name>"  # TODO


# ------ Registration
from cqparts.search import (
    find as _find,
    search as _search,
    register as _register,
)
from cqparts.search import common_criteria

module_criteria = {
    'library': __name__,
}

register = common_criteria(**module_criteria)(_register)
search = common_criteria(**module_criteria)(_search)
find = common_criteria(**module_criteria)(_find)
