# -*- coding: utf-8 -*-

import re
import argparse
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup as BS


#use the following for easy debugging
DEBUG=False
SENDMAIL=False

def debug(*args):
    if DEBUG:
        print("DEBUG", args)


def send_mail(content):
    debug("SEND EMAIL")


def custom_parser(element, soup):
    info = []
    # general handling for contact form on wordpress
    if element == "contact":
        divs = soup.find_all(class_=element)
        items = divs[0].find_all("a")
    # custom handling on html
    elif element == "entry-content":
        divs = soup.find_all(class_=element)
        items = divs[0].find_all(re.compile('^h[1-6]$'))
    # simple handling on html title
    elif element == "title":
        items = soup.find_all(element)
    else:
        return "error"
    #debug(items); # help debug
    for i in items:
        info.append(i.get_text().strip().replace("\n", " "))
    return info


def find_data(html, element, word, url):
    soup = BS(html, "html.parser")
    info = custom_parser(element, soup)
    debug("ACTUAL HTML CONTENT", info); # use this for debug debug of html
    if word not in info and word not in str(info):
        content = "NOT_FOUND", word, element, url
        send_mail(content)
        debug(
            "FAILURE to find {} in {} into html element {}".format(word, url, element)
        )


def fetch(session, element, word, url):
    # use header orelse wordpress is not found status_code 403
    header = {"User-Agent": "Mozilla/5.0"}
    with session.get(url, headers=header) as response:
        enc = response.apparent_encoding
        if not enc:
            enc ='utf-8' # fix for greek websites
        debug(enc)
        response.encoding = enc
        resp = response.text
        if response.status_code != 200:
            content = "HTTP_STATUS", response.status_code, word, url
            send_mail(content)
            debug("FAILURE to get {} error code {}".format(url, response.status_code))
        find_data(resp, element, word, url)
        return resp


async def get_data_asynchronous():
    # if you want to define hardcoded values to it here
    # url = "" ; words_to_fetch = []
    parser = argparse.ArgumentParser(
        description="""aspy-check.py 'http://example.com' 'entry-content' 'word1' 'word2' 'word3' """
    )
    parser.add_argument("url", metavar="url", type=str, nargs="?", help="url to search")
    parser.add_argument(
        "element", metavar="element", type=str, nargs="?", help="html class name"
    )
    parser.add_argument(
        "word", metavar="word", type=str, nargs="+", help="word(s) to search for"
    )
    args = parser.parse_args()
    url = args.url
    element = args.element
    words_to_fetch = args.word
    debug("ARGS", url, element, words_to_fetch)
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            # Set any session parameters here before calling `fetch`
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(
                        session,
                        element,
                        word,
                        url,
                    )  # Allows us to pass in multiple arguments to `fetch`
                )
                for word in words_to_fetch
            ]
            for response in await asyncio.gather(*tasks):
                pass


def main():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)


main()
