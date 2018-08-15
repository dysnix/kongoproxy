import re
import redis
import pickle
import logging
import requests
from settings import REDIS_HOST, REDIS_PORT, REDIS_DB_NEUTRINOAPI, NEUTRINOAPI_URL, NEUTRINOAPI_USER_ID, \
    NEUTRINOAPI_API_KEY, NEUTRINOAPI_CHACHE_EXPIRE

redis_conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB_NEUTRINOAPI)


def check_neutrinoapi(ip):
    cached_result = redis_conn.get(ip)
    if cached_result:
        return pickle.loads(cached_result)

    params = {
        'user-id': NEUTRINOAPI_USER_ID,
        'api-key': NEUTRINOAPI_API_KEY,
        'ip': ip
    }

    try:
        result = requests.post(NEUTRINOAPI_URL, data=params)
    except Exception as e:
        logging.error('Error getting proxy info from neutrinoapi service: %s' % str(e))
        return True

    if not result.status_code == 200:
        logging.error('Error neutrinoapi response: %s' % result.text)
        return True

    data = result.json()
    check_result = [k for k in data.keys() if re.search('^is-.*', k) and data[k]] or None

    redis_conn.setex(ip, NEUTRINOAPI_CHACHE_EXPIRE, pickle.dumps(check_result))

    if check_result:
        logging.warning('IP {ip} is listed in: {listed_blackilists}'.format(
            ip=ip, listed_blackilists=", ".join(check_result))
        )
        return True

    return False
