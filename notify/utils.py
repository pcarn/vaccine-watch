import requests


def shorten_url(url):
    response = requests.get("http://tinyurl.com/api-create.php?url={}".format(url))
    try:
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError:
        logging.warning("Error when shortening url, will use original")
        return url
