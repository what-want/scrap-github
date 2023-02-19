#!/usr/bin/python
#-*-coding:utf-8-*-

import argparse
import os
import requests
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('repopath', metavar='Repository-Path-in-GitHub', type=str, nargs=1, help='a repo path for the scrapping')
    args = vars(parser.parse_args())

    repoPath = args.get('repopath', [None])[0]
    if repoPath is None:
        print('No repository path is given!')
        exit(1)

    print(repoPath)

    owner, repo = repoPath.split('/')
    token = os.environ.get('GH_TOKEN', "")


    # Get a repository

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
    print(url)

    if( API_Get_a_repository['METHOD_TYPE'] == "GET" ):
        results = requests.get( url, headers=API_Get_a_repository['HEADERS'] )

    if( not results.status_code in [ 200 ] ):
        msg_error = "Recieved %s response : %s" % (results.status_code, url)
        msg_code = results.status_code

        print(f'Error : {msg_code} - {msg_error}')
        exit(1)
    
    result = json.loads( results.text ) if (results.text != '') else ''
    # print(result)

    if(result.get('id', 0) == 0):
        msg_error = "Recieved wrong response"
        msg_code = results.status_code

        print(f'Error : {msg_code} - {msg_error}')
        exit(1)



    # List repository contributors

    per_page = 100
    contributors = []

    for page in range(1, 100):

        API_List_repository_contributors = {
            'URL' : f'https://api.github.com/repos/{owner}/{repo}/contributors?page={page}&per_page={per_page}',
            'HEADERS' : {
                'Accept' : 'application/vnd.github+json',
                'Authorization' : f'Bearer {token}'
            },
            'METHOD_TYPE' : 'GET',
            'RESPONSE_CODE' : {
                200	: 'if repository contains content',
                204 : 'Response if repository is empty',
                403 : 'Forbidden',
                404	: 'Resource not found'
            }
        }

        url = API_List_repository_contributors['URL']
        print(url)

        if( API_List_repository_contributors['METHOD_TYPE'] == "GET" ):
            results = requests.get( url, headers=API_List_repository_contributors['HEADERS'] )

        if( not results.status_code in [ 200, 204 ] ):
            msg_error = "Recieved %s response : %s" % (results.status_code, url)
            msg_code = results.status_code

            print(f'Error : {msg_code} - {msg_error}')
            exit(1)
        
        result = json.loads( results.text ) if (results.text != '') else ''

        contributors.extend(result)
        
        print(len(result))

        if( len(result) < per_page ):
            break

    print(len(contributors))

    filename = 'contributors.json'
    with open(filename, "w") as f:
        f.write( json.dumps(contributors, indent=4) )
    print(f'written file: {filename}')
    
    exit(0)