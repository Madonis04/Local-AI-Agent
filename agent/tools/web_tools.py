# agent/tools/web_tools.py
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from urllib.parse import urlparse, quote_plus
import json
from datetime import datetime

from agent.tools.base_tool import BaseTool
from config_manager import config
from logger import logger


class GoogleSearchTool(BaseTool):
    """Search Google and return structured results."""
    
    name = "google_search"
    description = "Search Google for information. Argument: search query (e.g., 'Python tutorials', 'weather in Mumbai')"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def execute(self, argument: str) -> str:
        try:
            if not argument or argument.strip() == "":
                return "Error: Please provide a search query."
            
            query = argument.strip()
            logger.info(f"Searching Google for: {query}")
            
            # Use DuckDuckGo HTML (simpler, no API key needed)
            # Google blocks automated requests, so we use DuckDuckGo instead
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return f"Error: Search service returned status {response.status_code}"
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse search results
            results = []
            result_divs = soup.find_all('div', class_='result')
            
            for i, result in enumerate(result_divs[:5], 1):  # Top 5 results
                try:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No description available"
                        
                        results.append({
                            'position': i,
                            'title': title,
                            'url': url,
                            'snippet': snippet[:150] + '...' if len(snippet) > 150 else snippet
                        })
                except Exception as e:
                    logger.debug(f"Error parsing result {i}: {e}")
                    continue
            
            if not results:
                return f"No results found for '{query}'"
            
            # Format output
            output = f"🔍 Search Results for '{query}':\n"
            output += "=" * 60 + "\n\n"
            
            for result in results:
                output += f"{result['position']}. {result['title']}\n"
                output += f"   🔗 {result['url']}\n"
                output += f"   📝 {result['snippet']}\n\n"
            
            logger.info(f"Found {len(results)} search results")
            return output.strip()
            
        except requests.Timeout:
            return "Error: Search request timed out"
        except requests.RequestException as e:
            logger.error(f"Search request error: {e}")
            return "Error: Could not connect to search service"
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Error: Search failed - {str(e)}"


