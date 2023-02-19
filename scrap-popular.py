#!/usr/bin/python
#-*-coding:utf-8-*-

import argparse
import os
import requests
import json
from bs4 import BeautifulSoup


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('jsonpath', metavar='JSON-Path-of-Contributors', type=str, nargs=1, help='a JSON path of the contributors')
    args = vars(parser.parse_args())

    jsonPath = args.get('jsonpath', [None])[0]
    if jsonPath is None:
        print('No JSON path is given!')
        exit(1)

    print(jsonPath)

    if( not os.path.exists(jsonPath) ):
        print('JSON file does not exist!')
        exit(1)

    with open(jsonPath, 'r') as f:
        contributors = json.load(f)
    
    print(len(contributors))

    populars = {}
    for idx, contributor in enumerate(contributors):
        print(f'[{idx+1}/{len(contributors)}] {contributor["login"]}')
        url = contributor['html_url']

        response = requests.get(url)
        populars[contributor['login']] = []
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            for index in range(1, 11):
                path = soup.select(f'#user-profile-frame > div > div:nth-child(1) > div > ol > li:nth-child({index}) > div > div > div > a')
                if len(path) == 0:
                    break
                else:
                    populars[contributor['login']].append(path[0]['href'])
            
        else : 
            print(response.status_code)

    filename = 'contributors-popular.json'
    with open(filename, "w") as f:
        f.write( json.dumps(populars, indent=4) )
    print(f'written file: {filename}')
    
    exit(0)