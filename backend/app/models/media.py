from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import computed_field


class Libro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(index=True)
    isbn: Optional[str] = Field(default=None, unique=True, index=True)
    autor: str = Field(index=True)
    paginas_leidas: int = Field(default=0)
    paginas_totales: int = Field(default=0)
    fecha_publicacion: Optional[date] = None

    @computed_field
    @property
    def porcentaje_leido(self) -> float:
        if not self.paginas_totales or self.paginas_totales == 0:
            return 0.0
        return round((self.paginas_leidas * 100) / self.paginas_totales, 2)


class Pelicula(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(index=True)


class Serie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(index=True)
    sinopsis: Optional[str] = Field(default=None)
