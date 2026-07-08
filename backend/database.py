"""
=============================================================================
LEARNING MODULE: Relational Databases & ORMs
=============================================================================
This file sets up the connection to our SQLite database using SQLAlchemy.

Key Concepts Used Here:
1. SQLite: A lightweight, file-based relational database. Perfect for local 
   development and small applications because it requires no separate server.
2. ORM (Object-Relational Mapping): SQLAlchemy is an ORM. Instead of writing
   raw SQL queries (like `SELECT * FROM jobs`), we define Python classes 
   (`JobDB`, `CandidateDB`). The ORM automatically translates our Python code 
   into SQL under the hood, protecting us from SQL injection and making 
   the code much easier to read and maintain.
=============================================================================
"""

import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./ats.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class JobDB(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    required_skills = Column(Text)
    min_experience_years = Column(Integer)
    education = Column(String, nullable=True)
    additional_context = Column(Text, nullable=True)

    candidates = relationship("CandidateDB", back_populates="job", cascade="all, delete-orphan")

class CandidateDB(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    filename = Column(String)
    score_data_json = Column(Text)  # We will store the Pydantic model as JSON

    job = relationship("JobDB", back_populates="candidates")

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
