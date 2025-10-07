#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import argparse
import requests
import time

import pprint

from w3lib.url import safe_url_string
import validators

# Globals
VERSION = '1.5'

CRDF_API_BASE_URL = 'https://threatcenter.crdf.fr/api/v1/'
CRDF_API_KEY = 'SECRET_CRDF_API_KEY'

ACTION_SUBMIT = 'submit'
ACTION_CHECK = 'check'
ACTION_INFO_KEY = 'info_key'
ACTIONS = [ACTION_SUBMIT, ACTION_CHECK, ACTION_INFO_KEY]

# Options definition
parser = argparse.ArgumentParser(description="version: " + VERSION)
parser.add_argument('-k', '--api-key', help='API key (could either be provided in the "%s" env var)' % CRDF_API_KEY, type = str)
parser.add_argument('-i', '--input-file', help='Input file (either list of newline-separated FQDN, or a list newline-separated of CRDF refs)')
parser.add_argument('-a', '--action', help = 'Action to do on CRDF (default \'submit\')', choices = ACTIONS, type=str.lower, default = ACTION_SUBMIT)
parser.add_argument('-p', '--proxy', help = 'Proxy configuration (e.g "-p \'http://127.0.0.1:8080\'")', type=str.lower, default = None)


def dump_success(req, action):
    req_json = req.json()
    if req_json:
        if req_json.get('error') == False:
            print('[+] CRDF "%s" request successful' % action)
            pprint.pprint(req_json)
    return

def dump_err(req, msg):
    print(msg)
    print(req.status_code)
    print(req.content.decode('utf-8'))
    return

def set_proxies(options):
    res = None
    if options.proxy:
        res = { 'http': options.proxy,
                'https': options.proxy }
    return res


def handle_res(req, action):
    if req.ok:
        dump_success(req, action)
    else:
        dump_err(req, '[!] CRDF "%s" request error' % action)
        print('[!] Exiting')
        sys.exit(0)
    print('-------------------')
    return


def handle_req(action, http_method, url_endpoint, data_payload, options):
    req = None
    try:
        if http_method == 'post':
            req = requests.post(url_endpoint, json=data_payload, proxies=set_proxies(options))
        
        elif http_method == 'get':
            req = requests.get(url_endpoint, json=data_payload, proxies=set_proxies(options))
        
        handle_res(req, action)
    
    except Exception as e:
        print('[!] Exception: "%s"' % e)
    
    return req


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def crdf_info_key(options):
    retval = os.EX_OK
    url_endpoint = CRDF_API_BASE_URL + 'info_key.json'
    
    req_data = { "token": options.api_key,
                 "method": "info_key" }
                 
    req = handle_req(ACTION_INFO_KEY, 'post', url_endpoint, req_data, options)
    
    return retval


def crdf_check(options):
    retval = os.EX_OK
    
    url_endpoint = CRDF_API_BASE_URL + 'submit_get_info.json'

    refs = []
    
    if os.path.isfile(options.input_file):
        with open(options.input_file, mode='r', encoding='utf-8') as fd_input:
            refs = fd_input.read().splitlines()
        
        if refs:
            #pprint.pprint(refs)
            
            for ref in refs:
                ref = ref.strip()
                req_data = { "token": options.api_key,
                             "method": "submit_get_info",
                             "ref": ref}
                
                print("[+] CRDF ref '%s'" % ref)
                req = handle_req(ACTION_CHECK, 'post', url_endpoint, req_data, options)
                
        else:
            retval = os.EX_NOINPUT
    
    else:
        retval = os.EX_NOINPUT
        
    return retval

def crdf_submit(options):
    retval = os.EX_OK
    
    url_endpoint = CRDF_API_BASE_URL + 'submit_url.json'
    
    malicious_url = []
    
    if os.path.isfile(options.input_file):
        with open(options.input_file, mode='r', encoding='utf-8') as fd_input:
            for line in fd_input:
                line = line.strip()
                if line.startswith(('http://', 'https://')):
                    if validators.url(line):
                        entry = safe_url_string(line)
                        if validators.url(entry):
                            malicious_url.append(entry)
                else:
                    entry_http_raw = 'http://' + line
                    if validators.url(entry_http_raw):
                        entry_http = safe_url_string(entry_http_raw)
                        if validators.url(entry_http):
                            malicious_url.append(entry_http)
                    
                    entry_https_raw = 'https://' + line
                    if validators.url(entry_https_raw):
                        entry_https = safe_url_string(entry_https_raw)
                        if validators.url(entry_https):
                            malicious_url.append(entry_https)
        
        if malicious_url:
            #pprint.pprint(malicious_url)
            
            # slices of max 1000 url
            for sublist in chunks(malicious_url, 1000):
                req_data = { "token": options.api_key,
                             "method": "submit_url",
                             "urls": sublist }
                
                req = handle_req(ACTION_SUBMIT, 'post', url_endpoint, req_data, options)
                
                # 2 submissions per minute
                time.sleep(31)
            
    else:
        retval = os.EX_NOINPUT
        
    return retval

def main():
    global parser
    options = parser.parse_args()
    
    api_key = options.api_key
    if not(api_key):
        if CRDF_API_KEY in os.environ:
            api_key = os.environ[CRDF_API_KEY]
        else:
            parser.error('[!] No API key has been provided, exiting.')
    options.api_key = api_key
    
    
    if (options.input_file == None) and (options.action != 'info_key'):
         parser.error('Please specify a valid input file or a valid URL')
    
    if options.action == ACTION_SUBMIT:
        sys.exit(crdf_submit(options))
    
    elif options.action == ACTION_CHECK:
        sys.exit(crdf_check(options))
        
    elif options.action == ACTION_INFO_KEY:
        sys.exit(crdf_info_key(options))

if __name__ == "__main__" :
    main()