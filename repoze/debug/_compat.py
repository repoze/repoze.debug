try:
    import gzip
except ImportError:  # pragma: no cover system w/o gzip??
    gzip = None

try:
    from html import escape
except ImportError:  # pragma: no cover Python3
    from cgi import escape

try:
    from cPickle import Pickler
    from cPickle import Unpickler
except ImportError:  # pragma: no cover Python3
    from pickle import Pickler
    from pickle import Unpickler

try:
    import thread
except ImportError:  # pragma: no cover Python 3.x
    import _thread as thread

try:
    from urllib import quote
except: #pragma NO COVER Py3k
    from urllib.parse import quote

try:
    STRING_TYPES = (str, unicode)
except NameError:    # pragma: no cover Python >= 3.0
    STRING_TYPES = (str,)
    TEXT = str
else:
    TEXT = unicode
