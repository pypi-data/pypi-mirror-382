from rtnls_registration.registration import Registration
from rtnls_registration.utils import open_image

try:
    from ._version import version as __version__
except Exception:
    __version__ = "0+unknown"