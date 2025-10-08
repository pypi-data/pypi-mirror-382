from importlib.metadata import version as _get_version_str
from ._bode_testing import (
    url,
    request_headers,
    generate_request_id_header,
    generate_user_header,
    generate_admin_header,
)

__version__ = _get_version_str("bode_logger")
