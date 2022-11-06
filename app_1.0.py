import json
import uuid
import time
from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2
from google.cloud import bigquery
from flask import Flask, request, Response, g, redirect
import logging
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Create table with data which we want see in Responce and in Data Base
def save_request(request_id,request):
    req_data = {}

    req_data['request_id'] = request_id
    uuid = dict(request.cookies).get('uuid')
    if uuid is None:
        req_data['uuid'] = g.request_id
    else:
        req_data['uuid'] = uuid
    req_data['timestamp'] = int(time.time_ns() / 1000)
    req_data['data'] = request.data.decode("utf-8")
    req_data['headers'] = dict(request.headers)
    req_data['headers'].pop('Cookie', None)
    req_data['args'] = dict(request.args)
    req_data['url'] = request.url
    req_data['path'] = request.path
    req_data['remote_addr'] = request.remote_addr
    return req_data

# def save_response(request_id, resp):
#     resp_data = {}
#     # resp_data['request_id'] = request_id
#     # resp_data['uuid'] = resp.headers
#     # resp_data['status'] = resp.status
#     resp_data['headers'] = dict(resp.headers)
#     #resp_data['data'] = dict(resp.get_json())
#     # resp_data['headers'].get('Set-Cookie')
#     print(resp_data)
#     return resp_data
# #

@app.after_request
def after_request(resp):
    cookie = resp.get_json(force=True).get('uuid')
    resp.set_cookie('uuid', value=cookie, max_age=63072000, httponly=True, samesite=None)
    # resp.headers.add('Access-Control-Allow-Origin', '*')
    # resp.headers.add('Access-Control-Allow-Credentials', True)
    resp.data = {}
    # resp_data = save_response(g.request_id, resp)
    # print('Response:: ', json.dumps(resp_data, indent=4))
    return resp

@app.route('/collect',methods=['GET', 'POST'])
def log():
    # Create Hesh for every row
    g.request_id = uuid.uuid1().hex
    # Call function and come back data from request in dict type
    req_data = save_request(g.request_id,request)
    # Make data for Responce function for responce to website

    resp = Response(json.dumps(req_data, indent=4, default=str), mimetype="application/json")
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)
