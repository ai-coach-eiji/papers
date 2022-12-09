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
    print('Id list: ', id_list)
    
    result_dict = {}
    
    dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    dt_day = str(dt_now).split(' ', 1)[0]

    for cat in cat_list:
        print('\n Searching for category: ', cat)
        q = f'cat:cs.{cat}'
        
        search = arxiv.Search(
            query = q,
            max_results = 20,
            sort_by = arxiv.SortCriterion.SubmittedDate
        )
        
        r_count = 0
        for result in search:
            print('result: ', result)
            
            if 'https://' in result.summary:
                url = result.links[0]['href']
                print('url: ', url)

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
    response=requests.post(api_url, data={"value1": f"{dt_day}<br>{r_message}"})

if __name__ == "__main__":
    print("Publish")

    # Load log of published data
    if os.path.exists("published.pkl"):
        with open("published.pkl", mode='rb') as f:
            id_list = pickle.load(f)
    else:
        print('pickle Not Exist.')
        id_list = []

    # Query for arXiv API
    cat_list = ['AI', 'CL', 'CV', 'CY', 'ET', 'GR', 'GT', 'HC']
    
    # Call function
    main(API_URL, cat_list, id_list)

    # Update log of published data
    pickle.dump(id_list, open("published.pkl", "wb"))
