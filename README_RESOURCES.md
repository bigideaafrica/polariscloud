# Bittensor Subnet Building Resources

This repository contains scripts and resources to help you learn about and build Bittensor subnets. The included scraper tool fetches and compiles documentation from both Celium Compute and the official Bittensor documentation to provide a comprehensive resource.

## Quick Start

To generate the Bittensor subnet resources document, simply run:

```bash
cd docs
./get_subnet_resources.sh
```

This will:
1. Install the necessary Python dependencies
2. Run the scraper script to collect documentation
3. Generate a comprehensive markdown document in `docs/bittensor_subnet_resources.md`

## What's Included

The generated resource document contains:

- Celium Miner documentation
- Celium Subnet documentation
- Bittensor Mining FAQ (from official Bittensor docs)
- Bittensor Subnet Creation guide
- Bittensor Subnet Tutorial
- General Bittensor Overview

## Using the Resources

The compiled document serves as a reference for building and understanding Bittensor subnets. Use it to:

1. Learn the basics of Bittensor subnet architecture
2. Understand the roles of miners and validators
3. Follow step-by-step guides for creating subnets
4. Explore best practices from Celium Compute's implementation

## Advanced Usage

The scraper scripts can be customized to focus on specific aspects of subnet development:

- `celium_scraper.py` - Focuses only on Celium's miner documentation
- `bittensor_subnet_resources.py` - The comprehensive scraper that pulls from multiple sources

You can modify these scripts to adjust the scraping behavior, add new documentation sources, or filter the content differently.

## About Bittensor Subnets

Bittensor is an open source platform where participants produce and validate digital commodities like compute power and AI inference. Each subnet is an independent community of miners and validators working together within an incentive mechanism.

Building a subnet involves creating and deploying code that:
1. Defines the work miners must perform
2. Establishes how validators evaluate that work
3. Manages the distribution of rewards based on performance

These resources will help you understand both the technical and economic aspects of building effective Bittensor subnets. 