class WebScraperTool(BaseTool):
    """Extract text content from any webpage."""
    
    name = "scrape_webpage"
    description = "Extract text content from a webpage. Argument: URL (e.g., 'https://example.com')"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def execute(self, argument: str) -> str:
        try:
            if not argument or argument.strip() == "":
                return "Error: Please provide a URL to scrape."
            
            url = argument.strip()
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            logger.info(f"Scraping webpage: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            # Limit output length
            max_length = 2000
            if len(text) > max_length:
                text = text[:max_length] + f"\n\n... [Content truncated. Total length: {len(text)} characters]"
            
            # Get page title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "Unknown"
            
            output = f"📄 Scraped Content from: {url}\n"
            output += f"📌 Title: {title_text}\n"
            output += "=" * 60 + "\n\n"
            output += text
            
            logger.info(f"Successfully scraped {len(text)} characters from {url}")
            return output
            
        except requests.HTTPError as e:
            return f"Error: HTTP {e.response.status_code} - Could not access webpage"
        except requests.Timeout:
            return "Error: Request timed out"
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return f"Error: Could not connect to webpage - {str(e)}"
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return f"Error: Failed to scrape webpage - {str(e)}"


class WebContentReaderTool(BaseTool):
    """Read and summarize main content from a webpage."""
    
    name = "read_webpage"
    description = "Read main content from a webpage (article text). Argument: URL (e.g., 'https://blog.example.com/article')"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def execute(self, argument: str) -> str:
        try:
            if not argument or argument.strip() == "":
                return "Error: Please provide a URL to read."
            
            url = argument.strip()
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            logger.info(f"Reading webpage: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find main content (common article tags)
            main_content = None
            for tag in ['article', 'main', ['div', {'class': 'content'}], ['div', {'class': 'article'}]]:
                main_content = soup.find(tag)
                if main_content:
                    break
            
            if not main_content:
                # Fallback to body
                main_content = soup.find('body')
            
            if not main_content:
                return "Error: Could not find main content on page"
            
            # Remove unwanted elements
            for element in main_content(['script', 'style', 'nav', 'footer', 'aside', 'header']):
                element.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "Unknown"
            
            # Try to find h1 heading
            h1 = main_content.find('h1')
            heading = h1.get_text(strip=True) if h1 else None
            
            # Get paragraphs
            paragraphs = main_content.find_all('p')
            text_blocks = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            
            content = '\n\n'.join(text_blocks)
            
            # Limit length
            max_length = 1500
            if len(content) > max_length:
                content = content[:max_length] + f"\n\n... [Content truncated. Total: {len(content)} chars]"
            
            output = f"📰 Article Content\n"
            output += "=" * 60 + "\n"
            output += f"🔗 URL: {url}\n"
            output += f"📌 Title: {title_text}\n"
            if heading:
                output += f"📝 Heading: {heading}\n"
            output += "=" * 60 + "\n\n"
            output += content
            
            logger.info(f"Successfully read article from {url}")
            return output
            
        except requests.HTTPError as e:
            return f"Error: HTTP {e.response.status_code} - Could not access webpage"
        except requests.Timeout:
            return "Error: Request timed out"
        except Exception as e:
            logger.error(f"Reading error: {e}")
            return f"Error: Failed to read webpage - {str(e)}"


class DownloadFileTool(BaseTool):
    """Download files from URLs."""
    
    name = "download_file"
    description = "Download a file from URL. Argument: URL of the file to download (e.g., 'https://example.com/file.pdf')"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        
        # Create downloads directory
        data_dir = Path(config.get('Paths', 'data_directory', fallback='.agent_data'))
        self.downloads_dir = data_dir / 'downloads'
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, argument: str) -> str:
        try:
            if not argument or argument.strip() == "":
                return "Error: Please provide a URL to download."
            
            url = argument.strip()
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            logger.info(f"Downloading file from: {url}")
            
            # Get filename from URL
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name
            
            if not filename or '.' not in filename:
                # Generate filename if not available
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"download_{timestamp}"
            
            filepath = self.downloads_dir / filename
            
            # Download file with streaming
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            
            # Save file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Get actual file size
            file_size = filepath.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            logger.info(f"File downloaded successfully: {filepath}")
            
            output = f"✓ File downloaded successfully!\n\n"
            output += f"📁 Saved to: {filepath}\n"
            output += f"📊 Size: {file_size_mb:.2f} MB\n"
            output += f"📝 Filename: {filename}"
            
            return output
            
        except requests.HTTPError as e:
            return f"Error: HTTP {e.response.status_code} - Could not download file"
        except requests.Timeout:
            return "Error: Download timed out (file too large or slow connection)"
        except Exception as e:
            logger.error(f"Download error: {e}")
            return f"Error: Download failed - {str(e)}"


class URLInfoTool(BaseTool):
    """Get information about a URL (status, headers, metadata)."""
    
    name = "url_info"
    description = "Get information about a URL (status, headers, page info). Argument: URL (e.g., 'https://example.com')"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def execute(self, argument: str) -> str:
        try:
            if not argument or argument.strip() == "":
                return "Error: Please provide a URL."
            
            url = argument.strip()
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            logger.info(f"Getting info for URL: {url}")
            
            # Make HEAD request first (faster)
            response = requests.head(url, headers=self.headers, timeout=10, allow_redirects=True)
            
            # If HEAD fails, try GET
            if response.status_code >= 400:
                response = requests.get(url, headers=self.headers, timeout=10)
            
            # Parse domain info
            parsed = urlparse(url)
            
            output = f"🔗 URL Information\n"
            output += "=" * 60 + "\n"
            output += f"📍 URL: {url}\n"
            output += f"🌐 Domain: {parsed.netloc}\n"
            output += f"📊 Status Code: {response.status_code} ({response.reason})\n"
            output += f"🔄 Final URL: {response.url}\n\n"
            
            # Headers
            output += "📋 Response Headers:\n"
            interesting_headers = ['Content-Type', 'Content-Length', 'Server', 'Last-Modified', 'Date']
            for header in interesting_headers:
                if header in response.headers:
                    value = response.headers[header]
                    if header == 'Content-Length':
                        size_mb = int(value) / (1024 * 1024)
                        value = f"{size_mb:.2f} MB"
                    output += f"   • {header}: {value}\n"
            
            # Try to get page title if it's HTML
            if 'text/html' in response.headers.get('Content-Type', ''):
                try:
                    html_response = requests.get(url, headers=self.headers, timeout=10)
                    soup = BeautifulSoup(html_response.text, 'html.parser')
                    title = soup.find('title')
                    if title:
                        output += f"\n📌 Page Title: {title.get_text(strip=True)}"
                except:
                    pass
            
            logger.info(f"URL info retrieved successfully")
            return output
            
        except requests.Timeout:
            return "Error: Request timed out"
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return f"Error: Could not access URL - {str(e)}"
        except Exception as e:
            logger.error(f"URL info error: {e}")
            return f"Error: Failed to get URL info - {str(e)}"
