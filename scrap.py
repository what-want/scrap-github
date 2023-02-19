#!/usr/bin/python
#-*-coding:utf-8-*-

import argparse
import os
import json
import csv
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



    filename = 'repositories-info.csv'
    flag = True
    with open(filename, 'w') as f:
        wr = csv.writer(f)
        for key, value in repositories.items():
            if(flag):
                wr.writerow(value.keys())
                flag = False
            wr.writerow(value.values())

    print('Done!')
    exit(0)