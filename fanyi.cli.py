#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Use Baidu Translate API for translating.
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document.
# And see another brief document: `https://fanyi-api.baidu.com/product/113`

release_notes="""
# 2022-2-25: release v1.0: a cli translator tool written in python.
# 2022-2-28: release v1.5: fixed some bugs; rename applet as 'fanyi' instead of 'fanyi.cli'.
# 2022-3-6: release v1.6: delay 1 second to avoid restriction while translating multiple words.
"""

import requests
import time # this library is needed by "sleep()"
#import random
import json
from hashlib import md5
import os
import sys # this library is needed by "exit()"
import argparse

def print_release_notes():
    print(release_notes[1:].replace("# ",""))
    sys.exit()
def get_release_version():
    note = release_notes.split("#")[-1].split(":")[1]
    return note.replace(" release ","")

Abstract = "Fanyi CLI tool({})".format(get_release_version())

parser = argparse.ArgumentParser(description=Abstract)
parser.add_argument('-e', help = "translate Chinese into English.", action="store_true")
parser.add_argument('-z', help = "translate English into Chinese.", action="store_true")
parser.add_argument('-c', help = " = argument '-z'", action="store_true")
parser.add_argument('-a', help = "translate text with auto detecting language(default)", action="store_true")
parser.add_argument('-t', type = str, help = "get text from std i/o")
parser.add_argument('-f', type = str, help = "get text from file")
parser.add_argument('--ori', help = "show origin text", action="store_true")
parser.add_argument('--log', help = "check release notes", action="store_true")
parser.add_argument('--version', help = "check release version", action="store_true")
args = parser.parse_args()
if(args.log):
    print_release_notes()
if(args.version):
    print(Abstract)
    sys.exit()

# Set translate language
# For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
from_lang = 'auto'
to_lang   = 'auto'
if(args.e):
    from_lang = 'zh'
    to_lang   = 'en'
elif(args.z):
    from_lang = 'en'
    to_lang   = 'zh'
elif(args.c):
    from_lang = 'en'
    to_lang   = 'zh'
else:pass

# Generate salt and sign
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()

def translate(query):
    # Set your own appid/appkey.
    appid = '20201212000645063'
    appkey = 'HEhjErB3C9EQzQdtZklq'
    # Set url
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path
    # It is recommend to use a random num as `salt` to enhance security. But I think is unnecessary.
    salt = 65500 
    sign = make_md5(appid + query + str(salt) + appkey)
    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    # Send request
    r = requests.post(url, params=payload, headers=headers)
    try:
        result = r.json()
    except:
        print("Error:request result={}".format(r))
        return "",""
    # Get result
    try:
        trans_res = result['trans_result']
        ori = "" # origin text
        res = "" # translated text
        for p in trans_res:
            res += p["dst"]
            res += "\n"
            ori += p["src"]
            ori += "\n"
        return ori,res
    except:
        print("Error:")
        print(json.dumps(result, indent=4, ensure_ascii=False))
        return "",""

text     = args.t
filepath = args.f

if(text!=None):
    ori,res = translate(text)
    if(args.ori):
        print("# Origin:\n{}\n\n# Result:\n{}\n".format(ori,res))
    else:
        print("# Result:\n{}\n".format(res))
elif(filepath!=None):
    try:
        with open(filepath,'r',encoding='utf-8') as f:
            text = f.read()
    except:
        try:
            with open(filepath,'r',encoding='gbk') as f:
                text = f.read()
        except:
            print("Error:file doesn't exist!\n")
            sys.exit()
    #with open(filepath,'r',encoding='utf-8') as f:
    #    text = f.read()
    #    print(text)
    ori,res = translate(text)
    if(args.ori):
        print("# Origin:\n{}\n\n# Result:\n{}\n".format(ori,res))
    else:
        print("# Result:\n{}\n".format(res))
else:
    while(True):
        text = input("# Input text:\n")
        if(text=='exit' or text=='quit'or text=='0'):
            break
        ori,res = translate(text)
        if(args.ori):
            print("# Origin:\n{}\n\n# Result:\n{}\n".format(ori,res))
        else:
            print("# Result:\n{}\n".format(res))
        time.sleep(1.01) # sleep about 1 second to avoid API freq restriction.
    print("Thanks for using!\n")

