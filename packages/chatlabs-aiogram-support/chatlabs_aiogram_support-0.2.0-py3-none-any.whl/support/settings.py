from os import getenv

from .utils import get_url

BACKEND_URL = get_url(
    schema=getenv('BACKEND_SCHEMA', 'http'),
    host=getenv('BACKEND_HOST', 'localhost'),
    port=getenv('BACKEND_PORT', '8000'),
    path=getenv('BACKEND_SUPPORT_PATH', 'support/'),
)
