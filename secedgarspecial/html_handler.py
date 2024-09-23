import requests
import os
import time
import uuid
from random import uniform
from typing import Callable, Any, Optional
from typing import List, Dict, Union
from tenacity import retry, wait_fixed, stop_after_attempt
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import re
import warnings


warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


class HTMLHandler:
    def __init__(self, save_directory: Optional[str] = None):
        if save_directory:
            self.save_directory = save_directory
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

    def fetch_html(self, url: str) -> Union[str, None]:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    @staticmethod
    def fetch_page_login(
        url: str,
        min_wait_seconds: float,
        max_wait_seconds: float,
        stop_after_n: int,
    ) -> Callable[[Callable[..., Any], Optional[str]], None]:
        """
        Curried function that fetches the given URL and retries the request if the page load fails.
        Example usage: fetch_page(driver, url, 10, 3)(lambda: driver.find_element(By.ID, 'foo').text != "failed")

        :param url: URL to fetch
        :param min_wait_seconds: minimum wait time for the request to complete before executing the check method
        :param max_wait_seconds: maximum wait time for the request to complete before executing the check method
        :param stop_after_n: how many times to retry the request before failing
        :return: wrapper function that takes a check method and retries the request if the page load fails
        """
        @retry(
            wait=wait_fixed(uniform(min_wait_seconds, max_wait_seconds)),
            stop=stop_after_attempt(stop_after_n),
            reraise=True,
        )
        def wrapper(err_msg: Optional[str] = None) -> None:
            print(f"Requesting URL: {url}")
            headers = {
                "User-Agent": f"BellingcatEDGARTool_{uuid.uuid4()} contact-tech@bellingcat.com"
            }
            res = requests.get(url, headers=headers)
            randomized_wait = uniform(min_wait_seconds, max_wait_seconds)
            print(f"Waiting {randomized_wait} seconds for the request to complete...")
            time.sleep(randomized_wait)
            if res.status_code != 200:
                # TODO: Put this into log
                print(f"Error for url {url}, with code {res.status_code}")
            else:
                print(f"Successfully fetched URL: {url}")
            return res.text

        return wrapper

    def save_html(self, content, filename):
        try:
            filepath = os.path.join(self.save_directory, filename)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Saved HTML to {filepath}")
        except IOError as e:
            print(f"Error saving HTML to {filename}: {e}")

    def _download_html(self, url, filename):
        content = self.fetch_html(url)
        if content:
            self.save_html(content, filename)

    def _edgar_fetch(self, url, filename):
        content = self.fetch_page_login(url, min_wait_seconds=0.1, max_wait_seconds=1, stop_after_n=3)(lambda x: x is not None)
        if content:
            self.save_html(content, filename)

    def download_html_files(self, data: List[Dict[str, str]]):
        for item in data:
            filename = item.get('id')
            url = item.get('url')
            if (filename and url) and not os.path.exists(os.path.join(self.save_directory, filename)):
                self._edgar_fetch(url, filename)

    @property
    def html_files(self) -> List[str]:
        """List all HTML files in the directory."""
        html_files = [
            file for file in os.listdir(self.save_directory)
            if file.endswith('.html') or file.endswith('.htm')
        ]
        return html_files
    
    @staticmethod
    def parse_html(filepath: str) -> str:
        """Parse HTML file to extract text content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                text = soup.get_text(separator="\n")
                cleaned_text = re.sub(r'\s+', ' ', text)  # Normalize white spaces
                return cleaned_text.strip()
        except IOError as e:
            print(f"Error reading HTML file {filepath}: {e}")
            return ""

    @staticmethod
    def structure_text(text: str) -> Dict[str, str]:
        """Convert extracted text to a structured format."""
        structured_data = {
            "content": text
        }
        return structured_data

    @staticmethod
    def chunk_text(text: str, max_tokens: int = 512) -> List[str]:
        """Chunk text into smaller pieces for LLM processing."""
        words = text.split()
        chunks = [' '.join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]
        return chunks

    def process_html_files(self) -> List[Dict[str, Union[str, List[str]]]]:
        """Process all HTML files in the save directory and prepare them for LLM input."""
        processed_files = []
        for filename in os.listdir(self.save_directory):
            if filename.endswith('.htm') or filename.endswith('.html'):
                text = self.parse_html(os.path.join(self.save_directory, filename))
                processed_files.append({
                    "source": filename,
                    "page_content": text,
                })
        return processed_files
