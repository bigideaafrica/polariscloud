import time
import json
import requests
import torch
import bittensor as bt
from template.base.validator import BaseValidatorNeuron
import asyncio
import os
from loguru import logger
from typing import List, Dict
import hashlib
import secrets
import subprocess
from utils.pogs import fetch_compute_specs, compare_compute_resources, compute_resource_score

class PolarisNode(BaseValidatorNeuron):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.max_allowed_weights = 500
        self.active_compute_nodes: List[str] = []
        self.trust_scores = {}

    def retrieve_hardware_specs(self, node_id):
        try:
            output = subprocess.check_output(["tpm2_getrandom", "32"], stderr=subprocess.DEVNULL)
            return hashlib.sha256(output).hexdigest()
        except Exception as e:
            logger.error(f"{node_id}: Failed to retrieve TPM attestation - {e}")
            return None

    def validate_hardware_integrity(self, node_id, reported_hash):
        expected_hash = self.retrieve_hardware_specs(node_id)
        return reported_hash == expected_hash if expected_hash else False

    def request_proof_of_computation(self, node_id):
        challenge = secrets.token_hex(16)
        proof = hashlib.sha256(f"{node_id}_{challenge}".encode()).hexdigest()
        return self.verify_cryptographic_proof(node_id, challenge, proof)

    def verify_cryptographic_proof(self, node_id, challenge, proof):
        expected_proof = hashlib.sha256(f"{node_id}_{challenge}".encode()).hexdigest()
        return proof == expected_proof

    def get_registered_miners(self) -> List[int]:
        try:
            self.metagraph.sync()
            return self.metagraph.uids.tolist()
        except Exception as e:
            logger.error(f"Error fetching registered miners: {e}")
            return []

    def decentralized_miner_verification(self, miners):
        miner_scores = {}
        compute_resources = self.get_unverified_miners()
        active_miners = list(compute_resources.keys())
        for miner in miners:
            if miner not in active_miners:
                logger.debug(f"Miner {miner} is not active. Skipping...")
                continue
            miner_resources = compute_resources.get(miner, None)
            if miner_resources:
                tpm_hash = self.retrieve_hardware_specs(miner)
                if not self.validate_hardware_integrity(miner, tpm_hash):
                    logger.info(f"Miner {miner} failed TPM verification.")
                    continue
                compute_score = compute_resource_score(miner_resources)[0]
                self.trust_scores[miner] = compute_score
                miner_scores[miner] = compute_score
        return miner_scores

    def set_weights_based_on_trust(self):
        if not self.trust_scores:
            logger.info("No miner trust scores available to set weights.")
            return
        uids = list(self.trust_scores.keys())
        scores = torch.tensor(list(self.trust_scores.values()), dtype=torch.float32)
        scores[scores < 0] = 0  # Remove negative scores
        weights = torch.nn.functional.normalize(scores, p=1.0, dim=0)
        try:
            self.subtensor.set_weights(
                netuid=self.netuid,
                wallet=self.wallet,
                uids=uids,
                weights=weights,
                wait_for_inclusion=False
            )
            logger.success("Successfully set trust-based weights on the blockchain.")
        except Exception as e:
            logger.error(f"Failed to set weights: {e}")

    async def forward(self):
        try:
            logger.info("Starting decentralized miner verification...")
            registered_miners = self.get_registered_miners()
            trust_scores = self.decentralized_miner_verification(registered_miners)
            if trust_scores:
                self.set_weights_based_on_trust()
        except Exception as e:
            logger.error(f"Error in forward: {str(e)}")

    async def __aenter__(self):
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def setup(self):
        pass

    async def cleanup(self):
        pass

if __name__ == "__main__":
    async def main():
        async with PolarisNode() as validator:
            while True:
                logger.info(f"Validator running... {time.time()}")
                await validator.forward()
                await asyncio.sleep(300)
    asyncio.run(main())
