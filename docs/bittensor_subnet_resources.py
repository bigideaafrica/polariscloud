#!/usr/bin/env python3
# bittensor_subnet_resources.py
# A script to create comprehensive resources for building a Bittensor subnet
# using both Celium and official Bittensor documentation

import requests
from bs4 import BeautifulSoup
import os
import time
import re
import logging
from urllib.parse import urljoin
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URLs for documentation
CELIUM_BASE_URL = "https://celiumcompute.ai"
CELIUM_MINER_DOCS_URL = f"{CELIUM_BASE_URL}/docs/category/miner"
CELIUM_SUBNET_DOCS_URL = f"{CELIUM_BASE_URL}/docs/category/bittensor-subnet"

BITTENSOR_BASE_URL = "https://docs.bittensor.com"
BITTENSOR_MINING_FAQ_URL = f"{BITTENSOR_BASE_URL}/questions-and-answers"
BITTENSOR_SUBNET_CREATE_URL = f"{BITTENSOR_BASE_URL}/subnets/create-a-subnet"
BITTENSOR_SUBNET_TUTORIAL_URL = f"{BITTENSOR_BASE_URL}/tutorials/ocr-subnet-tutorial"
BITTENSOR_HOMEPAGE_URL = f"{BITTENSOR_BASE_URL}/"

# Output directory and files
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bittensor_subnet_resources.md")
URLS_CACHE_FILE = os.path.join(OUTPUT_DIR, ".scraper_cache.json")

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# URLs to scrape and their descriptions
URLS_TO_SCRAPE = [
    {"url": CELIUM_MINER_DOCS_URL, "source": "Celium", "type": "miner"},
    {"url": CELIUM_SUBNET_DOCS_URL, "source": "Celium", "type": "subnet"},
    {"url": BITTENSOR_MINING_FAQ_URL, "source": "Bittensor", "type": "mining_faq"},
    {"url": BITTENSOR_SUBNET_CREATE_URL, "source": "Bittensor", "type": "subnet_create"},
    {"url": BITTENSOR_SUBNET_TUTORIAL_URL, "source": "Bittensor", "type": "subnet_tutorial"},
    {"url": BITTENSOR_HOMEPAGE_URL, "source": "Bittensor", "type": "homepage"},
]

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

def extract_links_from_page(soup, base_url, url_info):
    """Extract all links from a documentation page based on its source"""
    links = []
    
    # Different selectors based on the documentation source
    if url_info["source"] == "Celium":
        # Celium links are typically in the sidebar or content
        article_links = soup.select('a[href^="/docs/"]')
        
        for link in article_links:
            href = link.get('href')
            if href and '/docs/' in href:
                # Make sure we have the full URL
                full_url = urljoin(base_url, href)
                links.append(full_url)
    
    elif url_info["source"] == "Bittensor":
        # Bittensor links might be structured differently
        article_links = soup.select('a')
        
        for link in article_links:
            href = link.get('href')
            if href:
                # Check if it's a relative link within the docs or an absolute URL to docs.bittensor.com
                if href.startswith('/') or href.startswith(BITTENSOR_BASE_URL):
                    # Make sure we have the full URL
                    full_url = urljoin(base_url, href)
                    if BITTENSOR_BASE_URL in full_url:
                        links.append(full_url)
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(links))

