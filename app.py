import json
import uuid
import time
from google.cloud import bigquery
import requests
from flask import Flask, request, Response, g, redirect
from google.cloud import tasks_v2
app = Flask(__name__)
# Create table with data which we want see in Responce and in Data Base
def save_request(request_id,request):
    req_data = {}
    req_data['timestamp'] = int(time.time_ns() / 1000)
    req_data['request_id'] = request_id
    req_data['endpoint'] = request.endpoint
    req_data['method'] = request.method
    req_data['cookies'] = request.cookies
    req_data['data'] = request.data.decode("utf-8")
    req_data['headers'] = dict(request.headers)
    req_data['headers'].pop('Cookie', None)
    req_data['args'] = request.args
    req_data['form'] = request.form
    req_data['url'] = request.url
    req_data['path'] = request.path
    req_data['remote_addr'] = request.remote_addr
    return req_data

# def save_response(request_id, resp):
#     resp_data = {}
#     resp_data['request_id'] = request_id
#     resp_data['status_code'] = resp.status_code
#     resp_data['status'] = resp.status
#     resp_data['headers'] = dict(resp.headers)
#     resp_data['data'] = dict(resp.get_json())
#     return resp_data
#

@app.route('/',methods=['GET', 'POST'])
def log():
    # Create Hesh for every row
    g.request_id = uuid.uuid1().hex
    # Call function and come back data from request
    raw_req_data = save_request(g.request_id,request)
    # Make data for Responce function
    # resp = Response(json.dumps(raw_req_data, indent=4, default=str), mimetype="application/json")

    url = 'http://127.0.0.1:80/process'
    headers = {'Content-type': 'text/html; charset=UTF-8'}
    response = requests.post(url, data=json.dumps(raw_req_data), headers=headers)


    # json.dumps(raw_req_data)
# # -------------------------------------------BQ---------------------------------------
# Create list for convert it in json and poot to BQ
#     rows_to_insert = []
#     rows_to_insert.append({
#         'data': json.dumps(raw_req_data),
#         'request_id': raw_req_data.get('request_id'),
#         'ad_timestamp': int(time.time_ns() / 1000)
#     })

    # GOOGLE_APPLICATION_CREDENTIALS = 'streaming-bq-e8b723d246f1.json'
    # bigquery_client = bigquery.Client.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)
    # dataset_id = bigquery_client.dataset('cloudRun')
    # table_id = dataset_id.table('cloud_run')
    # errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
    # if errors == []:
    #     print("New rows have been added.")
    # else:
    #     print("Encountered errors while inserting rows: {}".format(errors))
# ------------------------------------------------------------------------------------

    return {'test': response.status_code}

if __name__ == '__main__':
    app.run(debug=False, port=8080, host='0.0.0.0')
