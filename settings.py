import logging

LOGGING_LEVEL = logging.ERROR

RSOCKS_PROXY_LIST_URL = ""
AWPROXY_PROXY_LIST_URL = ""
NOSOK_PROXY_LIST_URL = ""
BEST_PROXY_LIST_URL = ""

NEUTRINOAPI_URL = 'http://neutrinoapi.com/ip-blocklist'
NEUTRINOAPI_USER_ID = ''
NEUTRINOAPI_API_KEY = ''
REDIS_DB_NEUTRINOAPI = 1
NEUTRINOAPI_CHACHE_EXPIRE = 60 * 60

PROXY_CHECK_URL = ''
PROXY_CHECK_TIMEOUT = 5
PROXY_CHECK_WORKERS = 400

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

FIRST_LOCAL_PORT = 3128

HAPROXY_CONF_PATH = 'etc/forwarding.conf'

EXTERNAL_IP = ''

MAX_PROXIES_IN_COUNTRY = 100

EXTRA_COUNTRIES = {'THA': [], 'TUN': [], 'UKR': [], 'KAZ': [], 'SYR': [], 'EU': [], '-': []}

DOCKER_PATH = "/usr/bin/docker"

DOCKER_CONTAINER_NAME_HAPROXY = "haproxy"

API_PORT = 3000

try:
    from local_settings import *
except ImportError:
    pass
