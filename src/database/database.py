from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine
from dotenv import load_dotenv
import os

load_dotenv()

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        database_uri = os.getenv("DATABASE_URI")
        if not database_uri:
            raise RuntimeError("DATABASE_URI environment variable is not set")
        _engine = create_engine(database_uri, echo=False)
    return _engine


def get_session():
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
