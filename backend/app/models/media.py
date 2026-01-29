from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel


class Libro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(index=True)
    isbn: Optional[str] = Field(default=None, unique=True, index=True)
    autor: str = Field(index=True)
    paginas_leidas: int = Field(default=0)
    paginas_totales: int = Field(default=0)
    fecha_publicacion: date = None


class Pelicula(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(index=True)


class Serie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(index=True)
    