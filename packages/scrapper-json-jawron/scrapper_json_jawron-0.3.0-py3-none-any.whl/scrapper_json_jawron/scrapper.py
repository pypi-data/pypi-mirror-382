import json
import time
from typing import List, Type, Generic, TypeVar, Callable
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, Tag
import dataclasses
import csv
from src.scrapper_json_jawron.cleaner import Cleaner

def get_rules_from_file(file: str) -> dict:
    with open(file, 'r') as f:
        rules = json.load(f)
        return rules

def get_element_attribute(element: Tag, attribute: str) -> Tag|str:
    if attribute == "text":
        return element.get_text(strip=True)
    elif attribute == "element":
        return element
    else:
        return element.get(attribute)

def get_element(root_element: Tag, rules: dict) -> list[Tag]|Tag|str:
    selector = rules.get('selector')
    attribute = rules.get('attribute', 'text')
    item_type = rules.get('item_type', 'single')
    index = rules.get('index', 0)

    if selector is None:
        return get_element_attribute(root_element, attribute)

    if item_type == 'single':
        element_list = root_element.select(selector, limit=index+1)
        check_length = len(element_list) == 0 or len(element_list) <= index
        if element_list is None or check_length:
            return ""

        element = element_list[index]
        return get_element_attribute(element, attribute)
    elif item_type == 'list':
        elements = root_element.select(selector)
        return elements
    else:
        return root_element

def get_response(url: str, retries: int, delay: int, debug: bool = False) -> str:
    current_delay = delay
    for retry in range(retries):
        if debug:
            print(f"Retry {retry+1} of {retries}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'referer': 'https://www.google.com/',
            }
            request = Request(url, headers=headers)
            response = urlopen(request)
        except HTTPError as e:
            print(f"Failed to execute function. {e}")
            time.sleep(current_delay)
            current_delay *= 2
            continue
        return response.read()
    raise HTTPError

T = TypeVar('T')

def _basic_pagination(root_url: str, start: int, limit: int):
    url_list = []
    for page in range(start, limit):
        url = root_url.replace("{}", str(page))
        url_list.append(url)
    return url_list


class Scrapper(Generic[T]):
    def __init__(self, rules: dict, result_class: Type[T]):
        self.rules = rules
        self.root_url = rules.get('url')
        self.result_class = result_class
        self.retries = rules.get('retries', 3)
        self.delay = rules.get('delay', 2)

    def _scrap_list_html(self, response: str) -> List[T]:
        entity_list = []
        soup = BeautifulSoup(response, "html.parser")
        root = get_element(soup, self.rules.get('root'))
        for entry in get_element(root, self.rules.get('entry')):
            item_dict = self.iterate_elements(entry, self.rules)
            page_obj = self.result_class(**item_dict)
            entity_list.append(page_obj)

        return entity_list

    def _scrap_list_xml(self, response: str) -> List[T]:
        tree = ET.fromstring(response)
        namespaces = self.rules.get('namespace')
        root = tree.find(self.rules.get('root'), namespaces) if self.rules.get('root') is not None else tree
        entries = root.findall(self.rules.get('entry'), namespaces)

        entity_list = []
        for entry in entries:
            entry_rules = self.rules.get("elements")
            item_dict = {}

            for key, item_rules in entry_rules.items():
                item_element = entry.find(item_rules.get('selector'), namespaces)
                if item_rules.get('attribute') == 'text':
                    item = item_element.text.strip() if item_element is not None else ''
                else:
                    item = item_element.attrib[item_rules.get('attribute')] if item_element is not None else ''

                if item_rules.get('prefix') is not None:
                    item = item_rules.get('prefix') + item
                if item_rules.get('suffix') is not None:
                    item = item + item_rules.get('suffix')
                item_dict[key] = item

            page_obj = self.result_class(**item_dict)
            entity_list.append(page_obj)
        return entity_list

    def scrap_list(self, custom_pagination: Callable = _basic_pagination, custom_params: dict = None, content_file: str = None) -> List[T]:
        entity_list = []
        if self.rules.get('type') == 'xml':
            if content_file is not None:
                response = content_file
            else:
                response = get_response(self.root_url, self.retries, self.delay)
            entity_list += self._scrap_list_xml(response)
        elif self.rules.get('type') == 'html':
            paginate = self.rules.get('pagination', False)
            if paginate and content_file is None:
                limit = self.rules.get('pagination_limit', 10)
                start = self.rules.get('pagination_start', 1)
                if custom_params is not None:
                    url_list = custom_pagination(self.root_url, start, limit, **custom_params)
                else:
                    url_list = custom_pagination(self.root_url, start, limit)
                for url in url_list:
                    response = get_response(url, self.retries, self.delay)
                    entity_list += self._scrap_list_html(response)
                    time.sleep(2)
            else:
                if content_file is not None:
                    response = content_file
                else:
                    response = get_response(self.root_url, self.retries, self.delay)
                entity_list += self._scrap_list_html(response)

        return entity_list

    def scrap_entity(self, article_rules: dict, entity: T) -> T:
        url = entity.url
        response = get_response(url, self.retries, self.delay)

        soup = BeautifulSoup(response, "html.parser")
        content = get_element(soup, article_rules.get('content'))
        entity.content = content
        return entity

    def iterate_elements(self, entry: Tag, rules: dict) -> dict:
        entry_rules = rules.get("elements")
        item_dict = {}

        for key, item_rules in entry_rules.items():
            item = get_element(entry, item_rules)

            if item_rules.get('elements') is not None:
                item = self.iterate_elements(item, item_rules)

            if item_rules.get('transform') is not None:
                if not isinstance(item, str):
                    print("Can't apply cleaning function to entity that is not string")
                    continue
                clean = item_rules.get('transform')
                item = Cleaner().apply(item, clean)
            else: # default cleaning rules
                if not isinstance(item, str):
                    item_dict[key] = item
                    continue
                clean = ["REMOVE_NEWLINES", "COLLAPSE_WHITESPACE", "STRIP"]
                item = Cleaner().apply(item, clean)

            item_dict[key] = item
        return item_dict

    def export_to_csv(self, file: str, entity_list: List[T]) -> None:
        with open(file, 'w') as csvfile:
            writer = csv.writer(csvfile)
            header = [field.name for field in dataclasses.fields(entity_list[0])]
            writer.writerow(header)
            rows = [dataclasses.asdict(entity).values() for entity in entity_list]
            writer.writerows(rows)

    def export_to_json(self, file: str, entity_list: List[T]) -> None:
        with open(file, 'w') as jsonfile:
            data = [dataclasses.asdict(entity) for entity in entity_list]
            json.dump(data, jsonfile, indent=4)