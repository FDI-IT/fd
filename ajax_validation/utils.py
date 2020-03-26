from django.utils.functional import Promise
from django.utils.encoding import force_unicode
# try:
#     from json import JSONEncoder
# except ImportError:
try:
    from json import JSONEncoder
except ImportError:
    from django.utils.json import JSONEncoder

class LazyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj
