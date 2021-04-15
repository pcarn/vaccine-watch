import logging

import requests

from utils import timeout_amount


def shorten_url(url):
    try:
        response = requests.get(
            "http://tinyurl.com/api-create.php?url={}".format(url),
            timeout=timeout_amount,
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        logging.warning("Error when shortening url, will use original")
        return url
