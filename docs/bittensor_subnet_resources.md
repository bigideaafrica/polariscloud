# Bittensor Subnet Building Resources

*This document was auto-generated from Celium Compute and Bittensor documentation.*

## Table of Contents

### Celium Miner

- [Untitled](#untitled)
- [Overview](#overview)
- [Overview](#overview)
- [Overview](#overview)
- [Best Practices for Assigning Validator Hotkeys](#best-practices-for-assigning-validator-hotkeys)
- [Validator](#validator)
- [Executor](#executor)
- [Untitled](#untitled)

### Celium Subnet

- [Untitled](#untitled)

### Bittensor Mining FAQ

- [Mining and validation​](#mining-and-validation)

### Bittensor Subnet Creation

- [Create a Subnet](#create-a-subnet)

### Bittensor Subnet Tutorial

- [OCR Subnet Tutorial](#ocr-subnet-tutorial)

### Bittensor Overview

- [Bittensor Documentation](#bittensor-documentation)

---

# Celium Miner

## Untitled

*Source: [https://celiumcompute.ai/docs/category/miner](https://celiumcompute.ai/docs/category/miner)*

[📄️ OverviewThis miner allows you to contribute your GPU resources to the Compute Subnet and earn compensation for providing computational power. You will run a central miner on a CPU server, which manages multiple executors running on GPU-equipped machines.](/docs/bittensor-subnet/miner/overview)## 📄️ Overview

This miner allows you to contribute your GPU resources to the Compute Subnet and earn compensation for providing computational power. You will run a central miner on a CPU server, which manages multiple executors running on GPU-equipped machines.

[📄️ Best Practices for Assigning Validator HotkeysIn the Compute Subnet, validators play a critical role in ensuring the performance and security of the network. However, miners must assign executors carefully to the validators to maximize incentives. This guide explains the best strategy for assigning validator hotkeys based on stake distribution within the network.](/docs/bittensor-subnet/miner/assigning_validator_hotkeys)## 📄️ Best Practices for Assigning Validator Hotkeys

In the Compute Subnet, validators play a critical role in ensuring the performance and security of the network. However, miners must assign executors carefully to the validators to maximize incentives. This guide explains the best strategy for assigning validator hotkeys based on stake distribution within the network.


---

## Overview

*Source: [https://celiumcompute.ai/docs/intro](https://celiumcompute.ai/docs/intro)*

* 
[](/)* Overview
# Overview

Celium is an innovative GPU rental platform built on the Bittensor subnet infrastructure. Our platform enables seamless access to GPU computing resources through a decentralized network, providing reliable and efficient solutions for computational needs.

## Key Features​

[​](#key-features)### Decentralized Infrastructure​

[​](#decentralized-infrastructure)* Built on Bittensor subnet technology
* Trustless and transparent operations
* Distributed network of GPU providers
### User-Friendly Platform​

[​](#user-friendly-platform)* Intuitive web interface
* Streamlined rental process
* Flexible payment options with automatic top-up capabilities
### Resource Management​

[​](#resource-management)* Real-time GPU availability tracking
* Performance monitoring and optimization
## How It Works​

[​](#how-it-works)### For Renters​

[​](#for-renters)1. Create an account on the Celium platform
[Celium platform](https://celiumcompute.ai/register)1. Set up your payment method and optional auto top-up
1. Browse available GPU resources
1. Select and rent the computational power you need
1. Monitor your usage through the dashboard
### For GPU Providers​

[​](#for-gpu-providers)1. Join our Bittensor Subnet as a miner
[Join](https://github.com/Datura-ai/compute-subnet/tree/main/neurons/miners)1. Register your GPU resources
1. Earn rewards for providing computational power
## Contact​

[​](#contact)For support or inquiries:

* Website: Celium Platform
[Celium Platform](https://celiumcompute.ai/)* Email: Support Email
[Support Email](mailto:support@celiumcompute.ai)* Discord: Celium Subnet
[Celium Subnet](https://discord.com/channels/799672011265015819/1291754566957928469)Note: This documentation is regularly updated to reflect the latest features and improvements to the Celium platform.


---

## Overview

*Source: [https://celiumcompute.ai/docs/bittensor-subnet/overview](https://celiumcompute.ai/docs/bittensor-subnet/overview)*

* 
[](/)* Bittensor Subnet
[Bittensor Subnet](/docs/category/bittensor-subnet)* Overview
# Overview

## Celium Subnet​

[​](#celium-subnet)Welcome to the Celium Subnet! This project enables a decentralized, peer-to-peer GPU rental marketplace, connecting miners who contribute GPU resources with users who need computational power. Our frontend interface is available at celiumcompute.ai, where you can easily rent machines from the subnet.

[celiumcompute.ai](https://celiumcompute.ai)## Table of Contents​

[​](#table-of-contents)* Introduction
[Introduction](#introduction)* High-Level Architecture
[High-Level Architecture](#high-level-architecture)* Getting Started

For Renters
For Miners
For Validators
[Getting Started](#getting-started)* For Renters
[For Renters](#for-renters)* For Miners
[For Miners](#for-miners)* For Validators
[For Validators](#for-validators)* Contact and Support
[Contact and Support](#contact-and-support)## Introduction​

[​](#introduction)The Compute Subnet on Bittensor is a decentralized network that allows miners to contribute their GPU resources to a global pool. Users can rent these resources for computational tasks, such as machine learning, data analysis, and more. The system ensures fair compensation for miners based on the quality and performance of their GPUs.

## High-Level Architecture​

[​](#high-level-architecture)* Miners: Provide GPU resources to the network, evaluated and scored by validators.
* Validators: Securely connect to miner machines to verify hardware specs and performance. They maintain the network's integrity.
* Renters: Rent computational resources from the network to run their tasks.
* Frontend (celiumcompute.ai): The web interface facilitating easy interaction between miners and renters.
* Bittensor Network: The decentralized blockchain in which the compensation is managed and paid out by the validators to the miners through its native token, $TAO.
## Getting Started​

[​](#getting-started)### For Renters​

[​](#for-renters)If you are looking to rent computational resources, you can easily do so through the Compute Subnet. Renters can:

1. Visit celiumcompute.ai and sign up.
[celiumcompute.ai](https://celiumcompute.ai)1. Browse available GPU resources.
1. Select machines based on GPU type, performance, and price.
1. Deploy and monitor your computational tasks using the platform's tools.
To start renting machines, visit celiumcompute.ai and access the resources you need.

[celiumcompute.ai](https://celiumcompute.ai)### For Miners​

[​](#for-miners)Miners can contribute their GPU-equipped machines to the network. The machines are scored and validated based on factors like GPU type, number of GPUs, bandwidth, and overall GPU performance. Higher performance results in better compensation for miners.

If you are a miner and want to contribute GPU resources to the subnet, please refer to the Miner Setup Guide for instructions on how to:

[Miner Setup Guide](/docs/bittensor-subnet/miner/overview)* Set up your environment.
* Install the miner software.
* Register your miner and connect to the network.
* Get compensated for providing GPUs!
### For Validators​

[​](#for-validators)Validators play a crucial role in maintaining the integrity of the Compute Subnet by verifying the hardware specifications and performance of miners’ machines. Validators ensure that miners are fairly compensated based on their GPU contributions and prevent fraudulent activities.

For more details, visit the Validator Setup Guide.

[Validator Setup Guide](/docs/bittensor-subnet/validator)## Contact and Support​

[​](#contact-and-support)If you need assistance or have any questions, feel free to reach out:

* Discord Support: Dedicated Channel within the Bittensor Discord
[Dedicated Channel within the Bittensor Discord](https://discord.com/channels/799672011265015819/1291754566957928469)
---

## Overview

*Source: [https://celiumcompute.ai/docs/bittensor-subnet/miner/overview](https://celiumcompute.ai/docs/bittensor-subnet/miner/overview)*

* 
[](/)* Bittensor Subnet
[Bittensor Subnet](/docs/category/bittensor-subnet)* Miner
[Miner](/docs/category/miner)* Overview
# Overview

This miner allows you to contribute your GPU resources to the Compute Subnet and earn compensation for providing computational power. You will run a central miner on a CPU server, which manages multiple executors running on GPU-equipped machines.

### Central Miner Server Requirements​

[​](#central-miner-server-requirements)To run the central miner, you only need a CPU server with the following specifications:

* CPU: 4 cores
* RAM: 8GB
* Storage: 50GB available disk space
* OS: Ubuntu (recommended)
### Executors​

[​](#executors)Executors are GPU-equipped machines that perform the computational tasks. The central miner manages these executors, which can be easily added or removed from the network.

To see the compatible GPUs to mine with and their relative rewards, see this dict here.

[here](https://github.com/Datura-ai/compute-subnet/blob/main/neurons/validators/src/services/const.py#L3)## Installation​

[​](#installation)### Using Docker​

[​](#using-docker)#### Step 1: Clone the Git Repository​

[​](#step-1-clone-the-git-repository)```
git clone https://github.com/Datura-ai/compute-subnet.git
```

```
git clone https://github.com/Datura-ai/compute-subnet.git
```

#### Step 2: Install Required Tools​

[​](#step-2-install-required-tools)```
cd compute-subnet && chmod +x scripts/install_miner_on_ubuntu.sh && ./scripts/install_miner_on_ubuntu.sh
```

```
cd compute-subnet && chmod +x scripts/install_miner_on_ubuntu.sh && ./scripts/install_miner_on_ubuntu.sh
```

Verify if bittensor and docker installed:

```
btcli --version
```

```
btcli --version
```

```
docker --version
```

```
docker --version
```

If one of them isn't installed properly, install using following link:
For bittensor, use This Link
For docker, use This Link

[This Link](https://github.com/opentensor/bittensor/blob/master/README.md#install-bittensor-sdk)[This Link](https://docs.docker.com/engine/install/)#### Step 3: Setup ENV​

[​](#step-3-setup-env)```
cp neurons/miners/.env.template neurons/miners/.env
```

```
cp neurons/miners/.env.template neurons/miners/.env
```

Fill in your information for:

BITTENSOR_WALLET_NAME: Your wallet name for Bittensor. You can check this with btcli wallet list

```
BITTENSOR_WALLET_NAME
```

```
btcli wallet list
```

BITTENSOR_WALLET_HOTKEY_NAME: The hotkey name of your wallet's registered hotkey. If it is not registered, run btcli subnet register --netuid 51.

```
BITTENSOR_WALLET_HOTKEY_NAME
```

```
btcli subnet register --netuid 51
```

EXTERNAL_IP_ADDRESS: The external IP address of your central miner server. Make sure it is open to external connections on the EXTERNAL PORT

```
EXTERNAL_IP_ADDRESS
```

```
EXTERNAL PORT
```

HOST_WALLET_DIR: The directory path of your wallet on the machine.

```
HOST_WALLET_DIR
```

INTERNAL_PORT and EXTERNAL_PORT: Optionally customize these ports. Make sure the EXTERNAL PORT is open for external connections to connect to the validators.

```
INTERNAL_PORT
```

```
EXTERNAL_PORT
```

```
EXTERNAL PORT
```

#### Step 4: Start the Miner​

[​](#step-4-start-the-miner)```
cd neurons/miners && docker compose up -d
```

```
cd neurons/miners && docker compose up -d
```

## Managing Executors​

[​](#managing-executors)### Adding an Executor​

[​](#adding-an-executor)Executors are machines running on GPUs that you can add to your central miner. The more executors (GPUs) you have, the greater your compensation will be. Here's how to add them:

1. Ensure the executor machine is set up and running Docker. For more information, follow the executor README.md here
Ensure the executor machine is set up and running Docker. For more information, follow the executor README.md here

[executor README.md here](/docs/bittensor-subnet/executor)1. Use the following command to add an executor to the central miner:
docker exec <container-id or name> python /root/app/src/cli.py add-executor --address <executor-ip-address> --port <executor-port> --validator <validator-hotkey>

<executor-ip-address>: The IP address of the executor machine.
<executor-port>: The port number used for the executor (default: 8001).
<validator-hotkey>: The validator hotkey that you want to give access to this executor. Which validator hotkey should you pick? Follow this guide
Use the following command to add an executor to the central miner:

```
docker exec <container-id or name> python /root/app/src/cli.py add-executor --address <executor-ip-address> --port <executor-port> --validator <validator-hotkey>
```

```
docker exec <container-id or name> python /root/app/src/cli.py add-executor --address <executor-ip-address> --port <executor-port> --validator <validator-hotkey>
```

* <executor-ip-address>: The IP address of the executor machine.
```
<executor-ip-address>
```

* <executor-port>: The port number used for the executor (default: 8001).
```
<executor-port>
```

```
8001
```

* <validator-hotkey>: The validator hotkey that you want to give access to this executor. Which validator hotkey should you pick? Follow this guide
```
<validator-hotkey>
```

[this guide](/docs/bittensor-subnet/miner/assigning_validator_hotkeys)### What is a Validator Hotkey?​

[​](#what-is-a-validator-hotkey)The validator hotkey is a unique identifier tied to a validator that authenticates and verifies the performance of your executor machines. When you specify a validator hotkey during executor registration, it ensures that your executor is validated by this specific validator.

To switch to a different validator first follow the instructions for removing an executor. After removing the executor, you need to re-register executors by running the add-executor command again (Step 2 of Adding an Executor).

### Removing an Executor​

[​](#removing-an-executor)To remove an executor from the central miner, follow these steps:

1. Run the following command to remove the executor:
docker exec <docker instance> python /root/app/src/cli.py remove-executor --address <executor public ip> --port <executor external port>
Run the following command to remove the executor:

```
docker exec <docker instance> python /root/app/src/cli.py remove-executor --address <executor public ip> --port <executor external port>
```

```
docker exec <docker instance> python /root/app/src/cli.py remove-executor --address <executor public ip> --port <executor external port>
```

### Monitoring earnings​

[​](#monitoring-earnings)To monitor your earnings, use Taomarketcap.com's subnet 51 miner page to track your daily rewards, and relative performance with other miners.

[Taomarketcap.com](https://taomarketcap.com/subnets/51/miners)
---

## Best Practices for Assigning Validator Hotkeys

*Source: [https://celiumcompute.ai/docs/bittensor-subnet/miner/assigning_validator_hotkeys](https://celiumcompute.ai/docs/bittensor-subnet/miner/assigning_validator_hotkeys)*

* 
[](/)* Bittensor Subnet
[Bittensor Subnet](/docs/category/bittensor-subnet)* Miner
[Miner](/docs/category/miner)* Best Practices for Assigning Validator Hotkeys
# Best Practices for Assigning Validator Hotkeys

In the Compute Subnet, validators play a critical role in ensuring the performance and security of the network. However, miners must assign executors carefully to the validators to maximize incentives. This guide explains the best strategy for assigning validator hotkeys based on stake distribution within the network.

## Why Validator Hotkey Assignment Matters​

[​](#why-validator-hotkey-assignment-matters)You will not receive any rewards if your executors are not assigned to validators that control a majority of the stake in the network. Therefore, it’s crucial to understand how stake distribution works and how to assign your executors effectively.

## Step-by-Step Strategy for Assigning Validator Hotkeys​

[​](#step-by-step-strategy-for-assigning-validator-hotkeys)### 1. Check the Validator Stakes​

[​](#1-check-the-validator-stakes)The first step is to determine how much stake each validator controls in the network. You can find the current stake distribution of all validators by visiting:

TaoMarketCap Subnet 51 Validators

[TaoMarketCap Subnet 51 Validators](https://taomarketcap.com/subnets/51/validators)This page lists each validator and their respective stake, which is essential for making decisions about hotkey assignments.

### 2. Assign Executors to Cover at Least 50% of the Stake​

[​](#2-assign-executors-to-cover-at-least-50-of-the-stake)To begin, you need to ensure that your executors are covering at least 50% of the total network stake. This guarantees that your executors will be actively validated and you’ll receive rewards.

#### Example:​

[​](#example)Suppose you have 100 executors (GPUs) and the stake distribution of the validators is as follows:

| Table content (formatting not preserved) |
|---|
| Validator | Stake (%) |
| Validator 1 | 50% |
| Validator 2 | 25% |
| Validator 3 | 15% |
| Validator 4 | 5% |
| Validator 5 | 1% |

* To cover 50% of the total stake, assign enough executors to cover Validator 1 (50% stake).
* In this case, assign at least one executor to Validator 1 because they control 50% of the network stake.
### 3. Stake-Weighted Assignment for Remaining Executors​

[​](#3-stake-weighted-assignment-for-remaining-executors)Once you’ve ensured that you’re covering at least 50% of the network stake, the remaining executors should be assigned in a stake-weighted fashion to maximize rewards.

#### Continuing the Example:​

[​](#continuing-the-example)You have 99 remaining executors to assign to validators. Here's the distribution of executors you should follow based on the stake:

* Validator 1 (50% stake): Assign 50% of executors to Validator 1.

Assign 50 executors.
* Assign 50 executors.
* Validator 2 (25% stake): Assign 25% of executors to Validator 2.

Assign 25 executors.
* Assign 25 executors.
* Validator 3 (15% stake): Assign 15% of executors to Validator 3.

Assign 15 executors.
* Assign 15 executors.
* Validator 4 (5% stake): Assign 5% of executors to Validator 4.

Assign 5 executors.
* Assign 5 executors.
* Validator 5 (1% stake): Assign 1% of executors to Validator 5.

Assign 1 executor.
* Assign 1 executor.
### 4. Adjust Based on Network Dynamics​

[​](#4-adjust-based-on-network-dynamics)The stake of validators can change over time. Make sure to periodically check the validator stakes on TaoMarketCap and reassign your executors as needed to maintain optimal rewards. If a validator’s stake increases significantly, you may want to adjust your assignments accordingly.

[TaoMarketCap](https://taomarketcap.com/subnets/51/validators)## Summary of the Best Strategy​

[​](#summary-of-the-best-strategy)* Step 1: Check the validator stakes on TaoMarketCap.
[TaoMarketCap](https://taomarketcap.com/subnets/51/validators)* Step 2: Ensure your executors are covering at least 50% of the total network stake.
* Step 3: Use a stake-weighted strategy to assign your remaining executors, matching the proportion of the stake each validator controls.
* Step 4: Periodically recheck the stake distribution and adjust assignments as needed.
By following this strategy, you’ll ensure that your executors are assigned to validators in the most efficient way possible, maximizing your chances of receiving rewards.

## Additional Resources​

[​](#additional-resources)* TaoMarketCap Subnet 51 Validators
[TaoMarketCap Subnet 51 Validators](https://taomarketcap.com/subnets/51/validators)
---

## Validator

*Source: [https://celiumcompute.ai/docs/bittensor-subnet/validator](https://celiumcompute.ai/docs/bittensor-subnet/validator)*

* 
[](/)* Bittensor Subnet
[Bittensor Subnet](/docs/category/bittensor-subnet)* Validator
# Validator

## System Requirements​

[​](#system-requirements)For validation, a validator machine will need:

* CPU: 4 cores
* RAM: 8 GB
Ensure that your machine meets these requirements before proceeding with the setup.

First, register and regen your bittensor wallet and validator hotkey onto the machine.

For installation of btcli, check this guide

[this guide](https://github.com/opentensor/bittensor/blob/master/README.md#install-bittensor-sdk)```
btcli s register --netuid 51
```

```
btcli s register --netuid 51
```

```
btcli w regen_coldkeypub
```

```
btcli w regen_coldkeypub
```

```
btcli w regen_hotkey
```

```
btcli w regen_hotkey
```

## Installation​

[​](#installation)### Using Docker​

[​](#using-docker)#### Step 1: Clone Git repo​

[​](#step-1-clone-git-repo)```
git clone https://github.com/Datura-ai/compute-subnet.git
```

```
git clone https://github.com/Datura-ai/compute-subnet.git
```

#### Step 2: Install Required Tools​

[​](#step-2-install-required-tools)```
cd compute-subnet && chmod +x scripts/install_validator_on_ubuntu.sh && ./scripts/install_validator_on_ubuntu.sh
```

```
cd compute-subnet && chmod +x scripts/install_validator_on_ubuntu.sh && ./scripts/install_validator_on_ubuntu.sh
```

Verify docker installation

```
docker --version
```

```
docker --version
```

If did not correctly install, follow this link

[this link](https://docs.docker.com/engine/install/)#### Step 3: Setup ENV​

[​](#step-3-setup-env)```
cp neurons/validators/.env.template neurons/validators/.env
```

```
cp neurons/validators/.env.template neurons/validators/.env
```

Replace with your information for BITTENSOR_WALLET_NAME, BITTENSOR_WALLET_HOTKEY_NAME, HOST_WALLET_DIR.
If you want you can use different port for INTERNAL_PORT, EXTERNAL_PORT.

```
BITTENSOR_WALLET_NAME
```

```
BITTENSOR_WALLET_HOTKEY_NAME
```

```
HOST_WALLET_DIR
```

```
INTERNAL_PORT
```

```
EXTERNAL_PORT
```

#### Step 4: Docker Compose Up​

[​](#step-4-docker-compose-up)```
cd neurons/validators && docker compose up -d
```

```
cd neurons/validators && docker compose up -d
```


---

## Executor

*Source: [https://celiumcompute.ai/docs/bittensor-subnet/executor](https://celiumcompute.ai/docs/bittensor-subnet/executor)*

* 
[](/)* Bittensor Subnet
[Bittensor Subnet](/docs/category/bittensor-subnet)* Executor
# Executor

## Setup project​

[​](#setup-project)### Requirements​

[​](#requirements)* Ubuntu machine
* install docker
[docker](https://docs.docker.com/engine/install/ubuntu/)### Step 1: Clone project​

[​](#step-1-clone-project)```
git clone https://github.com/Datura-ai/compute-subnet.git
```

```
git clone https://github.com/Datura-ai/compute-subnet.git
```

### Step 2: Install Required Tools​

[​](#step-2-install-required-tools)Run following command to install required tools:

```
cd compute-subnet && chmod +x scripts/install_executor_on_ubuntu.sh && scripts/install_executor_on_ubuntu.sh
```

```
cd compute-subnet && chmod +x scripts/install_executor_on_ubuntu.sh && scripts/install_executor_on_ubuntu.sh
```

if you don't have sudo on your machine, run

```
sed -i 's/sudo //g' scripts/install_executor_on_ubuntu.sh
```

```
sed -i 's/sudo //g' scripts/install_executor_on_ubuntu.sh
```

to remove sudo from the setup script commands

### Step 3: Configure Docker for Nvidia​

[​](#step-3-configure-docker-for-nvidia)Please follow this to setup docker for nvidia properly

[this](https://stackoverflow.com/questions/72932940/failed-to-initialize-nvml-unknown-error-in-docker-after-few-hours)### Step 4: Install and Run​

[​](#step-4-install-and-run)* Go to executor root
```
cd neurons/executor
```

```
cd neurons/executor
```

* Add .env in the project
```
cp .env.template .env
```

```
cp .env.template .env
```

Add the correct miner wallet hotkey for MINER_HOTKEY_SS58_ADDRESS.
You can change the ports for INTERNAL_PORT, EXTERNAL_PORT, SSH_PORT based on your need.

```
MINER_HOTKEY_SS58_ADDRESS
```

```
INTERNAL_PORT
```

```
EXTERNAL_PORT
```

```
SSH_PORT
```

* INTERNAL_PORT: internal port of your executor docker container
* EXTERNAL_PORT: external expose port of your executor docker container
* SSH_PORT: ssh port map into 22 of your executor docker container
* SSH_PUBLIC_PORT: [Optional] ssh public access port of your executor docker container. If SSH_PUBLIC_PORT is equal to SSH_PORT then you don't have to specify this port.
```
SSH_PUBLIC_PORT
```

```
SSH_PORT
```

* MINER_HOTKEY_SS58_ADDRESS: the miner hotkey address
* RENTING_PORT_RANGE: The port range that are publicly accessible. This can be empty if all ports are open. Available formats are:

Range Specification(from-to): Miners can specify a range of ports, such as 2000-2005. This means ports from 2000 to 2005 will be open for the validator to select.
Specific Ports(port1,port2,port3): Miners can specify individual ports, such as 2000,2001,2002. This means only ports 2000, 2001, and 2002 will be available for the validator.
Default Behavior: If no ports are specified, the validator will assume that all ports on the executor are available.
* Range Specification(from-to): Miners can specify a range of ports, such as 2000-2005. This means ports from 2000 to 2005 will be open for the validator to select.
```
from-to
```

* Specific Ports(port1,port2,port3): Miners can specify individual ports, such as 2000,2001,2002. This means only ports 2000, 2001, and 2002 will be available for the validator.
```
port1,port2,port3
```

* Default Behavior: If no ports are specified, the validator will assume that all ports on the executor are available.
* RENTING_PORT_MAPPINGS: Internal, external port mappings. Use this env when you are using proxy in front of your executors and the internal port and external port can't be the same. You can ignore this env, if all ports are open or the internal and external ports are the same. example:

if internal port 46681 is mapped to 56681 external port and internal port 46682 is mapped to 56682 external port, then RENTING_PORT_MAPPINGS="[[46681, 56681], [46682, 56682]]"
* if internal port 46681 is mapped to 56681 external port and internal port 46682 is mapped to 56682 external port, then RENTING_PORT_MAPPINGS="[[46681, 56681], [46682, 56682]]"
Note: Please use either RENTING_PORT_RANGE or RENTING_PORT_MAPPINGS and DO NOT use both of them if you have specific ports are available.

* Run project
```
docker compose up -d
```

```
docker compose up -d
```


---

## Untitled

*Source: [https://celiumcompute.ai/docs/category/pods](https://celiumcompute.ai/docs/category/pods)*

[📄️ OverviewPods in Celium represent individual GPU rental units that users can lease for their computational needs. Each pod is a containerized environment that provides secure, isolated access to GPU resources through the Bittensor subnet infrastructure.](/docs/pods/overview)## 📄️ Overview

Pods in Celium represent individual GPU rental units that users can lease for their computational needs. Each pod is a containerized environment that provides secure, isolated access to GPU resources through the Bittensor subnet infrastructure.

[📄️ TemplatesOverview](/docs/pods/templates)## 📄️ Templates

Overview


---

# Celium Subnet

## Untitled

*Source: [https://celiumcompute.ai/docs/category/bittensor-subnet](https://celiumcompute.ai/docs/category/bittensor-subnet)*

[📄️ OverviewCelium Subnet](/docs/bittensor-subnet/overview)## 📄️ Overview

Celium Subnet

[🗃️ Miner2 items](/docs/category/miner)## 🗃️ Miner

2 items

[📄️ ValidatorSystem Requirements](/docs/bittensor-subnet/validator)## 📄️ Validator

System Requirements

[📄️ ExecutorSetup project](/docs/bittensor-subnet/executor)## 📄️ Executor

Setup project


---

# Bittensor Mining FAQ

## Mining and validation​

*Source: [https://docs.bittensor.com/questions-and-answers](https://docs.bittensor.com/questions-and-answers)*

## Mining and validation​

### Is mining and validation in Bittensor the same as in Bitcoin?​

[​](/questions-and-answers#is-mining-and-validation-in-bittensor-the-same-as-in-bitcoin)No, there are some key differences! Bitcoin miners work to validate blocks according to Proof of Work consensus so they can be added to the blockchain.

In Bittensor, "mining", within subnets, has nothing to do with adding blocks to the chain. Instead, it has to do with production of digital commodities. Similarly, "validation", within subnets, has nothing to do with validating blocks—it concerns validating the work performed by miners.

### So is there a separate blockchain validation on Bittensor?​

[​](/questions-and-answers#so-is-there-a-separate-blockchain-validation-on-bittensor)Yes indeed. In Bittensor, the work of validating the blockchain is performed by the Opentensor Foundation on a Proof-of-Authority model.

### What is the incentive to be a miner or a validator, or create a subnet?​

[​](/questions-and-answers#what-is-the-incentive-to-be-a-miner-or-a-validator-or-create-a-subnet)Bittensor incentivizes participation through emission of TAO. Each day, 7200 TAO are emitted into the network (one TAO every 12 seconds).

The emission of TAO within each subnet is as follows:

* 18% to the subnet creator.
* 41% to validators
* 41% to the miners
See Emissions.

[Emissions](/emissions)### I don't want to create a subnet, can I just be a miner or a validator?​

[​](/questions-and-answers#i-dont-want-to-create-a-subnet-can-i-just-be-a-miner-or-a-validator)Yes! Most participants will not create their own subnets, there are lots to choose from.

See:

* Validating in Bittensor
[Validating in Bittensor](/validators/)* Mining in Bittensor.
[Mining in Bittensor](/miners/)### Is there a central place where I can see compute requirements for mining and validating for all subnets?​

[​](/questions-and-answers#is-there-a-central-place-where-i-can-see-compute-requirements-for-mining-and-validating-for-all-subnets)Unfortunately no. Subnets are not run or managed by Opentensor Foundation, and the landscape of subnets is constantly evolving.

Browse the subnets at taostats.io/subnets, or on Discord.

[taostats.io/subnets](https://taostats.io/subnets)```
taostats.io/subnets
```

[Discord](https://discord.com/channels/799672011265015819/830068283314929684)### Can I be a subnet miner or a subnet validator forever?​

[​](/questions-and-answers#can-i-be-a-subnet-miner-or-a-subnet-validator-forever)You can keep trying forever, but your success depends on your performance. Mining and validating in a subnet is competitive. If a miner or validator is one of the three lowest in the subnet, it may be de-registered at the end of the tempo, and have to register again.

See miner deregistration.

[miner deregistration](/miners/#miner-deregistration)
---

# Bittensor Subnet Creation

## Create a Subnet

*Source: [https://docs.bittensor.com/subnets/create-a-subnet](https://docs.bittensor.com/subnets/create-a-subnet)*

* 
[](/)* Managing subnets
* Create a Subnet
[SUBMIT A PR](https://github.com/opentensor/developer-docs/blob/main/docs/subnets/create-a-subnet.md)[SUBMIT AN ISSUE](https://github.com/opentensor/developer-docs/issues)# Create a Subnet

This page describes the procedures for creating a Bittensor subnet. Read Understanding Subnets first to ensure you understand the concepts involved.

[Understanding Subnets](/subnets/understanding-subnets)You do not have to create a subnet to mine or validate on the Bittensor network.

## Recommended flow for deploying your subnet​

[​](/subnets/create-a-subnet#recommended-flow-for-deploying-your-subnet)Before you deploy your first subnet on the mainchain, we strongly recommend that you follow the below order:

1. Local first: Create a subnet on your local, and develop and test your incentive mechanism on the local subnet.
1. Testchain next: After you are satisfied with it, create a subnet on the Bittensor testchain, and test and debug your incentive mechanism on this testchain subnet.
1. Mainchain last: After completing the above steps, create a subnet on the Bittensor mainchain.
Subnet creations are limited to one subnet creation per 7200 blocks (approximately one per day).

## Prerequisites​

[​](/subnets/create-a-subnet#prerequisites)To create a subnet, whether locally, on testchain, or on mainchain, make sure that:

* You installed Bittensor.
[installed Bittensor](/getting-started/installation)* You have already created a wallet or know how to create one.
[created a wallet or know how to create one](/getting-started/wallets#creating-a-local-wallet)In Bittensor, when we say "registering your keys in a subnet", it means purchasing a UID slot in the subnet, and you will then either validate or mine on this UID. This step is also referred to as purchasing a slot. On the other hand, "creating a subnet" will create a subnet and give you its netuid.

```
netuid
```

## Creating a local subnet​

[​](/subnets/create-a-subnet#creating-a-local-subnet)You must also run a local Bittensor blockchain to create and run a local subnet. Running a local blockchain is sometimes synonymously referred to as running on staging. Running a local blockchain spins up two authority nodes locally, not connected to any other Bittensor blockchain nodes either on testchain or mainchain.

Running a local blockchain is different from running a public subtensor node. While a local blockchain node is not connected to any other Bittensor nodes, a public subtensor node will connect to the Bittensor network, testchain, or mainchain as per how you run the subtensor node and sync with the network, giving you your own access point to the Bittensor network. To create a local subnet, do not run a public subtensor; instead, only run a local blockchain.

### Step 1. Install and run a local blockchain node​

[​](/subnets/create-a-subnet#step-1-install-and-run-a-local-blockchain-node)Follow the Bittensor Subnet Template document and run the below specified steps:

[Bittensor Subnet Template document](https://github.com/opentensor/bittensor-subnet-template/blob/main/docs/running_on_staging.md)* From and including Step 1 Installing substrate dependencies.
[Step 1 Installing substrate dependencies](https://github.com/opentensor/bittensor-subnet-template/blob/main/docs/running_on_staging.md#1-install-substrate-dependencies)* To and including Step 5 Initialize.
[Step 5 Initialize](https://github.com/opentensor/bittensor-subnet-template/blob/main/docs/running_on_staging.md#5-initialize)The above steps will install and run a local blockchain node. Furthermore, when built with the --features pow-faucet flag, as instructed in the above Step 5. Initialize, the local blockchain node will provide the faucet feature, which you can use to mint test tokens.

```
--features pow-faucet
```

### Step 2. Create wallet​

[​](/subnets/create-a-subnet#step-2-create-wallet)If you have not already done so, create Bittensor wallet(s) using the steps described in the Create Wallet guide.

[Create Wallet](/getting-started/wallets)### Step 3. Mint tokens from the faucet​

[​](/subnets/create-a-subnet#step-3-mint-tokens-from-the-faucet)You will need tokens to register the subnet (which you will create below) on your local blockchain.  Run the following command to mint faucet tokens (fake TAO).

```
btcli wallet faucet --wallet.name <owner-wallet-name> --subtensor.chain_endpoint ws://127.0.0.1:9946 
```

```
btcli wallet faucet --wallet.name <owner-wallet-name> --subtensor.chain_endpoint ws://127.0.0.1:9946 
```

Output:

```
>> Balance: τ0.000000000 ➡ τ100.000000000
```

```
>> Balance: τ0.000000000 ➡ τ100.000000000
```

### Step 4. Create the subnet​

[​](/subnets/create-a-subnet#step-4-create-the-subnet)Run the below command to create a new subnet on your local chain. The cost will be exactly τ100.000000000 for the first subnet you create.

```
btcli subnet create --wallet.name owner --subtensor.chain_endpoint ws://127.0.0.1:9946 
```

```
btcli subnet create --wallet.name owner --subtensor.chain_endpoint ws://127.0.0.1:9946 
```

Output:

```
>> Your balance is: τ200.000000000>> Do you want to register a subnet for τ100.000000000? [y/n]: >> Enter password to unlock key: [YOUR_PASSWORD]>> ✅ Registered subnetwork with netuid: 1
```

```
>> Your balance is: τ200.000000000>> Do you want to register a subnet for τ100.000000000? [y/n]: >> Enter password to unlock key: [YOUR_PASSWORD]>> ✅ Registered subnetwork with netuid: 1
```

The local chain will now have registered a default netuid of 1. A second registration will create netuid 2, and so on, until you reach the subnet limit of 8. If you create the 9th subnet, the subnet with the least staked TAO will be replaced with the newly created subnet, thereby maintaining the total subnet count to 8.

```
netuid
```

```
netuid
```

## Creating a subnet on testchain​

[​](/subnets/create-a-subnet#creating-a-subnet-on-testchain)You do not need to run a local blockchain node to create a testchain subnet. Instead, your subnet will connect to the Bittensor testchain.

Creating a subnet on the testchain is competitive. Though you will only use the faucet TAO tokens for the testchain, the cost to create a subnet is determined by the rate at which new subnets are registered onto the testchain.

By default, you must have at least 100 test TAO in your owner wallet to create a subnet. However, the exact amount will fluctuate based on demand. Follow the below steps.

### Step 1. Create wallet​

[​](/subnets/create-a-subnet#step-1-create-wallet)If you have not already done so, create Bittensor wallet(s) using the steps described in the Create Wallet guide.

[Create Wallet](/getting-started/wallets)### Step 2. Get the current price​

[​](/subnets/create-a-subnet#step-2-get-the-current-price)```
btcli subnet lock_cost --subtensor.network test
```

```
btcli subnet lock_cost --subtensor.network test
```

Output:

```
>> Subnet lock cost: τ100.000000000
```

```
>> Subnet lock cost: τ100.000000000
```

### Step 3. Get faucet tokens​

[​](/subnets/create-a-subnet#step-3-get-faucet-tokens)The faucet is disabled on the testchain. Hence, if you don't have sufficient faucet tokens, ask the Bittensor Discord community for faucet tokens.

[Bittensor Discord community](https://discord.com/channels/799672011265015819/830068283314929684)### Step 4. Create the subnet​

[​](/subnets/create-a-subnet#step-4-create-the-subnet-1)Create your new subnet on the testchain using the test TAO you received from the previous step. This will create a new subnet on the testchain and give you its owner permissions.

Subnet creation (subnet registration) on the testchain costs test TAO. You will get this test TAO back when the subnet is deregistered.

Run the create subnet command on the testchain.

```
btcli subnet create --subtensor.network test 
```

```
btcli subnet create --subtensor.network test 
```

Output:

```
# Enter the owner wallet name, which gives the coldkey permissions to define running hyperparameters later.>> Enter wallet name (default): owner   # Enter your owner wallet name>> Enter password to unlock key:        # Enter your wallet password.>> Register subnet? [y/n]: <y/n>        # Select yes (y)>> Registering subnet...✅ Registered subnetwork with netuid: 1 # Your subnet netuid will show here, save this for later.
```

```
# Enter the owner wallet name, which gives the coldkey permissions to define running hyperparameters later.>> Enter wallet name (default): owner   # Enter your owner wallet name>> Enter password to unlock key:        # Enter your wallet password.>> Register subnet? [y/n]: <y/n>        # Select yes (y)>> Registering subnet...✅ Registered subnetwork with netuid: 1 # Your subnet netuid will show here, save this for later.
```

## Creating a subnet on mainchain​

[​](/subnets/create-a-subnet#creating-a-subnet-on-mainchain)You do not need to run a local blockchain node to create a subnet on the mainchain. Instead, your subnet will connect to the Bittensor mainchain. Follow the below steps.

Creating a subnet on the mainnet is competitive, and the cost is determined by the rate at which new networks are registered onto the chain. By default, you must have at least 100 TAO in your owner wallet to create a subnet on the mainchain. However, the exact amount will fluctuate based on demand.

### Step 1. Create wallet​

[​](/subnets/create-a-subnet#step-1-create-wallet-1)If you have not already done so, create Bittensor wallet(s) using the steps described in the Create Wallet guide.

[Create Wallet](/getting-started/wallets)### Step 2. Get the current price​

[​](/subnets/create-a-subnet#step-2-get-the-current-price-1)The code below shows how to get the current price of creating a subnet on the mainchain (when the --subtensor.network option is not used, then the btcli will default to the mainchain).

```
--subtensor.network
```

```
btcli
```

```
mainchain
```

```
btcli subnet lock_cost
```

```
btcli subnet lock_cost
```

Output:

```
>> Subnet lock cost: τ100.000000000
```

```
>> Subnet lock cost: τ100.000000000
```

### Step 3. Create the subnet​

[​](/subnets/create-a-subnet#step-3-create-the-subnet)Subnet creation (subnet registration) on the mainchain costs real TAO. You will get this TAO back when the subnet is deregistered.

Use the below command to create a new subnet on the mainchain.

```
btcli subnet create
```

```
btcli subnet create
```

Output:

```
>> Enter wallet name (default): owner   # Enter your owner wallet name>> Enter password to unlock key:        # Enter your wallet password.>> Register subnet? [y/n]: <y/n>        # Select yes (y)>> Registering subnet...✅ Registered subnetwork with netuid: 1 # Your subnet netuid will show here, save this for later.
```

```
>> Enter wallet name (default): owner   # Enter your owner wallet name>> Enter password to unlock key:        # Enter your wallet password.>> Register subnet? [y/n]: <y/n>        # Select yes (y)>> Registering subnet...✅ Registered subnetwork with netuid: 1 # Your subnet netuid will show here, save this for later.
```


---

# Bittensor Subnet Tutorial

## OCR Subnet Tutorial

*Source: [https://docs.bittensor.com/tutorials/ocr-subnet-tutorial](https://docs.bittensor.com/tutorials/ocr-subnet-tutorial)*

* 
[](/)* Managing subnets
* OCR Subnet Tutorial
[SUBMIT A PR](https://github.com/opentensor/developer-docs/blob/main/docs/tutorials/ocr-subnet-tutorial.md)[SUBMIT AN ISSUE](https://github.com/opentensor/developer-docs/issues)# OCR Subnet Tutorial

In this tutorial you will learn how to quickly convert your validated idea into a functional Bittensor subnet. This tutorial begins with a Python notebook that contains the already validated code for optical character recognition (OCR). We demonstrate how straightforward it is to start with such notebooks and produce a working subnet.

## Motivation​

[​](/tutorials/ocr-subnet-tutorial#motivation)Bittensor subnets are:

* Naturally suitable for continuous improvement of the subnet miners.
* High throughput environments to accomplish such improvements.
This is the motivation for creating an OCR subnet for this tutorial. By using the OCR subnet, one can extract the text from an entire library of books in a matter of hours or days. Moreover, when we expose the subnet miners, during training, to examples of  real-world use-cases, the OCR subnet can be fine-tuned to be maximally effective.

## Takeaway lessons​

[​](/tutorials/ocr-subnet-tutorial#takeaway-lessons)When you complete this tutorial, you will know the following:

* How to convert your Python notebook containing the validated idea into a working Bittensor subnet.
* How to use the Bittensor Subnet Template to accomplish this goal.
[Bittensor Subnet Template](https://github.com/opentensor/bittensor-subnet-template)* How to perform subnet validation and subnet mining.
* How to design your own subnet incentive mechanism.
## Tutorial code​

[​](/tutorials/ocr-subnet-tutorial#tutorial-code)### Python notebook​

[​](/tutorials/ocr-subnet-tutorial#python-notebook)The Python notebook we use in this tutorial contains all the three essential components of the OCR subnet:

[notebook](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=M8Cf2XVUJnBh)* Validation flow.
[Validation flow](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=M8Cf2XVUJnBh)* Baseline miner implementation.
[Baseline miner implementation](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=hhKFy5U2EW7e)* Reward model (incentive mechanism).
[Reward model (incentive mechanism)](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=jcwFaIjwJnBj)### OCR subnet repository​

[​](/tutorials/ocr-subnet-tutorial#ocr-subnet-repository)* We will use the OCR subnet repository as our starting point and then incorporate the notebook code to build the OCR subnet.
[OCR subnet repository](https://github.com/steffencruz/ocr_subnet)## Tutorial method​

[​](/tutorials/ocr-subnet-tutorial#tutorial-method)For the rest of this tutorial we will proceed by demonstrating which blocks of Python notebook code are copied into specific sections of the OCR subnet repository.

[OCR subnet repository](https://github.com/steffencruz/ocr_subnet)## Prerequisites​

[​](/tutorials/ocr-subnet-tutorial#prerequisites)### Required reading​

[​](/tutorials/ocr-subnet-tutorial#required-reading)If you are new to Bittensor, read the following sections before you proceed:

1. Introduction that describes how subnets form the heartbeat of the Bittensor network.
[Introduction](/learn/introduction)1. Bittensor Building Blocks that presents the basic building blocks you use to develop your subnet incentive mechanism.
[Bittensor Building Blocks](/learn/bittensor-building-blocks)1. Anatomy of Incentive Mechanism that introduces the general concept of a subnet incentive mechanism.
[Anatomy of Incentive Mechanism](/learn/anatomy-of-incentive-mechanism)## OCR subnet summary​

[​](/tutorials/ocr-subnet-tutorial#ocr-subnet-summary)This tutorial OCR subnet works like this. The below numbered items correspond to the numbers in the diagram:

![Incentive Mechanism Big Picture](/img/docs/OCR-high-level.svg)

![Incentive Mechanism Big Picture](/img/docs/dark-OCR-high-level.svg)

1. The subnet validator sends a challenge simultaneously to multiple subnet miners. In this tutorial the challenge consists of an image file of a synthetic invoice document. The serialized image file is attached to a synapse object called OCRSynapse. This step constitutes the query from the subnet validator to subnet miners.
```
OCRSynapse
```

1. The subnet miners respond after performing the challenge task. After receiving the synapse object containing the image data, each miner then performs the task of extracting, from the image data, its contents, including the text content, the positional information of the text, the fonts used in the text and the font size.
1. The subnet validator then scores each subnet miner based on the quality of the response and how quickly the miner completed the task. The subnet validator uses the original synthetic invoice document as the ground truth for this step.
1. Finally, the subnet validator sets the weights for the subnet miners by sending the weights to the blockchain.
## Step 1: Generate challenge and query the miners​

[​](/tutorials/ocr-subnet-tutorial#step-1-generate-challenge-and-query-the-miners)### Step 1.1: Synthetic PDF as challenge​

[​](/tutorials/ocr-subnet-tutorial#step-11-synthetic-pdf-as-challenge)In this tutorial, the subnet validator will generate synthetic data, which is a PDF document containing an invoice. The subnet validator will use this synthetic PDF as the basis for assessing the subnet miner performance. Synthetic data is an appropriate choice as it provides an unlimited source of customizable validation data. It also enables the subnet validators to gradually increase the difficulty of the task so that the miners are required to continuously improve. This is in contrast to using a pre-existing dataset from the web, where subnet miners can "lookup" the answers on the web.

The contents of the PDF document are the ground truth labels. The subnet validator uses them to score the miner responses. The synthetic PDF document is corrupted with different types of noise to mimic poorly scanned documents. The amount of noise can also be gradually increased to make the task more challenging.

To generate this challenge, the subnet validator applies the following steps:

* Creates a synthetic invoice document using the Python Faker library.
[Python Faker library](https://github.com/joke2k/faker)* Converts this synthetic data into PDF using ReportLab Python library.
[ReportLab Python library](https://docs.reportlab.com/install/open_source_installation/)* Finally, the validator creates the challenge by converting this PDF into a corrupted image, called noisy_image.
```
noisy_image
```

#### Code snapshot​

[​](/tutorials/ocr-subnet-tutorial#code-snapshot)See below for a snapshot view of the code.

```
# Generates a PDF invoice from the raw data passed in as "invoice_data" dictionary # and saves the PDF with "filename"def create_invoice(invoice_data, filename):...# Using Faker, generate sample data for the invoiceinvoice_info = {    "company_name": fake.company(),    "company_address": fake.address(),    "company_city_zip": f'{fake.city()}, {fake.zipcode()}',...}...# Pass the "invoice_info" containing the Faker-generated raw data # to create_invoice() method and generate the synthetic invoice PDF pdf_filename = "sample_invoice.pdf"data = create_invoice(invoice_info, pdf_filename)...# Loads PDF and converts it into usable PIL image using Pillow library# Used by the corrupt_image() method def load_image(pdf_path, page=0, zoom_x=1.0, zoom_y=1.0):  ...# Accepts a PDF, uses load_image() method to convert to image # and adds noise, blur, spots, rotates the page, curls corners, darkens edges so # that the overall result is noisy. Saves back in PDF format. # This is our corrupted synthetic PDF document. def corrupt_image(input_pdf_path, output_pdf_path, border=50, noise=0.1, spot=(100,100), scale=0.95, theta=0.2, blur=0.5):  ...
```

```
# Generates a PDF invoice from the raw data passed in as "invoice_data" dictionary # and saves the PDF with "filename"def create_invoice(invoice_data, filename):...# Using Faker, generate sample data for the invoiceinvoice_info = {    "company_name": fake.company(),    "company_address": fake.address(),    "company_city_zip": f'{fake.city()}, {fake.zipcode()}',...}...# Pass the "invoice_info" containing the Faker-generated raw data # to create_invoice() method and generate the synthetic invoice PDF pdf_filename = "sample_invoice.pdf"data = create_invoice(invoice_info, pdf_filename)...# Loads PDF and converts it into usable PIL image using Pillow library# Used by the corrupt_image() method def load_image(pdf_path, page=0, zoom_x=1.0, zoom_y=1.0):  ...# Accepts a PDF, uses load_image() method to convert to image # and adds noise, blur, spots, rotates the page, curls corners, darkens edges so # that the overall result is noisy. Saves back in PDF format. # This is our corrupted synthetic PDF document. def corrupt_image(input_pdf_path, output_pdf_path, border=50, noise=0.1, spot=(100,100), scale=0.95, theta=0.2, blur=0.5):  ...
```

Collab Notebook source: The validated code for the above synthetic PDF generation logic is in Validation flow cell.

[Validation flow cell](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=M8Cf2XVUJnBh)All we have to do is to copy the above Notebook code into a proper place in the OCR subnet repo.

```
...├── ocr_subnet│   ├── __init__.py│  ...│   └── validator│       ├── __init__.py│       ├── corrupt.py│       ├── forward.py│       ├── generate.py│       ├── reward.py│       └── utils.py...
```

```
...├── ocr_subnet│   ├── __init__.py│  ...│   └── validator│       ├── __init__.py│       ├── corrupt.py│       ├── forward.py│       ├── generate.py│       ├── reward.py│       └── utils.py...
```

We copy the above Notebook code into the following code files. Click on the OCR repo file names to see the copied code:

| Table content (formatting not preserved) |
|---|
| Python Notebook source | OCR repo destination |
| Methods: create_invoice, random_items, load_image, and lists items_list and invoice_info and all the import statements in cell 34. | ocr_subnet/validator/generate.py |
| Method: corrupt_image | ocr_subnet/validator/corrupt.py |

```
create_invoice
```

```
random_items
```

```
load_image
```

```
items_list
```

```
invoice_info
```

```
import
```

[ocr_subnet/validator/generate.py](https://github.com/steffencruz/ocr_subnet/blob/main/ocr_subnet/validator/generate.py)```
corrupt_image
```

[ocr_subnet/validator/corrupt.py](https://github.com/steffencruz/ocr_subnet/blob/main/ocr_subnet/validator/corrupt.py)### Step 1.2: Query miners​

[​](/tutorials/ocr-subnet-tutorial#step-12-query-miners)Next, the subnet validator sends this noisy_image to the miners, tasking them to perform OCR and content extraction.

```
noisy_image
```

Collab Notebook source: In the validated Collab Notebook code, this step is accomplished by directly passing the path information of the noisy_image from the Validator cell to the miner.

```
noisy_image
```

See noisy_image from line 32 in Quick sanity check cell being passed to line 90 of the Miner cell.

[See noisy_image from line 32 in Quick sanity check cell](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=_rHjuG6JD--P)```
noisy_image
```

[line 90 of the Miner cell](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=hhKFy5U2EW7e)#### Define OCRSynapse class​

[​](/tutorials/ocr-subnet-tutorial#define-ocrsynapse-class)However, in a Bittensor subnet, any communication between a subnet validator and a subnet miner must use an object of the type Synapse. Hence, the subnet validator must attach the corrupted image to a Synapse object and send this object to the miners. The miners will then update the passed synapse by attaching their responses into this same object and send them back to the subnet validator.

```
Synapse
```

```
Synapse
```

#### Code snapshot​

[​](/tutorials/ocr-subnet-tutorial#code-snapshot-1)```
# OCRSynapse class, using bt.Synapse as its base.# This protocol enables communication between the miner and the validator.# Attributes:#    - image: A pdf image to be processed by the miner.#    - response: List[dict] containing data extracted from the image.class OCRSynapse(bt.Synapse):   """    A simple OCR synapse protocol representation which uses bt.Synapse as its base.    This protocol enables communication between the miner and the validator.    Attributes:    - image: A pdf image to be processed by the miner.    - response: List[dict] containing data extracted from the image.    """    # Required request input, filled by sending dendrite caller. It is a base64 encoded string.    base64_image: str    # Optional request output, filled by receiving axon.    response: typing.Optional[typing.List[dict]] = None
```

```
# OCRSynapse class, using bt.Synapse as its base.# This protocol enables communication between the miner and the validator.# Attributes:#    - image: A pdf image to be processed by the miner.#    - response: List[dict] containing data extracted from the image.class OCRSynapse(bt.Synapse):   """    A simple OCR synapse protocol representation which uses bt.Synapse as its base.    This protocol enables communication between the miner and the validator.    Attributes:    - image: A pdf image to be processed by the miner.    - response: List[dict] containing data extracted from the image.    """    # Required request input, filled by sending dendrite caller. It is a base64 encoded string.    base64_image: str    # Optional request output, filled by receiving axon.    response: typing.Optional[typing.List[dict]] = None
```

The OCRSynapse object can only contain serializable objects. This is because both the subnet validators and the subnet miners must be able to deserialize after receiving the object.

```
OCRSynapse
```

See the OCRSynapse class definition in ocr_subnet/protocol.py.

```
OCRSynapse
```

[ocr_subnet/protocol.py](https://github.com/steffencruz/ocr_subnet/blob/main/ocr_subnet/protocol.py)```
...├── ocr_subnet│   ├── __init__.py│   ├── base│   │   ├── __init__.py│   │   ...│   ├── protocol.py...
```

```
...├── ocr_subnet│   ├── __init__.py│   ├── base│   │   ├── __init__.py│   │   ...│   ├── protocol.py...
```

See Neuron-to-neuron communication.

[Neuron-to-neuron communication](/learn/bittensor-building-blocks#neuron-to-neuron-communication)#### Send OCRSynapse to miners​

[​](/tutorials/ocr-subnet-tutorial#send-ocrsynapse-to-miners)With the OCRSynapse class defined, next we use the network client dendrite of the subnet validator to send queries to the Axon server of the subnet miners.

```
OCRSynapse
```

```
dendrite
```

```
Axon
```

#### Code snapshot​

[​](/tutorials/ocr-subnet-tutorial#code-snapshot-2)```
# Create synapse object to send to the miner and attach the image.# convert PIL image into a json serializable formatsynapse = OCRSynapse(base64_image = serialize_image(image))# The dendrite client of the validator queries the miners in the subnetresponses = self.dendrite.query(    # Send the query to selected miner axons in the network.    axons=[self.metagraph.axons[uid] for uid in miner_uids],    # Pass the synapse to the miner.    synapse=synapse,...)
```

```
# Create synapse object to send to the miner and attach the image.# convert PIL image into a json serializable formatsynapse = OCRSynapse(base64_image = serialize_image(image))# The dendrite client of the validator queries the miners in the subnetresponses = self.dendrite.query(    # Send the query to selected miner axons in the network.    axons=[self.metagraph.axons[uid] for uid in miner_uids],    # Pass the synapse to the miner.    synapse=synapse,...)
```

See ocr_subnet/validator/forward.py which contains all this communication logic.

[ocr_subnet/validator/forward.py](https://github.com/steffencruz/ocr_subnet/blob/main/ocr_subnet/validator/forward.py)Also note that the scripts/ directory contains the sample invoice document and its noisy version. The subnet validator uses these as ground truth labels to score the miner responses.

[scripts/](https://github.com/steffencruz/ocr_subnet/tree/main/scripts)```
...├── ocr_subnet│   ├── __init__.py│  ...│   └── validator│       ├── __init__.py│       ├── corrupt.py│       ├── forward.py│       ├── generate.py│       ├── reward.py│       └── utils.py...
```

```
...├── ocr_subnet│   ├── __init__.py│  ...│   └── validator│       ├── __init__.py│       ├── corrupt.py│       ├── forward.py│       ├── generate.py│       ├── reward.py│       └── utils.py...
```

## Step 2: Miner response​

[​](/tutorials/ocr-subnet-tutorial#step-2-miner-response)Having received the OCRSynapse object with the corrupted image data in it, the miners will next perform the data extraction.

```
OCRSynapse
```

### Base miner​

[​](/tutorials/ocr-subnet-tutorial#base-miner)The Python notebook contains an implementation of the base miner, which uses pytesseract, a popular open source OCR tool to extract data from the image sent by the subnet validator.

[pytesseract](https://github.com/madmaze/pytesseract)```
pytesseract
```

Collab Notebook source: See the miner method in this Miner cell of the Collab Notebook.

```
miner
```

[Miner cell of the Collab Notebook](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=hhKFy5U2EW7e)#### Code snapshot​

[​](/tutorials/ocr-subnet-tutorial#code-snapshot-3)```
import pytesseract# Extracts text data from image using pytesseract. This is the baseline miner.def miner(image, merge=True, sort=True)...response = miner(noisy_image, merge=True)
```

```
import pytesseract# Extracts text data from image using pytesseract. This is the baseline miner.def miner(image, merge=True, sort=True)...response = miner(noisy_image, merge=True)
```

We copy the above miner code from the Notebook into the following code files. Click on the OCR repo file names to see the copied code:

```
...├── neurons│   ├── __init__.py│   ├── miner.py│   └── validator.py...
```

```
...├── neurons│   ├── __init__.py│   ├── miner.py│   └── validator.py...
```

| Table content (formatting not preserved) |
|---|
| Python Notebook source | OCR repo destination |
| Methods: group_and_merge_boxes and miner and all the import statements in this Miner cell of the Collab Notebook. | neurons/miner.py |

```
group_and_merge_boxes
```

```
miner
```

```
import
```

[Miner cell of the Collab Notebook](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=hhKFy5U2EW7e)[neurons/miner.py](https://github.com/steffencruz/ocr_subnet/blob/main/neurons/miner.py)pytesseract is well-suited for this OCR problem. But it can be beaten by a subnet miner using more sophisticated approaches such as deep learning for OCR.

[pytesseract](https://github.com/madmaze/pytesseract)```
pytesseract
```

## Step 3: Scoring miner responses​

[​](/tutorials/ocr-subnet-tutorial#step-3-scoring-miner-responses)When a miner sends its response, the subnet validator scores the quality of the response in the following way:

Prediction reward
: Compute the similarity between the ground truth and the prediction of the miner for the text content, text position and the font. This is conceptually equivalent to a loss function that is used in a machine learning setting, with the only difference being that rewards are a function to be maximized rather than minimized. The total prediction reward is calculated as below:

* For each section of the synthetic invoice document, compute the three partial reward quantities:

text reward.
position reward.
font reward.
* text reward.
* position reward.
* font reward.
* This is done by comparing a section in the miner response to the corresponding section in the ground truth synthetic invoice document.
* Add the above three partial reward quantities to compute the total loss for the particular section.
* Take the mean score of all such total rewards over all the sections of the invoice document.
Response time penalty
: Calculate the response time penalty for the miner for these predictions. The goal here is to assign higher rewards to faster miners.

#### Code snapshot​

[​](/tutorials/ocr-subnet-tutorial#code-snapshot-4)```
# Calculate the edit distance between two strings.def get_text_reward(text1: str, text2: str = None):  ...# Calculate the intersection over union (IoU) of two bounding boxes.def get_position_reward(boxA: List[float], boxB: List[float] = None):  ...# Calculate the distance between two fonts, based on the font size and font family.def get_font_reward(font1: dict, font2: dict = None, alpha_size=1.0, alpha_family=1.0):  ...# Score a section of the image based on the section's correctness.# Correctness is defined as:# - the intersection over union of the bounding boxes,# - the delta between the predicted font and the ground truth font,# - and the edit distance between the predicted text and the ground truth text.def section_reward(label: dict, pred: dict, alpha_p=1.0, alpha_f=1.0, alpha_t=1.0, verbose=False):  ...  reward = {        'text': get_text_reward(label['text'], pred.get('text')),        'position': get_position_reward(label['position'], pred.get('position')),        'font': get_font_reward(label['font'], pred.get('font')),    }    reward['total'] = (alpha_t * reward['text'] + alpha_p * reward['position'] + alpha_f * reward['font']) / (alpha_p + alpha_f + alpha_t)...# Reward the miner response.def reward(image_data: List[dict], predictions: List[dict], time_elapsed: float) -> float:    time_reward = max(1 - time_elapsed / max_time, 0)    total_reward = (alpha_prediction * prediction_reward + alpha_time * time_reward) / (alpha_prediction + alpha_time)...
```

```
# Calculate the edit distance between two strings.def get_text_reward(text1: str, text2: str = None):  ...# Calculate the intersection over union (IoU) of two bounding boxes.def get_position_reward(boxA: List[float], boxB: List[float] = None):  ...# Calculate the distance between two fonts, based on the font size and font family.def get_font_reward(font1: dict, font2: dict = None, alpha_size=1.0, alpha_family=1.0):  ...# Score a section of the image based on the section's correctness.# Correctness is defined as:# - the intersection over union of the bounding boxes,# - the delta between the predicted font and the ground truth font,# - and the edit distance between the predicted text and the ground truth text.def section_reward(label: dict, pred: dict, alpha_p=1.0, alpha_f=1.0, alpha_t=1.0, verbose=False):  ...  reward = {        'text': get_text_reward(label['text'], pred.get('text')),        'position': get_position_reward(label['position'], pred.get('position')),        'font': get_font_reward(label['font'], pred.get('font')),    }    reward['total'] = (alpha_t * reward['text'] + alpha_p * reward['position'] + alpha_f * reward['font']) / (alpha_p + alpha_f + alpha_t)...# Reward the miner response.def reward(image_data: List[dict], predictions: List[dict], time_elapsed: float) -> float:    time_reward = max(1 - time_elapsed / max_time, 0)    total_reward = (alpha_prediction * prediction_reward + alpha_time * time_reward) / (alpha_prediction + alpha_time)...
```

The rewards attained by miners are averaged over many turns using an exponential moving average (EMA). This is done to obtain a more reliable estimate of the overall performance on the task. We often refer to these smoothed rewards as EMA scores.

Collab Notebook source: See the Incentive mechanism cell.

[Incentive mechanism cell](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=jcwFaIjwJnBj)We copy the above miner code from the Notebook into the following code files. Click on the OCR repo file names to see the copied code:

```
...├── ocr_subnet│   ├── __init__.py│  ...│   └── validator│       ├── __init__.py│       ├── corrupt.py│       ├── forward.py│       ├── generate.py│       ├── reward.py│       └── utils.py...
```

```
...├── ocr_subnet│   ├── __init__.py│  ...│   └── validator│       ├── __init__.py│       ├── corrupt.py│       ├── forward.py│       ├── generate.py│       ├── reward.py│       └── utils.py...
```

| Table content (formatting not preserved) |
|---|
| Python Notebook source | OCR repo destination |
| Methods: reward and miner and all the import statements in this Miner cell of the Collab Notebook. | ocr_subnet/validator/reward.py |
| Method section_reward. | Method loss in the reward.py. |
| Methods: get_position_reward, get_text_reward and get_font_reward. | Methods: get_iou, get_edit_distance and get_font_distance, respectively, in ocr_subnet/validator/utils.py |

```
reward
```

```
miner
```

```
import
```

[Miner cell of the Collab Notebook](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=hhKFy5U2EW7e)[ocr_subnet/validator/reward.py](https://github.com/steffencruz/ocr_subnet/blob/main/ocr_subnet/validator/reward.py)```
section_reward
```

```
loss
```

```
reward.py
```

```
get_position_reward
```

```
get_text_reward
```

```
get_font_reward
```

```
get_iou
```

```
get_edit_distance
```

```
get_font_distance
```

[ocr_subnet/validator/utils.py](https://github.com/steffencruz/ocr_subnet/blob/main/ocr_subnet/validator/utils.py)## Step 4: Set weights​

[​](/tutorials/ocr-subnet-tutorial#step-4-set-weights)Finally, as shown in the above OCR subnet summary, the subnet validator normalizes the EMA scores and sets the weights of the subnet miners to the blockchain. This step is not in the Python notebooks. This step is performed by the function set_weights in the ocr_subnet/base/validator.py and it is already available fully implemented in the OCR subnet repo.

[OCR subnet summary](/tutorials/ocr-subnet-tutorial#ocr-subnet-summary)```
set_weights
```

[ocr_subnet/base/validator.py](https://github.com/steffencruz/ocr_subnet/blob/main/ocr_subnet/base/validator.py#L206)## Next steps​

[​](/tutorials/ocr-subnet-tutorial#next-steps)Congratulations, you have successfully transformed your Python Notebook into a working Bittensor subnet. See below tips for your next steps.

Can you think of ways your incentive mechanism would lead to undesirable behavior? For example:

* The positional structure of the invoice, i.e., how sections are positioned in the invoice, is mostly static and thus easily predictable. Hence all subnet miners may predict the position correctly without doing much work. This will render the position reward as ineffective. How can you avoid this?
* Experiment with the α\alphaα hyperparameters to make the subnet miners compete more effectively. See Reward model (incentive mechanism).
[Reward model (incentive mechanism)](https://colab.research.google.com/drive/1Z2KT11hyKwsmMib8C6lDsY93vnomJznz#scrollTo=jcwFaIjwJnBj)
---

# Bittensor Overview

## Bittensor Documentation

*Source: [https://docs.bittensor.com/](https://docs.bittensor.com/)*

* 
[](/)* Docs Home
[SUBMIT A PR](https://github.com/opentensor/developer-docs/blob/main/docs/index.md)[SUBMIT AN ISSUE](https://github.com/opentensor/developer-docs/issues)# Bittensor Documentation

Bittensor is an open source platform where participants produce best-in-class digital commodities, including compute power, storage space, artificial intelligence (AI) inference and training, protein folding, financial markets prediction, and many more.

Bittensor is composed of distinct subnets. Each subnet is an independent community of miners (who produce the commodity), and validators (who evaluate the miners' work).

The Bittensor network constantly emits liquidity, in the form of its token, TAO (τ\tauτ), to participants in proportion to the value of their contributions. Participants include:

* Miners—Work to produce digital commodities. See mining in Bittensor.
[mining in Bittensor](/miners/)* Validators—Evaluate the quality of miners' work. See validating in Bittensor
[See validating in Bittensor](/validators/)* Subnet Creators—Manage the incentive mechanisms that specify the work miners and validate must perform and evaluate, respectively. See Create a Subnet
[Create a Subnet](/subnets/create-a-subnet)* Stakers—TAO holders can support specific validators by staking TAO to them. See Staking.
[Staking](/staking-and-delegation/delegation)Browse the subnets and explore links to their code repositories on Taostats' subnets listings.

[Taostats' subnets listings](https://taostats.io/subnets)[READ MORE](/learn/introduction)[READ MORE](/learn/introduction)[READ MORE](/tools)[READ MORE](https://taostats.io/subnets)[Bittensor media assetsMedia assets](/media-assets)## Participate​

[​](/#participate)You can participate in an existing subnet as either a subnet validator or a subnet miner, or by staking your TAO to running validators.

[READ MORE](/staking-and-delegation/delegation)[READ MORE](/miners)[READ MORE](/validators)[READ MORE](/emissions)[READ MORE](/governance)[READ MORE](/senate)## Running a subnet​

[​](/#running-a-subnet)Ready to run your own subnet? Follow the below links.

[READ MORE](/tutorials/basic-subnet-tutorials)[READ MORE](/subnets/create-a-subnet)[READ MORE](/tutorials/ocr-subnet-tutorial)[READ MORE](/subnets/subnet-hyperparameters)## Bittensor CLI, SDK, Wallet SDK​

[​](/#bittensor-cli-sdk-wallet-sdk)Use the Bittensor CLI and SDK and Wallet SDK to develop and participate in the Bittensor network.

See Legacy Bittensor 7.4.0 Documentation.

[Legacy Bittensor 7.4.0 Documentation](/legacy-python-api/html/index.html)[Bittensor CLI](/btcli)[Bittensor SDK](/bt-api-ref)[Wallet SDK](/btwallet-api/html/index.html)
---

