import datetime
import unittest
from unittest.mock import patch, mock_open, MagicMock
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, field

from src.scrapper_json_jawron.scrapper import get_rules_from_file, get_element, get_response, Scrapper

@dataclass
class MockArticle:
    title: str = ""
    description: str = ""
    url: str = ""
    metadata: str = ""
    content: str = ""
    extra: dict = field(default_factory=dict)


SAMPLE_HTML = """
<html>
<head><title>Test Page</title></head>
<body>
    <div id="main-content">
        <h1>Main Title</h1>
        <p>Some paragraph text.</p>
        <ul class="item-list">
            <li class="item"><a href="/article1">Article 1</a><span>Meta 1</span><span>2025-06-12</span></li>
            <li>Paragraph</li>
            <li class="item"><a href="/article2">Article 2</a><span>Meta 1</span></li>
            <li class="special-item"><a href="/article3">Article 3</a><span>Meta 3</span></li>
        </ul>
        <div id="footer" data-info="footer-info">Footer content</div>
    </div>
</body>
</html>
"""

SAMPLE_XML = """
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Example Feed</title>
  <entry>
    <title>Atom-Powered Robots Run Amok</title>
    <link href="http://example.org/2003/12/13/atom03" />
    <summary>Some text.</summary>
  </entry>
  <entry>
    <title>Second Entry</title>
    <link href="http://example.org/2003/12/14/atom04" />
    <summary>More text.</summary>
  </entry>
</feed>
"""


class TestHelperFunctions(unittest.TestCase):
    """Tests for standalone helper functions."""

    def test_get_rules_from_file_success(self):
        """Should correctly read and parse a valid JSON file."""
        mock_json_content = '{"key": "value", "number": 123}'
        m = mock_open(read_data=mock_json_content)
        with patch('builtins.open', m):
            rules = get_rules_from_file('dummy/path/rules.json')
            self.assertEqual(rules, {"key": "value", "number": 123})

    def test_get_rules_from_file_not_found(self):
        """Should raise FileNotFoundError for a non-existent file."""
        with self.assertRaises(FileNotFoundError):
            get_rules_from_file('non_existent_file.json')

    @patch('requests.get')
    def test_get_response_success(self, mock_get):
        """Should return a response object on a successful request."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = get_response("https://example.com", retries=3, delay=2)
        self.assertIsInstance(response, bytes)
        mock_get.assert_called_once_with("https://example.com", headers=unittest.mock.ANY)

    @patch('requests.get')
    def test_get_response_http_error(self, mock_get):
        """Should raise an Exception on an HTTP error."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError
        mock_get.return_value = mock_response

        with self.assertRaises(Exception, HTTPError):
            get_response("https://example.com/notfound", retries=3, delay=2)


class TestGetElement(unittest.TestCase):
    """Tests for the BeautifulSoup element selection logic."""

    def setUp(self):
        """Set up a BeautifulSoup object for all tests in this class."""
        self.soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

    def test_get_single_element_text(self):
        """Should select a single element and get its text."""
        rules = {'selector': 'h1', 'attribute': 'text', 'item_type': 'single'}
        result = get_element(self.soup, rules)
        self.assertEqual(result, "Main Title")

    def test_get_single_element_attribute(self):
        """Should select a single element and get a specific attribute."""
        rules = {'selector': '#footer', 'attribute': 'data-info', 'item_type': 'single'}
        result = get_element(self.soup, rules)
        self.assertEqual(result, "footer-info")

    def test_get_single_element_itself(self):
        """Should select and return the element Tag object itself."""
        rules = {'selector': 'p', 'attribute': 'element', 'item_type': 'single'}
        result = get_element(self.soup, rules)
        self.assertIsInstance(result, Tag)
        self.assertEqual(result.name, 'p')
        self.assertEqual(result.get_text(), "Some paragraph text.")

    def test_get_nth_element(self):
        """Should select and return the nth element Tag and get a specific attribute."""
        rules = {'selector': 'li', 'attribute': 'text', 'item_type': 'single', 'index': 1}
        result = get_element(self.soup, rules)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Paragraph")

    def test_get_list_of_elements(self):
        """Should select and return a list of matching elements."""
        rules = {'selector': 'li.item', 'item_type': 'list'}
        result = get_element(self.soup, rules)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].select_one('a').text, "Article 1")

    def test_element_not_found(self):
        """Should return an empty string when a single element is not found."""
        rules = {'selector': '.non-existent-class', 'item_type': 'single'}
        result = get_element(self.soup, rules)
        self.assertEqual(result, "")


