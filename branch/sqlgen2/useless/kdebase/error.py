import os
from kdeui import KMessageBox

from useless.base.util import excepthook_message
from useless.base.util import traceback_to_string

class MethodNotImplementedError(NotImplementedError):
    def __init__(self, parent, message):
        KMessageBox.error(parent, message)

def excepthook(type, value, tracebackobj):
    """In PyKDE applications, you can replace sys.excepthook
    with this function.  It will display a detailed error
    dialog displaying a traceback for the exception.  If the
    DEBUG environment variable is present, a debugger is
    started."""
    tbinfo = traceback_to_string(tracebackobj)
    if 'DEBUG' in os.environ:
        separator = '=' * 80
    else:
        separator = '-' * 80
    msg = '%s: %s' % (type, value)
    msg = '%s\n%s\n%s' % (separator, msg, separator)
    KMessageBox.detailedError(None, msg, tbinfo)
    if 'DEBUG' in os.environ:
        import pdb
        pdb.pm()
        
