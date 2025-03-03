import time
import json
import requests
import torch
import bittensor as bt
from template.base.validator import BaseValidatorNeuron
import asyncio
import os
from loguru import logger
from typing import List, Dict, Optional
import hashlib
import secrets
import subprocess
from utils.pogs import fetch_compute_specs, compare_compute_resources, compute_resource_score

class PolarisNode(BaseValidatorNeuron):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.max_allowed_weights = 500  # Maximum allowed validator weights
        self.active_compute_nodes: List[str] = []  # List of active compute nodes
        self.trust_scores = {}  # Stores miner trust scores dynamically
        self.trust_history = {}  # Store trust history (consider on-chain storage)
        self.challenge_solutions = {}  # Expected challenge solutions for miners
    
    async def retrieve_hardware_specs(self, node_id: str) -> Optional[str]:
        """Retrieves TPM attestation hash securely."""
        try:
            output = subprocess.check_output(["tpm2_getrandom", "32"], stderr=subprocess.DEVNULL)
            return hashlib.sha256(output).hexdigest()
        except subprocess.SubprocessError as e:
            logger.error(f"{node_id}: TPM attestation failed - {e}")
            return None
    
    async def validate_hardware_integrity(self, node_id: str, reported_hash: str) -> bool:
        """Validates miner hardware by comparing TPM attestation hashes."""
        expected_hash = await self.retrieve_hardware_specs(node_id)
        return expected_hash is not None and reported_hash == expected_hash
    
    async def generate_challenge(self, node_id: str) -> str:
        """Generates a cryptographic challenge for the miner."""
        nonce = secrets.token_hex(16)  # Use a secure nonce
        solution = hashlib.sha256(nonce.encode()).hexdigest()
        self.challenge_solutions[node_id] = solution
        return nonce  # Only return the nonce, not the solution
    
    async def verify_challenge_response(self, node_id: str, response: str) -> bool:
        """Verifies if the miner's response correctly computes the expected hash solution."""
        expected_solution = self.challenge_solutions.pop(node_id, None)
        if not expected_solution:
            logger.warning(f"No challenge found for miner {node_id}.")
            return False
        return response == expected_solution
    
    async def decentralized_miner_verification(self, miners: List[str]) -> Dict[str, float]:
        """Validates miners asynchronously using TPM attestation and assigns trust scores."""
        miner_scores = {}
        compute_resources = await self.get_unverified_miners()
        if not compute_resources:
            logger.warning("No unverified miners available.")
            return {}
        
        active_miners = list(compute_resources.keys())
        
        for miner in miners:
            if miner not in active_miners:
                logger.debug(f"Skipping inactive miner {miner}.")
                continue
            
            miner_resources = compute_resources.get(miner)
            if miner_resources:
                tpm_hash = await self.retrieve_hardware_specs(miner)
                if not await self.validate_hardware_integrity(miner, tpm_hash):
                    logger.info(f"Miner {miner} failed TPM verification.")
                    continue
                
                challenge = await self.generate_challenge(miner)
                response = await self.collect_miner_response(miner, challenge)  # Implement async miner response collection
                
                if not await self.verify_challenge_response(miner, response):
                    logger.info(f"Miner {miner} failed challenge response.")
                    continue
                
                compute_score = compute_resource_score(miner_resources)[0]
                self.trust_scores[miner] = compute_score
                self.trust_history.setdefault(miner, []).append(compute_score)
                miner_scores[miner] = compute_score
        
        return miner_scores
    
    async def set_weights_based_on_trust(self):
        """Normalizes and sets miner trust scores dynamically on the blockchain."""
        if not self.trust_scores:
            logger.info("No miner trust scores available to set weights.")
            return
        
        uids = list(self.trust_scores.keys())
        scores = torch.tensor(list(self.trust_scores.values()), dtype=torch.float32)
        scores = torch.relu(scores)  # Ensure non-negative scores
        if scores.sum() == 0:
            logger.warning("All trust scores are zero; skipping weight update.")
            return
        
        weights = torch.nn.functional.normalize(scores, p=1.0, dim=0)
        
        try:
            await self.subtensor.set_weights(
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
        """Periodically runs miner verification, updates trust scores, and sets weights."""
        try:
            logger.info("Starting decentralized miner verification...")
            registered_miners = await self.get_registered_miners()
            trust_scores = await self.decentralized_miner_verification(registered_miners)
            if trust_scores:
                await self.set_weights_based_on_trust()
        except Exception as e:
            logger.error(f"Error in forward: {str(e)}")
    
    async def __aenter__(self):
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
    
    async def setup(self):
        """Setup logic before running the validator."""
        pass
    
    async def cleanup(self):
        """Cleanup resources before shutting down the validator."""
        pass

if __name__ == "__main__":
    async def main():
        async with PolarisNode() as validator:
            while True:
                logger.info(f"Validator running... {time.time()}")
                await validator.forward()
                await asyncio.sleep(300)  # Wait 5 minutes before next verification cycle
    
    asyncio.run(main())