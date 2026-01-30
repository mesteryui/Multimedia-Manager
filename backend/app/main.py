from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Depends
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware
from core.db import create_db_and_tables, get_session
from models.media import Libro, Pelicula  # Importar para que SQLModel los reconozca


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Multimedia Manager API",
    description="API para gestión de series, libros y películas",
    version="0.1.0",
    lifespan=lifespan,
)

# Configuración CORS para permitir peticiones desde el frontend (cualquier origen por ahora)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a Multimedia Manager API. Visita /docs para ver la documentación."
    }


@app.get("/books/listAll")
def listar_todos_libros(session: Session = Depends(get_session)):
    return session.exec(select(Libro)).all()


@app.get("/books/{id}")
def listar_libro_por_id(id: int, session: Session = Depends(get_session)):
    return session.get(Libro, id)


@app.get("/books/libro_por_titulo/{titulo}")
def listar_libro_por_titulo(titulo: str, session: Session = Depends(get_session)):
    return session.exec(select(Libro).where(Libro.titulo == titulo)).all()


@app.post("/books/addLibro")
def add_libro(libro: Libro, session: Session = Depends(get_session)):
    session.add(libro)
    session.commit()
    return {"message": "Libro agregado correctamente"}


@app.delete("/books/deleteBook/{id}")
def delete_book_by_id(id: int, session: Session = Depends(get_session)):
    session.delete(session.get(Libro, id))
    session.commit()
    return {"message": "Libro eliminado correctamente"}


@app.post("/movies/addMovie")
def add_movie(movie: Pelicula, session: Session = Depends(get_session)):
    session.add(movie)
    session.commit()
    return {"message": "Pelicula agregada correctamente"}
