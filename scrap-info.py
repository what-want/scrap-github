#!/usr/bin/python
#-*-coding:utf-8-*-

import argparse
import os
import requests
import json
from bs4 import BeautifulSoup
from pprint import pprint


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('jsonpath', metavar='JSON-Path-of-Repositories', type=str, nargs=1, help='a JSON path of the repositories')
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
        repositories = json.load(f)
    
    print(len(repositories))


    filename = 'repositories-info.json'
    if( not os.path.exists(filename) ):
        infos = {}
    else:
        with open(filename, 'r') as f:
            infos = json.load(f)

    for idx, (full_name, repository) in enumerate(repositories.items()):
        if full_name in infos.keys():
            print(f'[{idx+1}/{len(repositories)}] {full_name} is already scrapped!')
            continue

        print(f'[{idx+1}/{len(repositories)}] {full_name}')
        # pprint(repository)

        repo = {
            'full_name' : repository['full_name'],
            'name' : repository['name'],
            'owner' : repository['owner']['login'],
            'owner_type' : repository['owner']['type'],
            'created_at' : repository['created_at'],
            'updated_at' : repository['updated_at'],
            'forks_count' : repository['forks_count'],
            'stars_count' : repository['stargazers_count'],
            'default_branch' : repository['default_branch'],
            'topics' : repository['topics'],
            'language' : repository['language'],
        }

        url = repository['html_url']

        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            item = soup.select_one('#issues-repo-tab-count')
            if item is None:
                repo['open_issues_count'] = 0
            else:
                item = item.text.replace(',', '').strip()
                if('5k+' in item):
                    repo['open_issues_count'] = 5001
                else:
                    repo['open_issues_count'] = int(float(item.replace('k','').strip()) * 1000) if('k' in item) else int(item.strip())

            item = soup.select_one('#pull-requests-repo-tab-count')
            if item is None:
                repo['open_pull_requests_count'] = 0
            else:
                item = item.text.replace(',', '').strip()
                if('5k+' in item):
                    repo['open_pull_requests_count'] = 5001
                else:
                    repo['open_pull_requests_count'] = int(float(item.replace('k','').strip()) * 1000) if('k' in item) else int(item.strip())

            item = soup.select_one('#repo-content-pjax-container > div > div > div.Layout.Layout--flowRow-until-md.Layout--sidebarPosition-end.Layout--sidebarPosition-flowRow-end > div.Layout-main > div.file-navigation.mb-3.d-flex.flex-items-start > div.flex-self-center.flex-self-stretch.d-none.flex-items-center.lh-condensed-ultra.d-lg-flex > a:nth-child(1) > strong')
            if item is None:
                repo['branches_count'] = 0
            else:
                item = item.text.strip().replace(',', '')
                repo['branches_count'] = int(float(item.replace('k','').strip()) * 1000) if('k' in item) else int(item.strip())

            item = soup.select_one('#repo-content-pjax-container > div > div > div.Layout.Layout--flowRow-until-md.Layout--sidebarPosition-end.Layout--sidebarPosition-flowRow-end > div.Layout-main > div.file-navigation.mb-3.d-flex.flex-items-start > div.flex-self-center.flex-self-stretch.d-none.flex-items-center.lh-condensed-ultra.d-lg-flex > a:nth-child(2) > strong')
            if item is None:
                repo['tags_count'] = 0
            else:
                item = item.text.strip().replace(',', '')
                repo['tags_count'] = int(float(item.replace('k','').strip()) * 1000) if('k' in item) else int(item.strip())
            
            item = soup.select_one('div.flex-shrink-0 > ul.list-style-none > li > a > span > strong')
            if item is None:
                repo['commits_count'] = 0
            else:
                item = item.text.strip().replace(',', '')
                repo['commits_count'] = int(float(item.replace('k','').strip()) * 1000) if('k' in item) else int(item.strip())

            items_count = soup.select('div.mt-2 > a')
            repo['watchers_count'] = 0
            for idx, item in enumerate(items_count):
                if('stars' in item.text.strip()):
                    temp = item.text.strip().split(' ')[0].replace(',', '').strip()
                    temp = int(float(temp.replace('k','').strip()) * 1000) if('k' in temp) else int(temp.strip())
                    if(repo['stars_count'] != temp):
                        if((temp - repo['stars_count']) / repo['stars_count'] > 2):
                            print(f"    stars_count value changed : {repo['stars_count']} <- {temp}")
                            repo['stars_count'] = temp
                        else:
                            print(f"    stars_count is not equal to side info : {repo['stars_count']} != {temp}")
                        # exit(1)

                if('watching' in item.text.strip()):
                    temp = item.text.strip().split(' ')[0].replace(',', '').strip()
                    repo['watchers_count'] = int(float(temp.replace('k','').strip()) * 1000) if('k' in temp) else int(temp.strip())
                
                if('forks' in item.text.strip()):
                    temp = item.text.strip().split(' ')[0].replace(',', '').strip()
                    temp = int(float(temp.replace('k','').strip()) * 1000) if('k' in temp) else int(temp.strip())
                    if(repo['forks_count'] != temp):

                        if((temp - repo['forks_count']) / repo['forks_count'] > 2):
                            print(f"    forks_count value changed : {repo['forks_count']} <- {temp}")
                            repo['forks_count'] = temp
                        else:
                            print(f"    forks_count is not equal to side info : {repo['forks_count']} != {temp}")
                        # exit(1)

            items = soup.select('div > div > div > div > h2 > a')
            repo['releases_count'] = 0
            repo['packages_count'] = 0
            repo['contributors_count'] = 0
            for item in items:
                if('Releases' in item.text.strip()):
                    temps = " ".join(item.text.split()).split(' ')
                    if(len(temps) != 2):
                        repo['releases_count'] = 0
                    else:
                        temp = temps[1].replace(',', '').strip()
                        temp = '5001' if('5000+' in temp) else temp
                        repo['releases_count'] = int(float(temp.replace('k','').strip()) * 1000) if('k' in temp) else int(temp.strip())

                if('Packages' in item.text.strip()):
                    temps = " ".join(item.text.split()).split(' ')
                    if(len(temps) != 2):
                        repo['packages_count'] = 0
                    else:
                        temp = temps[1].replace(',', '').strip()
                        temp = '5001' if('5000+' in temp) else temp
                        repo['packages_count'] = int(float(temp.replace('k','').strip()) * 1000) if('k' in temp) else int(temp.strip())

                if('Contributors' in item.text.strip()):
                    temps = " ".join(item.text.split()).split(' ')
                    if(len(temps) != 2):
                        repo['contributors_count'] = 0
                    else:
                        temp = temps[1].replace(',', '').strip()
                        temp = '5001' if('5000+' in temp) else temp
                        repo['contributors_count'] = int(float(temp.replace('k','').strip()) * 1000) if('k' in temp) else int(temp.strip())

            languages = soup.select('ul.list-style-none > li.d-inline > a > span')
            repo['languages'] = []
            for language in languages:
                if('%' not in language.text.strip()):
                    repo['languages'].append(language.text.strip())

            # pprint(repo)
            # exit(0)

        else : 
            print(response.status_code)


        url = f"{repository['html_url']}/issues"

        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # item = soup.select_one('#js-issues-toolbar > div > div.flex-auto.d-none.d-lg-block.no-wrap > div > a:nth-child(2)')
            items = soup.select('div.d-block > div.table-list-header-toggle > a')
            for item in items:
                if('Closed' in item.text.strip()):
                    temps = " ".join(item.text.split()).split(' ')
                    if(len(temps) != 2):
                        repo['close_issues_count'] = 0
                    else:
                        temp = temps[0].strip().replace(',', '')
                        repo['close_issues_count'] = int(float(temp.replace('k','').strip()) * 1000) if('k' in temp) else int(temp.strip())
                    break

            repo['issues_count'] = repo['open_issues_count'] + repo['close_issues_count']
            # pprint(repo)
            # exit(0)

        else : 
            print(response.status_code)
        


        url = f"{repository['html_url']}/pulls"

        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            items = soup.select('div.d-block > div.table-list-header-toggle > a')
            for item in items:
                if('Closed' in item.text.strip()):
                    temps = " ".join(item.text.split()).split(' ')
                    if(len(temps) != 2):
                        repo['close_pull_requests_count'] = 0
                    else:
                        temp = temps[0].strip().replace(',', '')
                        repo['close_pull_requests_count'] = int(float(temp.replace('k','').strip()) * 1000) if('k' in temp) else int(temp.strip())
                    break

            repo['pull_requests_count'] = repo['open_pull_requests_count'] + repo['close_pull_requests_count']
            # pprint(repo)
            # exit(0)

        else : 
            print(response.status_code)
        
        infos[full_name] = repo

        with open(filename, "w") as f:
            f.write( json.dumps(infos, indent=4) )
        print(f'    written file: {filename} {len(infos)}')
    
    exit(0)