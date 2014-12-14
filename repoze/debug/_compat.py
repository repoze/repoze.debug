try:
    STRING_TYPES = (str, unicode)
except NameError: #pragma NO COVER Python >= 3.0
    STRING_TYPES = (str,)
    TEXT = str
else:
    TEXT = unicode

try:
    import thread
except ImportError:                 #pragma NO COVER Python 3.x
    import _thread as thread

