from typing import Tuple, List
import urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

from blueness import module
from bluer_objects import path, file
from bluer_objects import objects

from bluer_sandbox import NAME
from bluer_sandbox.parser.hashing import hash_of
from bluer_sandbox.logger import logger


NAME = module.name(__file__, NAME)


def parse(
    url: str,
    object_name: str = "",
    filename: str = "",
) -> Tuple[bool, List[str]]:
    logger.info("{}.parse({})".format(NAME, url))

    success = False
    list_of_urls: List[str] = []

    try:
        response = urllib.request.urlopen(url)
        content = response.read().decode("utf-8")
        soup = BeautifulSoup(content, "html.parser")

        list_of_urls = list({link.get("href") for link in soup.find_all("a")})
        list_of_urls = [
            url_
            for url_ in list_of_urls
            if isinstance(url_, str) and not url_.startswith("#")
        ]
        list_of_urls = [
            urljoin(url, url_) if url_.startswith("/") else url_
            for url_ in list_of_urls
        ]
        logger.info(f"found {len(list_of_urls)} url(s):")
        for index, url_ in enumerate(list_of_urls):
            logger.info(f"#{index+1: 3}: {url_}")

        if object_name:
            if not filename:
                filename = "cache/{}.html".format(hash_of(url))

            filename = objects.path_of(
                object_name=object_name,
                filename=filename,
            )

            if not path.create(file.path(filename)):
                return False, []

            with open(filename, "w") as f:
                f.write(content)

            logger.info(f"-> {filename}")

        success = True
    except Exception as e:
        logger.error(e)

    return success, list_of_urls
