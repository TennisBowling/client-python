import os
from uuid import uuid4
import json
import time
from .gpt2_utils import gpt2_sync_main, gpt2_async_start_main, gpt2_async_check_main
from .generics import run_main, start_main, check_main
from .clip_utils import clip_main, async_clip_main, clip_image_main, clip_text_main
import asyncio
import sys

# Generics
def run(api_key, model_key, model_parameters):
    out = run_main(
        api_key = api_key, 
        model_key = model_key, 
        model_parameters = model_parameters
    )
    return out

def start(api_key, model_key, model_parameters):
    out = start_main(
        api_key = api_key, 
        model_key = model_key, 
        model_parameters = model_parameters
    )
    return out
    
def check(api_key, task_id):
    out_dict = check_main(
        api_key = api_key,
        task_id = task_id
    )
    return out_dict


# GPT2 small
def gpt2(api_key, in_string, length = 5, temperature = 0.8, window_max = 100):
    out_list = gpt2_sync_main(
        api_key = api_key, 
        model_size = "gpt2", 
        in_string = in_string, 
        length = length, 
        temperature = temperature,  
        window_max = window_max)
    return out_list

async def gpt2_async_start(api_key, in_string, length = 5, temperature = 0.8, window_max = 100):
    task_id = await gpt2_async_start_main(
        api_key = api_key, 
        model_size = "gpt2", 
        in_string = in_string, 
        length = length, 
        temperature = temperature,  
        window_max = window_max)
    return task_id

async def gpt2_async_check(api_key, task_id):
    dict_out = await gpt2_async_check_main(api_key, task_id)
    return dict_out

# GPT2 XL
def gpt2_xl(api_key, in_string, length = 5, temperature = 0.8, window_max = 100):
    out_list = gpt2_sync_main(
        api_key = api_key, 
        model_size = "gpt2-xl", 
        in_string = in_string, 
        length = length, 
        temperature = temperature,  
        window_max = window_max)
    return out_list

async def gpt2_xl_async_start(api_key, in_string, length = 5, temperature = 0.8, window_max = 100):
    task_id = await gpt2_async_start_main(
        api_key = api_key, 
        model_size = "gpt2-xl", 
        in_string = in_string, 
        length = length, 
        temperature = temperature,  
        window_max = window_max)
    return task_id

async def gpt2_xl_async_check(api_key, task_id):
    dict_out = await gpt2_async_check_main(api_key, task_id)
    return dict_out

def clip(api_key, prompts, images, pretty_print=False):
    try:
        # Run it async
        dict_out = asyncio.run(async_clip_main(api_key, prompts, images, pretty_print))
        return dict_out

    except:
        # Run it sync if async failed
        dict_out = clip_main(api_key,prompts, images, pretty_print)
        return dict_out
        

# def clip_image(images):
#     dict_out = clip_image_main(images)

# def clip_text(prompts):
#     dict_out = clip_text_main(prompts)

# def clip_fast(encoded_prompts, encoded_images, forward=True):
#     dict_out = clip_fast_main(encoded_prompts, encoded_images, forward)