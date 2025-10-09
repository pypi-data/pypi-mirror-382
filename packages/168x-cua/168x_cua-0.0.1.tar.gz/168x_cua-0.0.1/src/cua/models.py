from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Float, BigInteger, UniqueConstraint, Boolean, UUID, event, or_, Time, LargeBinary

from enum import Enum as PyEnum

from database import Base

class RunState(PyEnum):
    STOP = "stop"
    RUN = "run"
    RUN_ALL = "run_all"

class DB_CuaConfig(Base):
    __tablename__ = "cua_config"
    
    agent_id = Column(Integer, primary_key=True, index=True)
    secret_key = Column(String(100), nullable=True)
    
    system_prompt = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    
    run_state = Column(Enum(RunState, native_enum=False), nullable=True)
    
class 
    