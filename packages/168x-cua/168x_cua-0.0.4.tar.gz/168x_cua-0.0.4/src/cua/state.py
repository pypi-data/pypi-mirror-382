from pydantic import BaseModel
from enum import Enum

class StateEnum(Enum):
    INITIALIZED = "initialized"
    REGISTERED = "registered"

class State(BaseModel):
    state: StateEnum
    
    agent_id: str | None = None
    agent_secret_key: str | None = None