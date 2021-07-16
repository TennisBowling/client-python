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

# The syncronous end-to-end caller. Takes in user prams, returns outstring, throws error if server is shit
def gpt2_sync_main(api_key, model_size, in_string, length, temperature, window_max):
    sync_mode = "synchronous"
    validate_input(temperature, window_max)
    task_id = call_start_api(api_key, sync_mode, model_size, in_string, length, temperature, window_max)
    interval, initial_wait = choose_delay_params(model_size, length, window_max)
    time.sleep(initial_wait)
    while True:
        dict_out = call_check_api(api_key, sync_mode, task_id)
        if dict_out['Status'] == "Finished":
            return dict_out["Output"]
        if dict_out["Status"] == "Failed":
            raise Exception("Server error: Booste inference job returned status 'Failed'")
        time.sleep(interval)

async def gpt2_async_start_main(api_key, model_size, in_string, length, temperature, window_max):
    sync_mode = "asynchronous"
    validate_input(temperature, window_max)
    task_id = call_start_api(api_key, sync_mode, model_size, in_string, length, temperature, window_max)
    return task_id

async def gpt2_async_check_main(api_key, task_id):
    sync_mode = "asynchronous"
    dict_out = call_check_api(api_key, sync_mode, task_id)
    return dict_out




# THE API CALLING FUNCTIONS
# ________________________


# The bare async starter. Used by both gpt2_sync_main (automated) and async (client called)
# Takes in start params, returns task ID
def call_start_api(api_key, sync_mode, model_size, in_string, length, temperature, window_max):
    global endpoint
    route_start = 'inference/pretrained/gpt2/async/start'
    url_start = endpoint + route_start

    global cache
    # sequence = []
    payload = {
        "string" : in_string,
        "length" : str(length),
        "temperature" : str(temperature),
        "machineID" : cache['machine_id'],
        "apiKey" : api_key,
        "modelSize" : model_size,
        "windowMax" : window_max, 
        "syncMode": sync_mode
    }
    response = requests.post(url_start, json=payload)
    if response.status_code != 200:
        raise Exception("Server error: Booste inference server returned status code {}\n{}".format(
            response.status_code, response.json()['message']))
    
    try:
        out = response.json()
        task_id = out['TaskID']
        return task_id
    except:
        raise Exception("Server error: Failed to return TaskID")

# The bare async checker. Used by both gpt2_sync_main (automated) and async (client called)
# Takes in task ID, returns reformatted dict_out with Status and Output
def call_check_api(api_key, sync_mode, task_id):
    global endpoint
    route_check = 'inference/pretrained/gpt2/async/check/v2'
    url_check = endpoint + route_check

    # Poll server for completed task
    payload = {"TaskID": task_id, "apiKey": api_key, "syncMode": sync_mode}
    response = requests.post(url_check, json=payload)
    if response.status_code != 200:
        raise Exception("Server error: Booste inference server returned status code {}\n{}".format(
            response.status_code, response.json()['message']))
    out = response.json()
    return out

async def async_call_check_api(api_key, sync_mode, task_id):
    global endpoint
    route_check = 'inference/pretrained/gpt2/async/check/v2'
    url_check = endpoint + route_check

    # Poll server for completed task
    payload = {"TaskID": task_id, "apiKey": api_key, "syncMode": sync_mode}
    response = await asyncrequests.post(url_check, json=payload)
    if response.status_code != 200:
        raise Exception("Server error: Booste inference server returned status code {}\n{}".format(
            response.status_code, response.json()['message']))
    out = response.json()
    return out


# THE MISC FUNCTIONS
# ___________________________________

# The function to raise exceptions if parameters are not valid
def validate_input(temperature, window_max):
    # Make sure request is valid
    global client_error
    if temperature < 0.1 or temperature > 1:
        raise Exception(client_error['OOB'].format("temperature", temperature, "0.1", "1"))
    if window_max < 1 or window_max > 1023:
        raise Exception(client_error['OOB'].format("window_max", window_max,   "1", "1023"))

# The function to determine the frequency that the syncronous functions polls for an async response
def choose_delay_params(model_size, length, window_max): # window max not yet accounted for
    # Choose a delay approprate for the call
    if model_size == 'gpt2':
        interval = length * 0.1
        initial_wait = length * .2
    elif model_size == 'gpt2-xl':
        interval = length * 0.2
        initial_wait = length * .4
    else:
        interval = 3
        initial_wait = length * .3
    # Correct for small calls so it's not rediculous
    if interval < 3:
        interval = 3
    return interval, initial_wait