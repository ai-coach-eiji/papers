import pickle
import re
import requests
from time import sleep
import datetime

import arxiv
import pytz

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env') # github secrets
load_dotenv(dotenv_path)

APP_NAME = os.environ.get("APP_NAME")
APP_KEY = os.environ.get("APP_KEY")

# webhook POST先URL
API_URL = f"https://maker.ifttt.com/trigger/{APP_NAME}/with/key/{APP_KEY}"

def main(api_url, cat_list, id_list):
    result_dict = {}

    dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    dt_old = dt_now - datetime.timedelta(days=1)
    dt_all = dt_old.strftime('%Y%m%d%H%M%S')
    dt_day = dt_old.strftime('%Y%m%d')
    dt_hour = dt_old.strftime('%H')

    if dt_hour == '00':
        start = dt_day
        dt_last = dt_day + '115959'
    else:
        start = dt_all
        dt_last = dt_day + '235959'

    for cat in cat_list:
        print('\n Searching for category: ', cat)
        q = f'cat:cs.{cat} AND submittedDate:[{dt_day} TO {dt_last}]'
        
        search = arxiv.query(
                query=q, 
                max_results=30, 
                sort_by='submittedDate'
        )
        r_count = 0
        for result in search:
            if 'https://' in result.summary:
                url = result.links[0]['href']

                if url not in id_list:
                    id_list.append(url) # urlをidとしてpickleに保存

                    message = "\n".join([f"<br>[{cat}]: {result.title}", "<br><br>URL: "+url, "<br><br>発行日: " + result.published])             
        
                    #print('POST URL: ', API_URL) #DEBUG
                    response=requests.post(api_url, data={"value1": message})
                    r_count += 1
                    sleep(2)
        # 結果の表示用
        result_dict[f'{cat}'] = r_count
    
    r_message = "\n".join([f"{k}: {v}" for k, v in result_dict.items()])
    response=requests.post(api_url, data={"value1": f"{dt_day}\n{r_message}"})

if __name__ == "__main__":
    print("Publish")

    # Load log of published data
    if os.path.exists("published.pkl"):
        id_list = pickle.load(open("published.pkl", "rb"))
    else:
        print('pickle Not Exist.')
        id_list = []

    # Query for arXiv API
    cat_list = ['AI', 'CL', 'CV', 'CY', 'ET', 'GR', 'GT', 'HC']
    
    # Call function
    main(API_URL, cat_list, id_list)

    # Update log of published data
    pickle.dump(id_list, open("published.pkl", "wb"))