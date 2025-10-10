from datetime import datetime
from enum import Enum, auto
import re
from bs4 import BeautifulSoup

class CleaningFunction(Enum):
    REMOVE_NEWLINES = auto()
    STRIP = auto()
    TO_INTEGER = auto()
    TO_FLOAT = auto()
    TO_DATE = auto()
    TO_DATETIME = auto()
    COLLAPSE_WHITESPACE = auto()
    TO_LOWERCASE = auto()
    TO_UPPERCASE = auto()
    TO_TITLECASE = auto()
    REPLACE = auto()
    REMOVE = auto()
    ADD_PREFIX = auto()
    ADD_SUFFIX = auto()
    REMOVE_PREFIX = auto()
    REMOVE_SUFFIX = auto()
    EXTRACT_FIRST_NUMBER = auto()
    STRIP_HTML_TAGS = auto()

class Cleaner:
    def __init__(self):
        self.rules_map = {
            CleaningFunction.STRIP: lambda text: text.strip(),
            CleaningFunction.REMOVE_NEWLINES: lambda text: text.replace('\n', ''),
            CleaningFunction.COLLAPSE_WHITESPACE: lambda text: re.sub(r'\s+', ' ', text).strip(),
            CleaningFunction.TO_LOWERCASE: lambda text: text.lower(),
            CleaningFunction.TO_UPPERCASE: lambda text: text.upper(),
            CleaningFunction.TO_TITLECASE: lambda text: text.title(),
            CleaningFunction.TO_INTEGER: self._to_int,
            CleaningFunction.TO_FLOAT: self._to_float,
            CleaningFunction.EXTRACT_FIRST_NUMBER: self._extract_first_number,
            CleaningFunction.STRIP_HTML_TAGS: self._strip_html_tags,
        }

    def _to_int(self, text: str) -> int | str:
        try:
            return int(re.sub(r'[^\d-]', '', text))
        except (ValueError, TypeError):
            return text

    def _to_float(self, text: str) -> float | str:
        try:
            return float(re.sub(r'[^\d,.-]', '', text).replace(',', '.'))
        except (ValueError, TypeError):
            return text

    def _extract_first_number(self, text: str) -> float | str:
        match = re.search(r'(\d[\d,.]*)', text)
        return self._to_float(match.group(1)) if match else text

    def _strip_html_tags(self, text: str) -> str:
        return BeautifulSoup(text, "html.parser").get_text()

    def apply(self, item: str, rules: list) -> str:
        if not isinstance(rules, list):
            return item

        processed_value = item
        for rule in rules:
            try:
                if isinstance(rule, str):
                    enum_member = CleaningFunction[rule]
                    if enum_member in self.rules_map:
                        processed_value = self.rules_map[enum_member](processed_value)
                elif isinstance(rule, dict):
                    enum_member = CleaningFunction[rule.get('name')]
                    if enum_member == CleaningFunction.REMOVE_PREFIX:
                        processed_value = processed_value.removeprefix(rule.get('value'))
                    elif enum_member == CleaningFunction.REMOVE_SUFFIX:
                        processed_value = processed_value.removesuffix(rule.get('value'))
                    elif enum_member == CleaningFunction.ADD_PREFIX:
                        processed_value = rule.get('value') + processed_value
                    elif enum_member == CleaningFunction.ADD_SUFFIX:
                        processed_value = processed_value + rule.get('value')
                    elif enum_member == CleaningFunction.TO_DATE:
                        processed_value = datetime.strptime(processed_value, rule.get('format')).date()
                    elif enum_member == CleaningFunction.TO_DATETIME:
                        processed_value = datetime.strptime(processed_value, rule.get('format'))
                    elif enum_member == CleaningFunction.REMOVE:
                        processed_value = processed_value.replace(rule.get('value'), "")
                    elif enum_member == CleaningFunction.REPLACE:
                        processed_value = processed_value.replace(rule.get('old'), rule.get('new'))
            except(KeyError, IndexError, TypeError):
                print(f"Warning: Could not apply invalid cleaning rule: {rule}")
                continue
        return processed_value