import requests
from bs4 import BeautifulSoup
import pandas


def parse_steam_comments(profile_id, pagesize):
    url = f"https://steamcommunity.com/comment/Profile/render/{profile_id}/-1/"
    params = {
        'start': 0,
        'total_count': pagesize
    }
    all_comments = []

    while True:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
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

                comment_data = {
                    'username': username,
                    'time': time,
                    'comment': comment_text.get_text(strip=True)
                }
                all_comments.append(comment_data)

        start = data.get('start', 0)
        pagesize = data.get('pagesize', 0)
        total_count = data.get('total_count', 0)

        if start + pagesize >= total_count:
            break

        params['start'] = start + pagesize

    return all_comments


def export_to_excel(comments):
    df = pandas.DataFrame(comments)
    df.to_excel('steam_comments.xlsx', index=False)
