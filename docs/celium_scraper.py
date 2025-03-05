#!/usr/bin/env python3
# celium_scraper.py
# A script to scrape Celium miner documentation and generate a resource document

import requests
from bs4 import BeautifulSoup
import os
import time
import re
import logging
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL for Celium documentation
BASE_URL = "https://celiumcompute.ai"
MINER_DOCS_URL = f"{BASE_URL}/docs/category/miner"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "celium_miner_resources.md")

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def fetch_page(url):
    """Fetch a web page and return its BeautifulSoup object"""
    try:
        logger.info(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def extract_links_from_page(soup, base_url):
    """Extract all links from the miner documentation page"""
    links = []
    
    # Look for links in the sidebar navigation or main content area
    # Adjust selectors based on actual page structure
    article_links = soup.select('a[href^="/docs/"]')
    
    for link in article_links:
        href = link.get('href')
        if href and '/docs/' in href and not href.endswith('category/miner'):
            # Make sure we have the full URL
            full_url = urljoin(base_url, href)
            links.append(full_url)
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(links))

def extract_content(soup):
    """Extract the main content from a documentation page"""
    # Find the main content area - adjust selector based on page structure
    content_div = soup.select_one('main article')
    
    if not content_div:
        logger.warning("Main content area not found")
        return {"title": "Content not found", "content": ""}
    
    # Extract the title
    title_elem = content_div.select_one('h1')
    title = title_elem.get_text() if title_elem else "Untitled"
    
    # Extract content text
    # We'll keep the HTML structure for now, then clean it up when writing to file
    content = str(content_div)
    
    return {"title": title, "content": content}

def clean_html_content(html_content):
    """Clean HTML content to create a readable markdown document"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract text with basic formatting
    text = ""
    for element in soup.find_all():
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # Add appropriate markdown heading
            level = int(element.name[1])
            text += '#' * level + ' ' + element.get_text().strip() + '\n\n'
        elif element.name == 'p':
            text += element.get_text().strip() + '\n\n'
        elif element.name == 'li':
            # Add list items with proper formatting
            if element.parent.name == 'ol':
                text += '1. ' + element.get_text().strip() + '\n'
            else:
                text += '* ' + element.get_text().strip() + '\n'
        elif element.name == 'pre' or element.name == 'code':
            # Format code blocks
            text += '```\n' + element.get_text() + '\n```\n\n'
    
    # Clean up any excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def write_to_file(data, output_file):
    """Write the collected documentation to a markdown file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Celium Compute Miner Resources\n\n")
        f.write("*This document was auto-generated from the Celium Compute documentation.*\n\n")
        f.write("*Source: https://celiumcompute.ai/docs/category/miner*\n\n")
        f.write("---\n\n")
        
        for item in data:
            f.write(f"## {item['title']}\n\n")
            f.write(clean_html_content(item['content']))
            f.write("\n---\n\n")

def main():
    """Main function to scrape the Celium miner documentation"""
    logger.info("Starting Celium documentation scraper")
    
    # Fetch the main miner docs page
    main_soup = fetch_page(MINER_DOCS_URL)
    if not main_soup:
        logger.error("Failed to fetch main miner documentation page")
        return
    
    # Extract links to individual documentation pages
    doc_links = extract_links_from_page(main_soup, BASE_URL)
    logger.info(f"Found {len(doc_links)} documentation links")
    
    # Also include the main miner page
    doc_links = [MINER_DOCS_URL] + doc_links
    
    # Fetch each documentation page and extract content
    all_content = []
    
    for link in doc_links:
        soup = fetch_page(link)
        if soup:
            content = extract_content(soup)
            all_content.append(content)
            # Be nice to the server
            time.sleep(1)
    
    # Write all content to a markdown file
    write_to_file(all_content, OUTPUT_FILE)
    logger.info(f"Documentation saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main() 