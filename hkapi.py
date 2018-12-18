#!/usr/bin/python

import hashlib
import hmac
import requests
import time
import hashlib
import base64
import json
import re

APIKEY = 'your-api-key';  # replace with your own
APISECRET = b'your-api-secret'; # replace with your own

def headersKeysSort(headers):
    keys = []
    for key in headers:
        if (not (re.match(r'^(Accept|Content-MD5|Content-Type|Date)', key))):
            keys.append(key);
    keys.sort()
    return keys

def buildUrl(method, url, params, data):
    keys = []
    if (not(data)):
        for key in params:
            keys.append(key + "=" + str(params[key]))

    if (len(keys) > 0):
        keys.sort()
        return url + '?' + '&'.join(keys)

    return url

def sign(payload, secret):
    digest = hmac.new( secret, payload.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()

#function md5(content):
#    return crypto.createHash('md5').update(content, 'utf8').digest('base64');

def hkSignString(method, headers, url, params, data):
    list = []

    method = method.upper()
    list.append(method)

    if (not ('Accept' in headers)):
        headers['Accept'] = '*/*'
    list.append(headers['Accept']);

    if (not('Content-Type' in headers)):
        if (data):
            headers['Content-Type'] = 'text/plain;charset=UTF-8'
        else:
            headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
    list.append(headers['Content-Type'])

    if ('Date' in headers):
        list.append(headers['Date'])

    keys = headersKeysSort(headers)
    if (keys):
        for i in range(len(keys)):
            list.append(keys[i].lower() + ":" + headers[keys[i]]) 
        headers['X-Ca-Signature-Headers'] = ','.join(keys).lower()

    list.append(buildUrl(method, url, params, data))
    return '\n'.join(list)


def hkSignHeader (url, urlParams, method, headers, params, data):
    url = re.sub(r'https?:\/\/[\w.]+(:[0-9]*)?', '', url)
    if (urlParams):
        for key in urlParams:
            url = url.replace(key, urlParams[key])

    headers = headers if (headers) else {}
    headers['X-Ca-Timestamp'] = str(int(round(time.time() * 1000)))
    headers['X-Ca-Key'] = APIKEY
    _signString = hkSignString(method, headers, url, params, data)
    headers['X-Ca-Signature'] = str(sign(_signString, APISECRET))
    return headers

def hkvisionRequest(url, urlParams, method, headers, params, data):
    h = hkSignHeader(url, urlParams, method, headers, params, data)
    r = requests.post(url, data=params, headers=h)
    return r

if __name__ == "__main__":
    # 10 + 25 = 35
    p = { 'a': 10, 'b': 25 }
    r = hkvisionRequest('https://open8200.hikvision.com/artemis/api/artemis/v1/plus', None, 'post',  None, p, None)
    if (r.status_code < 200 or r.status_code >= 400):
        print("error - status code: " + str(r.status_code))
        quit(1)

    print(str(r.json()['result']))