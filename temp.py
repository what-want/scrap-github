#!/usr/bin/python
#-*-coding:utf-8-*-

if __name__ == '__main__':
    
    template = f'this is {a}'

    a = 'wow'

    o = template.format(a=a)

    print(o)