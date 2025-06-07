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
    #print('Id list: ', id_list)
    
    result_dict = {}
    
    dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    dt_day = str(dt_now).split(' ', 1)[0]

    print(f'\n--- Starting search ---')
    for cat in cat_list:
        print('\n Searching for category: ', cat)
        q = f'cat:cs.{cat}'
        
        search = arxiv.Search(
            query = q,
            max_results = 20,
            sort_by = arxiv.SortCriterion.SubmittedDate
        )
        
        r_count = 0
        for result in search.results():
            #print('result: ', result)
            
            if 'https://' in result.summary:
                url = str(result.links[0])
                #print('url: ', url)

                if url not in id_list:
                    id_list.append(url) # urlをidとしてpickleに保存

                    message = "\n".join([f"<br>[{cat}]: {result.title}", "<br><br>URL: "+url, "<br><br>発行日: " + str(result.published)])             
        
                    #print('POST URL: ', API_URL) #DEBUG
                    response=requests.post(api_url, data={"value1": message})
                    r_count += 1
                    sleep(2)
        # 結果の表示用
        result_dict[f'{cat}'] = r_count

    print('\n Searching for AI x Sports papers...')
    # AIとスポーツの関連性が高いカテゴリを指定
    ai_sports_categories = ['cs.AI', 'cs.CV', 'cs.CL', 'cs.GT', 'stat.ML', 'eess.AS']
    
    ai_sports_count = 0
    for ai_cat in ai_sports_categories:
        print(f'  - In category: {ai_cat}')
        # 各AIカテゴリ内でスポーツ関連キーワードを検索
        q_ai_sports = f'cat:{ai_cat} AND (ti:"sports" OR abs:"sports" OR ti:"athletic" OR abs:"athletic" OR ti:"game analysis" OR abs:"game analysis" OR ti:"player performance" OR abs:"player performance" OR ti:"sport" OR abs:"sport" OR ti:"e-sports" OR abs:"e-sports" OR ti:"sport analytics" OR abs:"sport analytics")'

        search_ai_sports = arxiv.Search(
            query = q_ai_sports,
            max_results = 10,
            sort_by = arxiv.SortCriterion.SubmittedDate
        )
        
        for result in search_ai_sports.results():
            url = result.pdf_url

            if url not in id_list:
                id_list.append(url)
                
                # 例1：シンプルにタイトルとURLと発行日
                # message = "\n".join([f"<br>[AI x Sports - {ai_cat.split('.')[-1].upper()}]: {result.title}", "<br><br>URL: "+url, "<br><br>発行日: " + str(result.published)])

                # 例2：アブストラクトの最初の200文字を追加する場合
                summary_snippet = result.summary[:200] + "..." if len(result.summary) > 200 else result.summary
                message = "\n".join([
                    f"<br>[AI x Sports - {ai_cat.split('.')[-1].upper()}]: {result.title}",
                    "<br><br>URL: "+url,
                    "<br><br>発行日: " + str(result.published)
                ])

                response=requests.post(api_url, data={"value1": message})
                ai_sports_count += 1
                sleep(2)
            
    result_dict['AI x Sports'] = ai_sports_count
    
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
    cat_list = ['AI', 'CL', 'CV', 'CY', 'ET', 'GR', 'GT', 'HC', 'eess.AS']
    
    # Call function
    main(API_URL, cat_list, id_list)

    # Update log of published data
    pickle.dump(id_list, open("published.pkl", "wb"))
