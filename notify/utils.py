import os

import requests


def shorten_url(url):
    response = requests.get("http://tinyurl.com/api-create.php?url={}".format(url))
    if response.status_code == 200:
        return response.text
    else:
        return url
