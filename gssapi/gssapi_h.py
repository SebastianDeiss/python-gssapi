from __future__ import absolute_import

import platform

_currentplatform = platform.system()

if _currentplatform == 'Darwin':
    from .mac.gssapi_h import *
elif _currentplatform == 'Linux':
    from .linux.gssapi_h import *
else:
    raise NotImplemented("Support for {0} platform is not (yet) implemented".format(_currentplatform))
