import os
from airflow.hooks.base import BaseHook
import json
from distutils import util
import logging

LOGGER = logging.getLogger("initializer")

class Credentials:
    def __init__(self, conn_id):
        connection = BaseHook.get_connection(conn_id)

        self.url = connection.host
        self.access_key = connection.login
        self.secret_key = connection.password
        if connection.extra is not None and len(connection.extra) > 0:
            version_check = json.loads(connection.extra).get('ENABLE_VERSION_CHECK', False)
            timeout_ms = json.loads(connection.extra).get('TIMEOUT_MS', 10000)
        else:
            version_check = False
            timeout_ms = 10000
        if isinstance(version_check, str):
            self.do_version_check = bool(util.strtobool(version_check))
        else:
            self.do_version_check = version_check

        LOGGER.info('do_version_check: %s ', self.do_version_check)

        if isinstance(timeout_ms, str):
            self.timeout_ms = int(timeout_ms)
        else:
            self.timeout_ms = timeout_ms

        LOGGER.debug('timeout_ms: %s ', self.timeout_ms)

# setup these 4 env vars in your airflow environment. You can create api keys from torch ui's setting page.
def torch_credentials(conn_id=None):
    if conn_id is None:
        creds = {
            'url': os.getenv('TORCH_CATALOG_URL', 'https://torch.acceldata.local:5443'),
            'access_key': os.getenv('TORCH_ACCESS_KEY', 'OY2VVIN2N6LJ'),
            'secret_key': os.getenv('TORCH_SECRET_KEY', 'da6bDBimQfXSMsyyhlPVJJfk7Zc2gs'),
            'do_version_check': os.getenv('ENABLE_VERSION_CHECK', False),
            'timeout_ms': os.getenv('TIMEOUT_MS', 10000)
        }
    else:
        creds = Credentials(conn_id).__dict__
    return creds
