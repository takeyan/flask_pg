# from flask import Flask, request, jsonify
from flask import Flask, request, render_template, make_response
from datetime import datetime
import os
import syslog
import json
import urllib.parse
from logging import getLogger, StreamHandler, DEBUG

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


@app.route('/api/<key>', methods=['POST'])
def post_api(key):
    resp_data = request.get_json()

    log = resp_data.get('log')

    resp_data["api"] = key
    resp_data["K8Senv"] = k8s_env()
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
    resp_data["timestamp"] = datetime.now().isoformat()

    if log[0].upper() == "Y":
        logger.debug('### api04.py -- GET:{}'.format(resp_data))

    return resp_data


if __name__ == '__main__':
    app.run(debug=True)
