
from cqparts.search import (
    find as _find,
    search as _search,
    register as _register,
)
from cqparts.search import common_criteria

module_criteria = {
    'module': __name__,
}

register = common_criteria(**module_criteria)(_register)
search = common_criteria(**module_criteria)(_search)
find = common_criteria(**module_criteria)(_find)
