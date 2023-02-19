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
        contributors = json.load(f)
    
    print(len(contributors))


    token = os.environ.get('GH_TOKEN', "")


    repositories = {}
    for idx, (contributor, repos) in enumerate(contributors.items()):
        print(f'[{idx+1}/{len(contributors)}] {contributor}')

        for idx, repoPath in enumerate(repos):

           # Get a repository
            _, owner, repo = repoPath.split('/')
            
            API_Get_a_repository = {
                'URL' : f'https://api.github.com/repos/{owner}/{repo}',
                'HEADERS' : {
                    'Accept' : 'application/vnd.github+json',
                    'Authorization' : f'Bearer {token}'
                },
                'METHOD_TYPE' : 'GET',
                'RESPONSE_CODE' : {
                    200	: 'OK',
                    301 : 'Moved permanently',
                    403 : 'Forbidden',
                    404	: 'Resource not found'
                }
            }

            url = API_Get_a_repository['URL']
            # print(url)

            if( API_Get_a_repository['METHOD_TYPE'] == "GET" ):
                results = requests.get( url, headers=API_Get_a_repository['HEADERS'] )

            if( not results.status_code in [ 200 ] ):
                msg_error = "Recieved %s response : %s" % (results.status_code, url)
                msg_code = results.status_code

                print(f'Error : {msg_code} - {msg_error}')
                exit(1)
            
            result = json.loads( results.text ) if (results.text != '') else ''
            # pprint(result)

            if(result.get('fork', False)):
                if(result['parent']['full_name'] in repositories.keys()):
                    print(f"    already exists - {result['parent']['full_name']}")
                
                else:
                    repositories[result['parent']['full_name']] = result['parent']
                    print(f"    added - {result['parent']['full_name']}")

            else:
                full_name = f'{owner}/{repo}'
                if(full_name in repositories.keys()):
                    print(f"    already exists - {full_name}")
                
                else:
                    repositories[full_name] = result
                    print(f"    added - {full_name}")

    print(len(repositories))
    filename = 'parent-of-popular.json'
    with open(filename, "w") as f:
        f.write( json.dumps(repositories, indent=4) )
    print(f'written file: {filename}')
    
    exit(0)