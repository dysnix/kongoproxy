import pickle
import redis
from flask import Flask
from flask import abort
from flask import jsonify

from settings import REDIS_HOST, REDIS_PORT, REDIS_DB

app = Flask(__name__)

redis_conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


@app.route("/countries/")
def countries():
    proxy_count_by_country = pickle.loads(redis_conn.get('proxy_count_by_country'))
    all_countries_count = len(proxy_count_by_country)
    all_proxy_count = pickle.loads(redis_conn.get('all_proxy_count'))

    return jsonify(countries=proxy_count_by_country, all_countries_count=all_countries_count,
                   all_proxy_count=all_proxy_count)


@app.route("/countries/<code>/")
def proxy_list(code):
    countries_connect_info = pickle.loads(redis_conn.get('proxy_countries_connect_info'))
    connect_info = countries_connect_info.get(code)

    if not proxy_list:
        abort(404)

    return jsonify(proxy_list=[connect_info])


@app.route("/countries/<code>/get/")
def proxy_get(code):
    countries_connect_info = pickle.loads(redis_conn.get('proxy_countries_connect_info'))
    connect_info = countries_connect_info.get(code)

    if not proxy_list:
        abort(404)

    return jsonify(proxy=connect_info)


if __name__ == "__main__":
    app.run(port=3000)
