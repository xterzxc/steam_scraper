import pandas
from steam_scraper import parse_steam_comments
import argparse


def main():
    parser = argparse.ArgumentParser(description='Scrape Steam comments and export to Excel.')
    parser.add_argument('profile_id', type=str, help='Steam profile ID')
    parser.add_argument('pagesize', type=int, help='Number of comments to fetch')


    args = parser.parse_args()

    comments = parse_steam_comments(args.profile_id, args.pagesize)
    if len(comments) == 0:
        print('No comments found / Profile is private.')
        return

    df = pandas.DataFrame(comments)
    df.to_excel('steam_comments.xlsx', index=False)



if __name__ == '__main__':
    main()