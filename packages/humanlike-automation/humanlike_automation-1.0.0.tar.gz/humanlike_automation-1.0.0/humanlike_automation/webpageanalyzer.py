import logging
from selenium import webdriver
from bs4 import BeautifulSoup, Tag
import json
from .utility import Utility
from .webpagehandler import WebPageHandler


class WebpageAnalyzer:
    """
    Analyzer for web pages with AI integration capabilities
    """
    
    def __init__(self, driver, ai_api_key=None):
        """
        Initialize WebpageAnalyzer
        
        Args:
            driver: Selenium WebDriver instance
            ai_api_key: Optional API key for future AI integration
        """
        self.driver = driver
        self.ai_api_key = ai_api_key
        self.webpagehandler = WebPageHandler(self.driver)
        self.utility = Utility()
        
        # Configure logging
        self.logger = logging.getLogger(__name__)

    def load_page(self, url):
        """Load a web page in the browser."""
        self.driver.get(url)    

    def download_html_content(self):
        """Get the current page HTML source."""
        return self.driver.page_source

    def parse_html_for_elements(self, html_content):
        """Parse HTML content and extract interactive elements."""
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = soup.find_all(['a', 'button', 'input', 'select', 'div'])
        return elements

    def generate_xpaths(self, elements):
        """Generate XPath expressions for given elements."""
        xpaths = []
        for element in elements:
            if isinstance(element, Tag):
                try:
                    xpath = self.webpagehandler.get_xpath(element)
                    xpaths.append(xpath)
                except Exception as e:
                    self.logger.warning(f"Could not generate XPath for element: {e}")
                    xpaths.append("//UNKNOWN")
        return xpaths

    def analyze_page(self, url):
        """
        Perform comprehensive page analysis.
        
        Args:
            url: URL to analyze
            
        Returns:
            JSON string with page analysis data
        """
        self.load_page(url)
        html_content = self.download_html_content()
        elements = self.parse_html_for_elements(html_content)
        xpaths = self.generate_xpaths(elements)

        data = {"url": url, "elements": []}
        for element, xpath in zip(elements, xpaths):
            element_data = {
                "tag": element.name,
                "text": element.get_text(strip=True),
                "xpath": xpath,
                "attributes": {attr: element[attr] for attr in element.attrs}
            }
            data["elements"].append(element_data)

        # Future AI analysis integration
        if self.ai_api_key:
            # TODO: Implement AI analysis when needed
            data["ai_analysis"] = "AI analysis available with API key"
        
        return json.dumps(data, indent=4)
