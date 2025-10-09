import requests #need pip install requests
from bs4 import BeautifulSoup # need pip install beautifulsoup4
from readability import Document # need pip install readability-lxml
from .log_set_up import setup_logging
import time
from typing import Union
from ddgs import DDGS # need  pip install ddgs
from .utils import enforce_type

class WebScraper:
    def __init__(self, user_agent: str = "Mozilla/5.0", num_results: int = 5, limit_word_per_url : int = 500):
        enforce_type(user_agent, str, "user_agent")
        enforce_type(num_results, int, "num_results")
        enforce_type(limit_word_per_url, int, "limit_word_per_url")
        self.user_agent = user_agent
        self.num_results = num_results
        self.limit_word = limit_word_per_url
        #for logging only this class rather
        self.logger = setup_logging(self.__class__.__name__)
        
    def _url_search(self, query : str, region : str) -> list:
        """helper function that performs a search based on a query and returns a list of URLs from the top results"""
        self.logger.debug("Trying to return the list of urls")
        try:
            with DDGS() as ddgs:
                results_generator = ddgs.text(query=query, region=region, max_results=self.num_results )
                
                # Convert them to a list
                results = list(results_generator)
                
                # Extract only the URLs from the results
                urls = [result['href'] for result in results]
                return urls
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []

    def _fetch_html(self, url : str) -> str:
        """helper function that downloads the HTML content of a given URL."""
        headers = {"User-Agent": self.user_agent}  #mimic a real browser
        resp = requests.get(url, headers=headers)  # GET the page
        resp.raise_for_status()
        if not resp.text.strip():
            self.logger.warning(f"Empty response from URL: {url}")
            
        self.logger.debug("Fetching html completed")
        return resp.text

    def _extract_with_readability(self, html : str) -> str:
        """ helper function that takes the HTML content of a web page and extracts its main, readable text."""
        doc = Document(html)          # build readability DOM
        summary_html = doc.summary()  # HTML content
        # BeautifulSoup to get plain text
        self.logger.debug("Trying to get the text from html")
        return BeautifulSoup(summary_html, "html.parser").get_text()

    def search(self, prompt : str = None, region : str = "vn-vi", grouped : bool = True) -> Union[str, list]:
        """Performs search and extracted text of the web search for the given prompt, length of each page is limited by the limit_word when init class\n
        If grouped=True, returns all extracted text as one string\n
        If grouped=False, returns a list of extracted texts (one per URL).
        """
        enforce_type(prompt, str, "prompt")
        enforce_type(region, str, "region")
        enforce_type(grouped, bool, "grouped")
        
        results = []
        urls = self._url_search(prompt, region)
        self.logger.debug(f"URLS: {urls}")

        for url in urls:
            try:
                result = self._fetch_html(url)
                text = self._extract_with_readability(result)
                results.append(text[:self.limit_word])
            except Exception:
                pass  # ignore
            finally:
                time.sleep(0.5) #delay to not trigger bot

        if grouped:
            return " ".join(results).replace("\n\n", "\n")
        return results
    
    def quick_search(self, prompt: str = None, region : str = "vn-vi", grouped: bool = True) -> Union[str, list]:
        """Performs the default search using DuckDuckGo API.\n
        If grouped=True, returns all answers joined as one string.\n
        If grouped=False, returns a list of answers.
        """
        enforce_type(prompt, str, "prompt")
        enforce_type(region, str, "region")
        enforce_type(grouped, bool, "grouped")
        
        try:
            with DDGS() as ddgs:
                results_generator = ddgs.text(query=prompt, region=region, max_results=self.num_results )
                results = list(results_generator)
                answers = [result.get('body', '') for result in results]

                if grouped:
                    return " ".join(answers).replace("\n\n", "\n")
                return answers
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return [] if not grouped else ""
    
    def list_ddgs_regions(self, keyword: str = None) -> None:
        """Print supported ddgs regions. Optionally filter by a keyword."""
        enforce_type(keyword, (type(None), str), "keyword")
        regions = {
            "xa-ar": "Arabia (Arabic)",
            "xa-en": "Arabia (English)",
            "ar-es": "Argentina (Spanish)",
            "au-en": "Australia (English)",
            "at-de": "Austria (German)",
            "be-fr": "Belgium (French)",
            "be-nl": "Belgium (Dutch/Flemish)",
            "br-pt": "Brazil (Portuguese)",
            "bg-bg": "Bulgaria (Bulgarian)",
            "ca-en": "Canada (English)",
            "ca-fr": "Canada (French)",
            "ct-ca": "Catalan (Catalonia/Canada)",
            "cl-es": "Chile (Spanish)",
            "cn-zh": "China (Chinese)",
            "co-es": "Colombia (Spanish)",
            "hr-hr": "Croatia (Croatian)",
            "cz-cs": "Czech Republic (Czech)",
            "dk-da": "Denmark (Danish)",
            "ee-et": "Estonia (Estonian)",
            "fi-fi": "Finland (Finnish)",
            "fr-fr": "France (French)",
            "de-de": "Germany (German)",
            "gr-el": "Greece (Greek)",
            "hk-tzh": "Hong Kong (Traditional Chinese)",
            "hu-hu": "Hungary (Hungarian)",
            "in-en": "India (English)",
            "id-id": "Indonesia (Indonesian)",
            "id-en": "Indonesia (English)",
            "ie-en": "Ireland (English)",
            "il-he": "Israel (Hebrew)",
            "it-it": "Italy (Italian)",
            "jp-jp": "Japan (Japanese)",
            "kr-kr": "Korea (Korean)",
            "lv-lv": "Latvia (Latvian)",
            "lt-lt": "Lithuania (Lithuanian)",
            "xl-es": "Latin America (Spanish)",
            "my-ms": "Malaysia (Malay)",
            "my-en": "Malaysia (English)",
            "mx-es": "Mexico (Spanish)",
            "nl-nl": "Netherlands (Dutch)",
            "nz-en": "New Zealand (English)",
            "no-no": "Norway (Norwegian)",
            "pe-es": "Peru (Spanish)",
            "ph-en": "Philippines (English)",
            "ph-tl": "Philippines (Tagalog)",
            "pl-pl": "Poland (Polish)",
            "pt-pt": "Portugal (Portuguese)",
            "ro-ro": "Romania (Romanian)",
            "ru-ru": "Russia (Russian)",
            "sg-en": "Singapore (English)",
            "sk-sk": "Slovak Republic (Slovak)",
            "sl-sl": "Slovenia (Slovenian)",
            "za-en": "South Africa (English)",
            "es-es": "Spain (Spanish)",
            "se-sv": "Sweden (Swedish)",
            "ch-de": "Switzerland (German)",
            "ch-fr": "Switzerland (French)",
            "ch-it": "Switzerland (Italian)",
            "tw-tzh": "Taiwan (Traditional Chinese)",
            "th-th": "Thailand (Thai)",
            "tr-tr": "Turkey (Turkish)",
            "ua-uk": "Ukraine (Ukrainian)",
            "uk-en": "United Kingdom (English)",
            "us-en": "United States (English)",
            "ue-es": "United States (Spanish)",
            "ve-es": "Venezuela (Spanish)",
            "vn-vi": "Vietnam (Vietnamese)",
        }

        if keyword:
            keyword = keyword.lower()
            filtered = {k: v for k, v in regions.items() if keyword in v.lower() or keyword in k.lower()}
            if not filtered:
                print(f"No regions found for keyword: {keyword}")
                return
            for code, desc in filtered.items():
                print(f"{code:7} -> {desc}")
        else:
            for code, desc in regions.items():
                print(f"{code:7} -> {desc}")