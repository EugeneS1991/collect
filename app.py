import json
import uuid
import time
import datetime
from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2
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

def tasks(request_id,task_request):
    data = task_request
    client = tasks_v2.CloudTasksClient()
    project = 'abiding-circle-361417'
    queue = 'cloud-run'
    location = 'europe-west1'
    url = 'https://my-application-process-a5nbasjb4q-ew.a.run.app/process'
    payload = data  # or {'param': 'value'} for application/json
    in_seconds = 10
    task_name = request_id
    deadline = 100
    # Construct the fully qualified queue name.
    parent = client.queue_path(project, location, queue)

    # Construct the request body.
    task = {
        "http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url,  # The full url path that the task will be sent to.
        }
    }
    if payload is not None:
        if isinstance(payload, dict):
            # Convert dict to JSON string
            payload = json.dumps(payload)
            # specify http content-type to application/json
            task["http_request"]["headers"] = {"Content-type": "application/json"}

        # The API expects a payload of type bytes.
        converted_payload = payload.encode()

        # Add the payload to the request.
        task["http_request"]["body"] = converted_payload

    if in_seconds is not None:
        # Convert "seconds from now" into an rfc3339 datetime string.
        d = datetime.datetime.utcnow() + datetime.timedelta(seconds=in_seconds)

        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        # Add the timestamp to the tasks.
        task["schedule_time"] = timestamp

    if task_name is not None:
        # Add the name to tasks.
        task["name"] = client.task_path(project, location, queue, task_name)

    if deadline is not None:
        # Add dispatch deadline for requests sent to the worker.
        duration = duration_pb2.Duration()
        duration.FromSeconds(deadline)
        task["dispatch_deadline"] = duration

    # Use the client to build and send the task.
    response = client.create_task(request={"parent": parent, "task": task})
    print("Created task {}".format(response.name))

    return "Created task {}".format(response.name)

@app.route('/collect',methods=['GET', 'POST'])
def log():
    # Create Hesh for every row
    g.request_id = uuid.uuid1().hex
    # Call function and come back data from request in dict type
    raw_req_data = save_request(g.request_id,request)
    task_request = tasks(g.request_id,raw_req_data)
    # Make data for Responce function for responce to website
    resp = Response(json.dumps(raw_req_data, indent=4, default=str), mimetype="application/json")
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)
