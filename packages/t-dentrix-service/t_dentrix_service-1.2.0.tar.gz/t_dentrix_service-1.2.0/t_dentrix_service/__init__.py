"""Top-level package for dentrix-service."""

__author__ = """Thoughtful"""
__email__ = "support@thoughtful.ai"
__version__ = "__version__ = '1.2.0'"

from .operations.dentrix_requests import DentrixServiceRequests  # noqa
from .dentrix_service import DentrixService  # noqa
from .ascend_service import AscendService  # noqa
