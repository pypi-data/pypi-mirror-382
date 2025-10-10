# ScrapperJson

### A simple automated scrapper with support for JSON structure of scrapping rules

## Installation:
```bash
pip install scrapper-json-jawron
```

## Usage:
```python
from scrapper-json-jawron.scrapper import Scrapper, get_rules_from_file
from dataclasses import dataclass

# example result dataclass
@dataclass
class Article:
    url: str
    title: str
    content: str = ""
        
rules = get_rules_from_file("example.json")

# create templated scrapper
scr = Scrapper(rules, Article)

# scrap entity list
result = scr.scrap_list()

# scrap entity details
entity_rules = get_rules_from_file("example_entity.json")
for entity in result:
    entity_result = scr.scrap_entity(entity_rules, entity)
```

## JSON structure

### Main options
* **type:** Defines the type of scrapping data, can be either `xml` or `html`
* **pagination:** Defines if the scrapping should perform pagination using a templated url from rules file, `default: false`
* **pagination_limit:** Defines the number of pages to scrape, `default: 100`
* **url**: Defines the url of XML feed or HTML page that will be scrapped
* **root**: Defines the root element at which scrapping begins
* **entry**: Defines the particular entries elements which will be scrapped to separate objects
* **elements**: Defines the scrapped properties of an entity

### Elements options
* **selector:** Defines the CSS or XML selector for the element
* **index:** Defines the index of the element to scrape, if a selector returns multiple elements
* **item_type:** Defines the type of item, can be either `single` or `list`, `default: single`
* **attribute:** Defines the attribute of element which will be scrapped, if scrapping text use `text`, else use the name of the attribute. You can also scrape an element as an object to use in nested properties. `default: text`
* **transform:** Defines the cleaning and transformation options to be executed on the result property
* **prefix:** Defines the prefix which is added to the result property. To be moved in next version into transform.
* **suffix:** Defines the suffix which is added to the result property. To be moved in next version into transform.
* **remove:** Defines the text which is to be removed from the result property. To be moved in next version into transform.
* **replace:** Defines the text which is to be replaced from the result property. To be moved in next version into transform.
* **elements**: Defines the scrapped properties of an entity

### Cleaning and transformation options
#### Simple options (pass as string)
* **REMOVE_NEWLINES:**
* **STRIP:**
* **TO_INTEGER:**
* **TO_FLOAT:**
* **COLLAPSE_WHITESPACE:**
* **TO_LOWERCASE:**
* **TO_UPPERCASE:**
* **TO_TITLECASE:**
* **EXTRACT_FIRST_NUMBER:**
* **STRIP_HTML_TAGS:**

#### Advanced options (pass as a dictionary)
* **REMOVE_PREFIX:**
* **REMOVE_SUFFIX:**
* **TO_DATE:**
* **TO_DATETIME:**

### Example HTML
```json
{
  "type": "html",
  "url": "https://www.technewsworld.com/archive",
  "root": {
    "selector": "div.category-article-list",
    "attribute": "element"
  },
  "entry": {
    "selector": "div.search-item",
    "attribute": "element",
    "item_type": "list"
  },
  "elements": {
    "title": {
      "selector": "div.search-txt a h2",
      "attribute": "text",
      "transform": ["REMOVE_NEWLINES", "STRIP", "TO_TITLECASE"]
    },
    "url": {
      "selector": "div.search-txt a",
      "attribute": "href"
    }
  }
}
```

### Example XML
```json
{
  "type": "xml",
  "url": "https://www.cijeurope.com/rss/posts/en.xml",
  "root": "channel",
  "entry": "item",
  "elements": {
    "title": {
      "selector": "title",
      "attribute": "text"
    },
    "url": {
      "selector": "link",
      "attribute": "text"
    }
  }
}
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change or add.

## Plans for future
* Pagination handling ✅
* Network error handling and retries ✅
* More export options (file etc.) ✅
* Rule-based data transformation and cleaning ✅ 
* Custom pagination functions ✅ 
* Login handling, session management
* Export to database
* Support for asynchronous requests