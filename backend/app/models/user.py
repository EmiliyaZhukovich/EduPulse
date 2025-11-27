from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.database import Base


class Curator(Base):
    __tablename__ = "curators"

    id = Column(Integer, primary_key=True, index=True)
    keycloak_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    keycloak_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
