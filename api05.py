# from flask import Flask, request, jsonify
from flask import Flask, request, render_template, make_response
from datetime import datetime
import os
import syslog
import json
import urllib.parse
from logging import getLogger, StreamHandler, DEBUG
import psycopg2
import psycopg2.extras

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 日本語文字化け対策

def k8s_env():
    json_dict = {
        'podname' :  os.getenv('K8S_POD_NAME','null'),
        'pod_ip' :      os.getenv('K8S_POD_IP','null'),
        'nodename' : os.getenv('K8S_NODE_NAME','null')
    }
    return json_dict

def select_pg(request):
    select_template = "SELECT * from {0} where {1} = '{2}' ;"

    tab_name = request.args.get('table')
    key_name= request.args.get('key')
    key_value = request.args.get('value')
    select_st = select_template.format(tab_name, key_name, key_value)

    conn = psycopg2.connect("host=172.18.0.72 port=5432 dbname=postgres user=postgres password=secret")
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(select_st)

    results = dict_cur.fetchall()
    dict_result = []
    for row in results:
        dict_result.append(dict(row))

    conn.commit()
    dict_cur.close()

    # print(dict_result)
    return dict_result


@app.route('/api/<key>', methods=['POST'])
def post_api(key):
    resp_data = request.get_json()

    log = resp_data.get('log')

    resp_data["api"] = key
    resp_data["K8Senv"] = k8s_env()
    resp_data["postgresql"] = select_pg(request)
    resp_data["timestamp"] = datetime.now().isoformat()

    if (resp_data["log"][0]).upper() == "Y":
        logger.debug('### api04.py -- POST:{}'.format(resp_data))

    return resp_data


@app.route('/api/<key>', methods=['GET'])
def get_api(key):

    query_params = request.args.to_dict()

    log = request.args.get('log')

    resp_data = query_params
    resp_data["api"] = key
    resp_data["K8Senv"] = k8s_env()
    resp_data["postgresql"] = select_pg(request)
    resp_data["timestamp"] = datetime.now().isoformat()

    if log[0].upper() == "Y":
        logger.debug('### api04.py -- GET:{}'.format(resp_data))

    return resp_data


if __name__ == '__main__':
    app.run(debug=True)