class TestScrapper(unittest.TestCase):
    """Tests for the main Scrapper class and its methods."""

    def setUp(self):
        """Set up a BeautifulSoup object for parsing."""
        self.html_soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

    def test_iterate_elements(self):
        """Should correctly process an element based on a set of rules."""
        scrapper = Scrapper({}, MockArticle)
        entry_element = self.html_soup.select_one('li.item')  # First li.item

        rules = {
            "elements": {
                "url": {
                    "selector": "a",
                    "attribute": "href",
                    "transform": [{"name": "ADD_PREFIX", "value": "http://base.url"}, "TO_UPPERCASE"]
                },
                "title": {
                    "selector": "a", "attribute": "text", "transform": [{"name": "REMOVE", "value": " 1"}]
                },
                "metadata": {
                    "selector": "span", "attribute": "text", "index": 1, "transform": [{"name": "TO_DATE", "format": "%Y-%m-%d"}]
                }
            }
        }
        result_dict = scrapper.iterate_elements(entry_element, rules)
        expected = {
            'url': 'http://base.url/article1'.upper(),
            'title': 'Article',
            'metadata': datetime.datetime(2025, 6, 12).date(),
        }
        self.assertEqual(result_dict, expected)

    def test_iterate_nested_elements(self):
        """Should correctly process a nested element based on a set of rules."""
        scrapper = Scrapper({}, MockArticle)
        entry_element = self.html_soup.select_one('li.item')
        rules = {
            "elements": {
                "url": {
                    "selector": "a",
                    "attribute": "element",
                    "elements": {
                        "link": {"attribute": "href", "transform": [{"name": "ADD_PREFIX", "value": "http://base.url"}]},
                        "text": {"attribute": "text"},
                    }
                },
            }
        }
        result_dict = scrapper.iterate_elements(entry_element, rules)
        expected = {
            'url': {
                'link': 'http://base.url/article1',
                'text': 'Article 1',
            }
        }
        self.assertEqual(result_dict, expected)

    def test_scrap_list_html(self):
        """Should correctly scrape a list of items from an HTML source."""
        rules = {
            "type": "html",
            "url": "https://example.com/list",
            "root": {"selector": "#main-content", "attribute": "element"},
            "entry": {"selector": ".item-list li", "item_type": "list"},
            "elements": {
                "url": {"selector": "a", "attribute": "href"},
                "title": {"selector": "a", "attribute": "text"},
                "metadata": {"selector": "span", "attribute": "text"}
            }
        }

        scrapper = Scrapper(rules, MockArticle)

        results = scrapper.scrap_list(content_file=SAMPLE_HTML)

        self.assertEqual(len(results), 4)
        self.assertIsInstance(results[0], MockArticle)
        self.assertEqual(results[0].title, "Article 1")
        self.assertEqual(results[0].url, "/article1")
        self.assertEqual(results[2].metadata, "Meta 1")

    def test_scrap_list_xml(self):
        """Should correctly scrape a list of items from an XML source."""
        rules = {
            "type": "xml", "url": "http://example.com/feed.xml",
            "namespace": {"atom": "http://www.w3.org/2005/Atom"},
            "entry": "atom:entry",
            "elements": {
                "title": {"selector": "atom:title", "attribute": "text"},
                "url": {"selector": "atom:link", "attribute": "href"},
                "description": {"selector": "atom:summary", "attribute": "text", "suffix": "..."}
            }
        }

        scrapper = Scrapper(rules, MockArticle)
        results = scrapper.scrap_list(content_file=SAMPLE_XML)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, "Atom-Powered Robots Run Amok")
        self.assertEqual(results[0].url, "http://example.org/2003/12/13/atom03")
        self.assertEqual(results[0].description, "Some text....")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
