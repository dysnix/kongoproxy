import time
import redis
import gevent
import pickle
import logging
import requests
import pycountry
import subprocess
from gevent import monkey, pool
from jinja2 import Environment, FileSystemLoader

from parsers import get_all_proxies
from neutrinoapi import check_neutrinoapi

from settings import PROXY_CHECK_WORKERS, PROXY_CHECK_URL, PROXY_CHECK_TIMEOUT, REDIS_HOST, REDIS_PORT, REDIS_DB, \
    FIRST_LOCAL_PORT, HAPROXY_CONF_PATH, EXTERNAL_IP, MAX_PROXIES_IN_COUNTRY, EXTRA_COUNTRIES, LOGGING_LEVEL, \
    DOCKER_PATH, DOCKER_CONTAINER_NAME_HAPROXY, PROXY_SRC_WHITELIST

monkey.patch_all()

jobs = []
PROXY_COUNT_BY_COUNTRY = {}
PROXY_COUNTRIES_CONNECT_INFO = {}
TMP_DATA = {'all_proxy_count': 0}
PROXY_COUNTRIES = {c.alpha_2: [] for c in pycountry.countries}
PROXY_COUNTRIES.update(EXTRA_COUNTRIES)
redis_conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

env = Environment(loader=FileSystemLoader('templates'))


def proxy_check(proxy):
    proxy_addr = proxy['address']
    proxy_name = proxy['name']

    full_proxy_addr = 'http://{proxy_addr}'.format(proxy_addr=proxy_addr)
    try:
        proxy_host, proxy_port = proxy_addr.split(':')
    except:
        return None

    try:
        r = requests.get(PROXY_CHECK_URL, proxies={'http': full_proxy_addr}, timeout=PROXY_CHECK_TIMEOUT)
        assert r.status_code == 200
        real_ip, country_code = r.text.split(' ')
        response_time = r.elapsed.total_seconds()
    except Exception as e:
        logging.debug(
            'Error check proxy {proxy_addr}: {description}'.format(proxy_addr=full_proxy_addr, description=str(e)))
        return None

    if real_ip == EXTERNAL_IP:
        logging.debug('This proxy is not anonymous: {proxy_addr}'.format(proxy_addr=full_proxy_addr))
        return None

    if country_code not in PROXY_COUNTRIES.keys():
        logging.fatal('Unsupported country {country_code} detected'.format(country_code=country_code))
        return None

    if check_neutrinoapi(real_ip):
        return None

    if not PROXY_COUNTRIES.get(country_code):
        PROXY_COUNT_BY_COUNTRY[country_code] = 0

    result = {
        'povider': proxy_name,
        'real_ip': real_ip,
        'proxy_host': proxy_host,
        'proxy_port': proxy_port,
        'country_code': country_code,
        'name': '{country_code}_{peer_counter}'.format(country_code=country_code,
                                                       peer_counter=PROXY_COUNT_BY_COUNTRY[country_code]),
        'response_time': response_time,
    }

    PROXY_COUNT_BY_COUNTRY[country_code] += 1
    TMP_DATA['all_proxy_count'] += 1

    PROXY_COUNTRIES[country_code].append(result)

    logging.debug('Working proxy found: %s' % proxy_addr)

    return result


def update_haproxy_forward_conf():
    if not PROXY_COUNT_BY_COUNTRY:
        logging.error('Any new proxies found/checked. Abort haproxy reconfigure.')
        return False

    haproxy_conf = open(HAPROXY_CONF_PATH, 'w+')

    country_counter = 1
    for proxy_country in sorted(PROXY_COUNTRIES.keys()):
        if not PROXY_COUNTRIES[proxy_country]:
            country_counter += 1
            logging.debug(
                'Any proxies found in country {proxy_country}. Continue..'.format(proxy_country=proxy_country))
            continue

        PROXY_COUNTRIES[proxy_country] = sorted(
            PROXY_COUNTRIES[proxy_country], key=lambda k: k['response_time'])[:MAX_PROXIES_IN_COUNTRY]

        connect_port = FIRST_LOCAL_PORT + country_counter
        proxy_line = "http://{external_ip}:{connect_port}".format(external_ip=EXTERNAL_IP, connect_port=connect_port)

        PROXY_COUNTRIES_CONNECT_INFO[proxy_country] = {
            "connect_port": connect_port,
            "proxy_line": proxy_line
        }

        template = env.get_template('haproxy.jinja2')
        data = template.render(
            proxy_country=proxy_country,
            connect_port=connect_port,
            peers=PROXY_COUNTRIES[proxy_country],
            proxy_src_whitelist=PROXY_SRC_WHITELIST,
            proxy_check_url=PROXY_CHECK_URL
        )
        haproxy_conf.write(data)

        country_counter += 1

    haproxy_conf.close()

    time.sleep(120)
    haproxy_pid = open("/var/run/haproxy.pid", "r").read().strip()
    subprocess.call(["/usr/sbin/haproxy", "-f", "/etc/haproxy/haproxy.cfg", "-f", "/root/kongoproxy_haproxy/etc/forwarding.conf", "-p", "/var/run/haproxy.pid", "-sf", haproxy_pid])

    logging.info('Haproxy conf updated & service reloaded')


def main():
    logging.basicConfig(level=LOGGING_LEVEL)

    p = pool.Pool(PROXY_CHECK_WORKERS)

    for proxy in get_all_proxies():
        jobs.append(p.spawn(proxy_check, proxy))

    gevent.joinall(jobs)

    update_haproxy_forward_conf()

    redis_conn.set('proxy_countries', pickle.dumps(PROXY_COUNTRIES))
    redis_conn.set('proxy_countries_connect_info', pickle.dumps(PROXY_COUNTRIES_CONNECT_INFO))
    redis_conn.set('proxy_count_by_country', pickle.dumps(PROXY_COUNT_BY_COUNTRY))
    redis_conn.set('all_proxy_count', pickle.dumps(TMP_DATA['all_proxy_count']))

    print('Done: %d proxies in %d countries saved to redis & haproxy conf' % (TMP_DATA['all_proxy_count'],
                                                                            len(PROXY_COUNT_BY_COUNTRY)))


if __name__ == '__main__':
    main()
