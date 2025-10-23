from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine
from dotenv import load_dotenv
import os

load_dotenv()

supabase_sql = os.getenv("DATABASE_URI", "")

engine = create_engine(supabase_sql, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
