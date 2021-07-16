import requests
import aiohttp
from aiohttp_requests import requests as asyncrequests
import time
import os
import json
from uuid import uuid4

endpoint = 'https://api.booste.io/'
# Endpoint override for development
if 'BOOSTE_URL' in os.environ:
    print("Dev Mode")
    if os.environ['BOOSTE_URL'] == 'local':
        endpoint = 'http://localhost/'
    else:
        endpoint = os.environ['BOOSTE_URL']
    print("Hitting endpoint:", endpoint)


# identify machine for blind use
cache_path = os.path.abspath(os.path.join(os.path.expanduser('~'),".booste","cache.json"))
if os.path.exists(cache_path):
    with open(cache_path, "r") as file:
        cache = json.load(file)
else:
    cache = {}
    cache['machine_id'] = str(uuid4())
    os.makedirs(os.path.join(os.path.expanduser('~'), ".booste"), exist_ok=True)
    with open(cache_path, "w+") as file:
        json.dump(cache, file)


client_error = {
    "OOB" : "Client error: {}={} is out of bounds.\n\tmin = {}\n\tmax = {}"
}

# THE MAIN FUNCTIONS
# ___________________________________


def run_main(api_key, model_key, model_parameters):
    task_id = call_start_api(api_key, model_key, model_parameters)
    # Just hardcode intervals
    while True:
        dict_out = call_check_api(api_key, task_id)
        if dict_out['data']['taskStatus'] == "Done":

            if "output" in dict_out['data']['taskOut']:
                return dict_out['data']['taskOut']["output"]
            else:
                return dict_out['data']['taskOut']
def start_main(api_key, model_key, model_parameters):
    task_id = call_start_api(api_key, model_key, model_parameters)
    return task_id
def check_main(api_key, task_id):
    dict_out = call_check_api(api_key, task_id)
    return dict_out


# THE API CALLING FUNCTIONS
# ________________________

# Takes in start params, returns task ID
def call_start_api(api_key, model_key, model_parameters):
    global endpoint
    route_start = "api/task/start/v1/"
    url_start = endpoint + route_start

    payload = {
        "id": str(uuid4()),
        "created": int(time.time()),
        "data": {
            "apiKey" : api_key,
            "modelKey" : model_key,
            "modelParameters" : model_parameters
        }
    }
    response = requests.post(url_start, json=payload)
    if response.status_code != 200:
        raise Exception("Server error: Booste inference server returned status code {}\n{}".format(
            response.status_code, response.json()['message']))
    try:
        out = response.json()
        if not out['success']:
            raise Exception(f"Booste inference start call failed with message: {out.message}")
        task_id = out['data']['taskID']
        return task_id
    except:
        raise Exception("Server error: Failed to return taskID")


# The bare async checker. Used by both gpt2_sync_main (automated) and async (client called)
# Takes in task ID, returns reformatted dict_out with Status and Output
def call_check_api(api_key, task_id):
    global endpoint
    route_check = "api/task/check/v1/"
    url_check = endpoint + route_check
    # Poll server for completed task

    payload = {
        "id": str(uuid4()),
        "created": int(time.time()),
        "longPoll": True,
        "data": {
            "taskID": task_id, 
            "apiKey": api_key
        }
    }
    response = requests.post(url_check, json=payload)
    if response.status_code != 200:
        raise Exception("Server error: Booste inference server returned status code {}\n{}".format(
            response.status_code, response.json()['message']))
    out = response.json()
    if not out['success']:
        raise Exception(f"Booste inference check call failed with message: {out.message}")
    return out

async def async_call_check_api(api_key, task_id):
    global endpoint
    route_check = "api/task/check/v1/"
    url_check = endpoint + route_check
    # Poll server for completed task

    payload = {
        "id": str(uuid4()),
        "created": int(time.time()),
        "longPoll": True,
        "data": {
            "taskID": task_id, 
            "apiKey": api_key
        }
    }
    response = await asyncrequests.post(url_check, json=payload)
    if await response.status_code != 200:
        raise Exception("Server error: Booste inference server returned status code {}\n{}".format(
            await response.status_code, await response.json()['message']))
    out = await response.json()
    if not await out['success']:
        raise Exception(f"Booste inference check call failed with message: {await out.message}")
    return out