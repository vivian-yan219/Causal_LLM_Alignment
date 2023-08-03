import requests
import json
import time
from termcolor import colored
import readline
import argparse
import yaml
from yaml.loader import SafeLoader
import re
from graph import Graph
import argparse

api_secret_key = "6d60510bc67941ffbc7a72ed5e945fe7"  # your api_secret_key

url = 'https://lm_experience.sensetime.com/v1/nlp/chat/completions'  
data = {
    "messages": [],
    "temperature": 0.8,
    "top_p": 0.7,
    "max_new_tokens": 2048,
    "repetition_penalty": 1,
    "stream": False,
    "user": "test",
    "model": "SC-PTC-XL-V1-20230609"
}  
headers = {
    'Content-Type': 'application/json',
    'Authorization': api_secret_key
}


def make_sensetime_requests():
    while True:
        try:
            with open('./data/seeds.json', "r") as fin:
                tasks = json.loads(fin.read())
                                
                for i in range(len(tasks)):
                    background = tasks[i]["background"]

                    data["messages"].append({"role": "user", "content": background})
                    response = requests.post(url, headers=headers, json=data)
                    obj = json.loads(response.text)
                
                    count = 0
                    while 'data' not in obj:
                        print(colored('response not valid. trying again...', 'grey'), flush=True)
                        time.sleep(5)
                        response = requests.post(url, headers=headers, json=data)
                        obj = json.loads(response.text)
                        count += 1
                    output = obj['data']['choices'][0]['message']
                    print(colored('SenseChat:' + output, 'white'))
                    data["messages"].append({"role": "assistant", "content": output})
            fin.close()
            #return data

        except KeyboardInterrupt:
            break

