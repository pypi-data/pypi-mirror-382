from cua.settings import settings

if settings.ENVIRONMENT == "development":
    from cua.logging_config_dev import setup_logging
    setup_logging(level="DEBUG")

else:
    from cua.logging_config import setup_logging
    setup_logging(level="DEBUG")


import logging
logger = logging.getLogger(__name__)

import asyncio
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from cua.state import State, StateEnum

async def main():    
    logger.info(f"Starting CUA (version: 0.0.1)")
    
    state = State(state=StateEnum.INITIALIZED)
    
    # register
    while True:
        match state.state:
            case StateEnum.INITIALIZED:
                await register(state)
                
            case StateEnum.REGISTERED:
                await run_loop()
    

async def _register_once():
    logger.info(f"Registering with backend: {settings.BACKEND_API_BASE_URL}/api/v2/agent-comm/register")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BACKEND_API_BASE_URL}/api/v2/agent-comm/register",
            json={
                "owner_secret_key": settings.OWNER_SECRET_KEY,
                "vm_type": "internal_azure_vmss",
                "azure_vmss_id": "/subscriptions/db0a29df-a02a-439a-a3f4-20345a628714/resourceGroups/rg-vmss-7IHwTpNYN/providers/Microsoft.Compute/virtualMachineScaleSets/7IHwTpNYN",
                "azure_vm_id": None,
                "private_ip": "10.0.0.6"
            }
        )
        response.raise_for_status()
        return response.json()["accepted"], response.json()["agent_id"], response.json()["agent_secret_key"]


async def register(state: State, poll_interval: float = 5):
    while True:
        try:
            accepted, agent_id, agent_secret_key = await _register_once()
        except Exception as e:
            logger.exception(f"Error registering with backend: {e}")
            await asyncio.sleep(poll_interval)
            continue
        
        if accepted:
            state.state = StateEnum.REGISTERED
            state.agent_id = agent_id
            state.agent_secret_key = agent_secret_key
            logger.info(f"Registration accepted. Agent ID: {agent_id}")
            break
        else:
            logger.info(f"Registration not accepted. Retrying in {poll_interval} seconds...")
            await asyncio.sleep(poll_interval)

async def run_loop():
    pass


def cli():
    """CLI entry point"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nClient interrupted by user")
    except Exception as e:
        logger.exception(f"Client error: {e}")
    finally:
        logger.info("Client shutting down...")


if __name__ == "__main__":
    cli()