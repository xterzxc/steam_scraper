import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import pandas as pd
import re
from googletrans import Translator

def translate_to_eng(comment):
    translator = Translator()
    translation = translator.translate(comment, src='ru', dest='en')
    return translation.text

def customurl_to_steamid64(custom_url):
    response = requests.get(custom_url)
    
    if response.status_code != 200:
        return None
    
    steamid64_match = re.search(r'steamid":"(\d+)"', response.text)
    
    if steamid64_match:
        return steamid64_match.group(1)
    else:
        return None


def parse_steam_comments(profile_id, pagesize, limit):
    url = f"https://steamcommunity.com/comment/Profile/render/{profile_id}/-1/"
    params = {
        'start': 0,
        'total_count': pagesize
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    all_comments = []

    while True:
        if len(all_comments) >= limit:
            break

        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching comments: {response.status_code}")
            break

        data = response.json()
        comments_html = data.get('comments_html', '')
        soup = BeautifulSoup(comments_html, 'html.parser')
        comments = soup.find_all('div', class_='commentthread_comment')

        for comment in comments:
            comment_text = comment.find('div', class_='commentthread_comment_text')
            if comment_text:
                username_element = comment.find('a', class_='commentthread_author_link')
                username = username_element.text.strip() if username_element else 'Unknown'

                timestamp_element = comment.find('span', class_='commentthread_comment_timestamp')
                time = timestamp_element['title'] if timestamp_element else 'Unknown'

                avatar_element = comment.find('img')
                avatar_url = avatar_element['src'] if avatar_element else 'https://avatars.steamstatic.com/b5bd56c1aa4644a474a2e4972be27ef9e82e517e_full.jpg'

                comment_data = {
                    'username': username,
                    'time': time,
                    'comment': comment_text.get_text(strip=True),
                    'avatar_url': avatar_url,
                }
                all_comments.append(comment_data)

        start = data.get('start', 0)
        pagesize = data.get('pagesize', 0)
        total_count = data.get('total_count', 0)

        if start + pagesize >= total_count:
            break

        params['start'] = start + pagesize

    sentiment_list = []
    pos, neg, neu = 0, 0, 0

    for comment in all_comments:
        blob = TextBlob(comment['comment'])
        sentiment = blob.sentiment.polarity
        sentiment_list.append(sentiment)
        if sentiment > 0:
            pos += 1
        elif sentiment < 0:
            neg += 1
        else:
            neu += 1 

    pos_percentage = (pos / (pos + neg + neu)) * 100.00
    neg_percentage = (neg / (pos + neg + neu)) * 100.00
    neu_percentage = 100.00 - (pos_percentage + neg_percentage) 

    pos_final = round(pos_percentage, 2)
    neg_final = round(neg_percentage, 2)
    neu_final = round(neu_percentage, 2)              

    result = zip(all_comments, sentiment_list)

    return list(result), pos_final, neg_final, neu_final


def export_to_excel(comments):
    df = pd.DataFrame(comments)
    df.to_excel('steam_comments.xlsx', index=False)