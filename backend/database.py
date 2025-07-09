from sqlmodel import SQLModel, create_engine, Session
import os

DATABASE_URL = "postgresql://admin:admin@db:5432/maomo"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    return Session(engine)

def init_db():
    SQLModel.metadata.create_all(engine)
