from sqlmodel import create_engine, SQLModel, Session
import os

# Por defecto usa localhost para desarrollo local fuera de docker, 
# pero idealmente usaremos variables de entorno.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/multimedia_db")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
