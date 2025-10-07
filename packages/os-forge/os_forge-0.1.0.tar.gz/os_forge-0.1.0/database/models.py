"""
Database Models for OS Forge

SQLAlchemy models for storing hardening results and audit logs.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class HardeningResult(Base):
    """
    Model for storing hardening rule execution results
    
    This table stores the results of each hardening rule execution,
    including before/after values and rollback information.
    """
    __tablename__ = "hardening_results"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String, index=True)
    host = Column(String, default="localhost")
    description = Column(String)
    severity = Column(String)
    status = Column(String)  # pass, fail, error, rollback_success
    old_value = Column(Text)
    new_value = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    rollback_data = Column(Text)  # JSON for rollback info
    
    def __repr__(self):
        return f"<HardeningResult(rule_id='{self.rule_id}', status='{self.status}', host='{self.host}')>"

