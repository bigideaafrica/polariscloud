# Bittensor Subnet Documentation Scraper

This directory contains tools to scrape and compile documentation about Bittensor subnets from multiple sources, creating a comprehensive resource document for building and understanding Bittensor subnets.

## Available Scripts

1. `bittensor_subnet_resources.py` - Main script that scrapes both Celium and Bittensor documentation
2. `celium_scraper.py` - Focused scraper for Celium miner documentation only
3. `get_subnet_resources.sh` - Shell script to install dependencies and run the scraper

## How to Use

The easiest way to generate the resource document is to run:

```bash
./get_subnet_resources.sh
```

This will:
1. Install the required Python dependencies
2. Run the comprehensive scraper
3. Save the output to `bittensor_subnet_resources.md`

## Generated Resources

The scraper creates a comprehensive markdown document containing:

- Information from Celium's miner documentation
- Information from Celium's subnet documentation
- Relevant information from Bittensor's documentation
- Organized sections with source links

## Prerequisites

- Python 3.7+
- pip
- Internet connection

## Dependencies

The scraper requires the following Python packages:
- requests
- beautifulsoup4

These will be automatically installed by the `get_subnet_resources.sh` script.

## Note

The scraped content is for educational and reference purposes only. Please respect the terms of service of the websites being scraped. 