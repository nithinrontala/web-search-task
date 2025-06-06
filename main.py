import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse

import logging

logging.basicConfig(level=logging.INFO)

class WebCrawler:
   def __init__(self):
       self.index = defaultdict(list)
       self.visited = set()


   def crawl(self, url, base_url=None):
       if url in self.visited:
           return
       self.visited.add(url)

       try:
           response = requests.get(url)
           soup = BeautifulSoup(response.text, 'html.parser')
           self.index[url] = soup.get_text()

           for link in soup.find_all('a'):
               href = link.get('href')
               if href:
                       href = urljoin(base_url or url, href)
                       if href.startswith(base_url or url):
                           self.crawl(href, base_url=base_url or url)
       except Exception as e:
           logging.error(f"Error crawling {url}: {e}")


   def search(self, keyword):
       results = []
       for url, text in self.index.items():
           if keyword.lower() in text.lower():
               results.append(url)
       return results


   def print_results(self, results):
       if results:
           print("Search results:")
           for result in results:
               print(f"- {result}")
       else:
           print("No results found.")


def main():
   crawler = WebCrawler()
   start_url = "https://example.com"
   crawler.crawl(start_url)


   keyword = "test"
   results = crawler.search(keyword)
   crawler.print_results(results)


import unittest
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse


class WebCrawlerTests(unittest.TestCase):
   @patch('requests.get')
   def test_crawl_success(self, mock_get):
       sample_html = """
       <html><body>
           <h1>Welcome!</h1>
           <a href="/about">About Us</a>
           <a href="https://www.external.com">External Link</a>
       </body></html>
       """
       mock_response = MagicMock()
       mock_response.text = sample_html
       mock_get.return_value = mock_response


       crawler = WebCrawler()
       crawler.crawl("https://example.com")

       self.assertIn("https://example.com/about", crawler.visited)
       self.assertNotIn("https://www.external.com", crawler.visited)
       self.assertIn("https://example.com", crawler.index)
       self.assertIn("https://example.com/about", crawler.index)


   @patch('requests.get')
   def test_crawl_already_visited(self, mock_get):
       crawler = WebCrawler()
       crawler.visited.add("https://example.com")
       crawler.crawl("https://example.com")
       mock_get.assert_not_called()


   @patch('requests.get')
   def test_crawl_relative_and_absolute_links(self, mock_get):
       html = """
       <html><body>
           <a href="/page1">Page1</a>
           <a href="https://example.com/page2">Page2</a>
       </body></html>
       """
       mock_response = MagicMock()
       mock_response.text = html
       mock_get.return_value = mock_response
       crawler = WebCrawler()
       crawler.crawl("https://example.com")
       self.assertIn("https://example.com/page1", crawler.visited)
       self.assertIn("https://example.com/page2", crawler.visited)


   @patch('requests.get')
   def test_crawl_error(self, mock_get):
       mock_get.side_effect = requests.exceptions.RequestException("Test Error")
       crawler = WebCrawler()
       crawler.crawl("https://example.com")
       self.assertIn("https://example.com", crawler.visited)


   def test_search_found_and_not_found(self):
       crawler = WebCrawler()
       crawler.index["page1"] = "This has the keyword"
       crawler.index["page2"] = "No keyword here"
       results = crawler.search("keyword")
       self.assertEqual(sorted(results), ["page1", "page2"])
       results = crawler.search("missing")
       self.assertEqual(results, [])


   def test_search_empty_index(self):
       crawler = WebCrawler()
       results = crawler.search("anything")
       self.assertEqual(results, [])


   def test_print_results_some(self):
       import io
       from contextlib import redirect_stdout
       crawler = WebCrawler()
       f = io.StringIO()
       with redirect_stdout(f):
           crawler.print_results(["https://test.com/result"])
       output = f.getvalue()
       self.assertIn("Search results:", output)
       self.assertIn("- https://test.com/result", output)


   def test_print_results_none(self):
       import io
       from contextlib import redirect_stdout
       crawler = WebCrawler()
       f = io.StringIO()
       with redirect_stdout(f):
           crawler.print_results([])
       output = f.getvalue()
       self.assertIn("No results found.", output)


   @patch('requests.get')
   def test_crawl_invalid_html(self, mock_get):
       mock_response = MagicMock()
       mock_response.text = "<html><body><a href='bad'></body></html>"
       mock_get.return_value = mock_response
       crawler = WebCrawler()
       crawler.crawl("https://example.com")
       self.assertIn("https://example.com", crawler.index)


   @patch('requests.get')
   def test_crawl_handles_non_200(self, mock_get):
       mock_response = MagicMock()
       mock_response.text = ""
       mock_response.status_code = 404
       mock_get.return_value = mock_response
       crawler = WebCrawler()
       crawler.crawl("https://example.com")
       self.assertIn("https://example.com", crawler.index)


if __name__ == "__main__":
   unittest.main()  # Run unit tests
   main()  # Run your main application logic