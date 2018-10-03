import requests
from settings import AWPROXY_PROXY_LIST_URL, RSOCKS_PROXY_LIST_URL, NOSOK_PROXY_LIST_URL, BEST_PROXY_LIST_URL, ADVANCED_PROXY_LIST_URL

def get_provider_proxies(url, name):
    html = requests.get(url).text
    return [{"name": name, "address": proxy} for proxy in html.strip().replace('\r', '').split('\n')]

def get_all_proxies():
    #data = get_provider_proxies(ADVANCED_PROXY_LIST_URL, "advanced")
    data = get_provider_proxies(AWPROXY_PROXY_LIST_URL, "awproxy")
    #data += get_provider_proxies(RSOCKS_PROXY_LIST_URL, "rsocks")
    data += get_provider_proxies(NOSOK_PROXY_LIST_URL, "nosok")
    #data += get_provider_proxies(BEST_PROXY_LIST_URL, "best")
    
    return data