def extract_content(soup, url_info):
    """Extract the main content from a documentation page based on its source"""
    
    # Find the main content area based on the source
    if url_info["source"] == "Celium":
        content_div = soup.select_one('main article')
    elif url_info["source"] == "Bittensor":
        # Try different selectors for Bittensor docs
        content_div = soup.select_one('article') or soup.select_one('main') or soup.select_one('div.md-content')
        
        # If we're on the FAQ page, try to extract only the mining section
        if url_info["type"] == "mining_faq" and content_div:
            mining_section = None
            for section in content_div.select('h2'):
                if "Mining and validation" in section.get_text():
                    mining_section = section
                    break
            
            if mining_section:
                # Get the section and its content until the next h2
                new_content = f"<h2>{mining_section.get_text()}</h2>"
                current = mining_section.next_sibling
                while current and (not current.name or current.name != 'h2'):
                    if hasattr(current, 'name') and current.name:
                        new_content += str(current)
                    current = current.next_sibling
                
                # Create a new soup with just this section
                content_div = BeautifulSoup(new_content, 'html.parser')
    else:
        content_div = None
    
    if not content_div:
        logger.warning(f"Main content area not found for {url_info['url']}")
        return {"title": "Content not found", "content": "", "source": url_info["source"], "url": url_info["url"], "type": url_info["type"]}
    
    # Extract the title
    if url_info["source"] == "Celium":
        title_elem = content_div.select_one('h1')
    elif url_info["source"] == "Bittensor":
        if url_info["type"] == "mining_faq":
            title_elem = content_div.select_one('h2')
        else:
            title_elem = content_div.select_one('h1')
    else:
        title_elem = None
        
    title = title_elem.get_text().strip() if title_elem else "Untitled"
    
    # Extract content text
    # We'll keep the HTML structure for now, then clean it up when writing to file
    content = str(content_div)
    
    return {
        "title": title, 
        "content": content, 
        "source": url_info["source"],
        "url": url_info["url"],
        "type": url_info["type"]
    }

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
            if element.parent and element.parent.name == 'ol':
                text += '1. ' + element.get_text().strip() + '\n'
            else:
                text += '* ' + element.get_text().strip() + '\n'
        elif element.name == 'pre' or element.name == 'code':
            # Format code blocks
            text += '```\n' + element.get_text() + '\n```\n\n'
        elif element.name == 'a' and element.get('href'):
            # Add links
            text += f"[{element.get_text().strip()}]({element.get('href')})"
        elif element.name == 'img' and element.get('src'):
            # Add images
            alt_text = element.get('alt', 'Image')
            text += f"![{alt_text}]({element.get('src')})\n\n"
        elif element.name == 'table':
            # Basic table support - this could be improved
            text += "| Table content (formatting not preserved) |\n|---|\n" 
            for row in element.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if cells:
                    text += "| " + " | ".join([cell.get_text().strip() for cell in cells]) + " |\n"
            text += "\n"
    
    # Clean up any excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def write_to_file(data, output_file):
    """Write the collected documentation to a markdown file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Bittensor Subnet Building Resources\n\n")
        f.write("*This document was auto-generated from Celium Compute and Bittensor documentation.*\n\n")
        f.write("## Table of Contents\n\n")
        
        # Create TOC sections
        sections = {
            "Celium Miner": [],
            "Celium Subnet": [],
            "Bittensor Mining FAQ": [],
            "Bittensor Subnet Creation": [],
            "Bittensor Subnet Tutorial": [],
            "Bittensor Overview": []
        }
        
        # Populate sections
        for item in data:
            if item['source'] == "Celium" and item['type'] == "miner":
                sections["Celium Miner"].append(item)
            elif item['source'] == "Celium" and item['type'] == "subnet":
                sections["Celium Subnet"].append(item)
            elif item['source'] == "Bittensor" and item['type'] == "mining_faq":
                sections["Bittensor Mining FAQ"].append(item)
            elif item['source'] == "Bittensor" and item['type'] == "subnet_create":
                sections["Bittensor Subnet Creation"].append(item)
            elif item['source'] == "Bittensor" and item['type'] == "subnet_tutorial":
                sections["Bittensor Subnet Tutorial"].append(item)
            elif item['source'] == "Bittensor" and item['type'] == "homepage":
                sections["Bittensor Overview"].append(item)
        
        # Write TOC
        for section, items in sections.items():
            if items:
                f.write(f"### {section}\n\n")
                for item in items:
                    sanitized_title = re.sub(r'[^a-zA-Z0-9\s-]', '', item['title']).lower().replace(' ', '-')
                    f.write(f"- [{item['title']}](#{sanitized_title})\n")
                f.write("\n")
        
        f.write("---\n\n")
        
        # Write content
        for section_name, section_items in sections.items():
            if section_items:
                f.write(f"# {section_name}\n\n")
                
                for item in section_items:
                    f.write(f"## {item['title']}\n\n")
                    f.write(f"*Source: [{item['url']}]({item['url']})*\n\n")
                    f.write(clean_html_content(item['content']))
                    f.write("\n---\n\n")

def save_urls_cache(urls):
    """Save the URLs to a cache file"""
    try:
        with open(URLS_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(urls, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving URL cache: {e}")

def load_urls_cache():
    """Load URLs from cache file if it exists"""
    try:
        if os.path.exists(URLS_CACHE_FILE):
            with open(URLS_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading URL cache: {e}")
    
    return []

def main():
    """Main function to scrape documentation and create a subnet building resource"""
    logger.info("Starting Bittensor subnet resource builder")
    
    # Clear the cache to fetch fresh content with the corrected URLs
    if os.path.exists(URLS_CACHE_FILE):
        os.remove(URLS_CACHE_FILE)
        logger.info("Removed old URL cache to fetch fresh content")
    
    all_urls = []
    scraped_urls = set()
    all_content = []
    
    # Process initial URLs
    for url_info in URLS_TO_SCRAPE:
        if url_info["url"] not in scraped_urls:
            soup = fetch_page(url_info["url"])
            if soup:
                # Extract content from the main page
                content = extract_content(soup, url_info)
                all_content.append(content)
                scraped_urls.add(url_info["url"])
                
                # Find additional links
                base_url = CELIUM_BASE_URL if url_info["source"] == "Celium" else BITTENSOR_BASE_URL
                links = extract_links_from_page(soup, base_url, url_info)
                
                # Add new links to process with the same type and source
                for link in links:
                    if link not in scraped_urls:
                        link_type = url_info["type"]
                        all_urls.append({
                            "url": link,
                            "source": url_info["source"],
                            "type": link_type
                        })
            
            # Be nice to the server
            time.sleep(1)
    
    # Process additional discovered URLs - limit to a reasonable number
    max_additional_pages = 10
    for i, url_info in enumerate(all_urls):
        if i >= max_additional_pages:
            logger.info(f"Reached limit of {max_additional_pages} additional pages, stopping.")
            break
            
        if url_info["url"] not in scraped_urls:
            soup = fetch_page(url_info["url"])
            if soup:
                content = extract_content(soup, url_info)
                all_content.append(content)
                scraped_urls.add(url_info["url"])
                
            # Be nice to the server
            time.sleep(1)
    
    # Save the URLs we've scraped
    save_urls_cache(list(scraped_urls))
    
    # Write all content to a markdown file
    write_to_file(all_content, OUTPUT_FILE)
    logger.info(f"Resource document saved to {OUTPUT_FILE}")
    logger.info(f"Scraped {len(all_content)} pages in total")

if __name__ == "__main__":
    main() 