# Guía Maestra: FastAPI + SQLModel (Multimedia Manager)

Esta documentación expandida está diseñada para darte un control total sobre tu proyecto. No solo explica el "cómo", sino el "por qué" de cada pieza, incluyendo patrones avanzados de validación y relaciones entre tablas.

---

## 1. Arquitectura del Proyecto: ¿Qué hace cada pieza?

Entender la arquitectura te ayudará a no perderte cuando el proyecto crezca.

### 🏛️ FastAPI: El Controlador de Tráfico
FastAPI no toca la base de datos directamente. Su trabajo es puramente **IO (Entrada/Salida)**.
*   **Routing**: Decide qué función de Python ejecutar basándose en la URL (`/books/`) y el método (`GET`, `POST`).
*   **Validación (Pydantic)**: Es el portero. Si dices que el `id` debe ser un entero y te mandan texto, FastAPI rechaza la petición antes de que tu código se ejecute.
*   **Serialización**: Convierte tus objetos complejos de Python (clases, fechas) en texto JSON que el navegador entiende.

### 🗄️ SQLModel: El Puente Híbrido
SQLModel es especial porque une dos mundos:
1.  **SQLAlchemy (ORM)**: Gestiona la conexión real con la DB, transacciones y consultas SQL.
2.  **Pydantic (Validación)**: Define la forma de los datos.
*Al heredar de `SQLModel`, tus clases sirven tanto para validar datos (FastAPI) como para crear tablas (Base de Datos).*

---

## 2. Validación de Esquemas (DTOs): El Patrón Profesional

Hasta ahora hemos usado una sola clase (`Libro`) para todo. Esto está bien para empezar, pero tiene problemas graves:
*   **Seguridad**: Permites que un usuario envíe un `id` en el JSON y sobrescriba tu base de datos.
*   **Privacidad**: Si tienes un campo `password` o `datos_privados` en tu tabla, no quieres enviarlo de vuelta al usuario al hacer un GET.

**La Solución: Modelos Separados (Data Transfer Objects)**
Usamos herencia para no repetir código, pero creamos "vistas" diferentes del mismo dato.

### El Patrón de Herencia

```python
# 1. BASE: Campos comunes que todos comparten
class LibroBase(SQLModel):
    titulo: str
    autor: str
    isbn: str

# 2. TABLE: La definición real de la Base de Datos
# Hereda de Base, añade el ID (porque solo la DB lo tiene) y table=True
class Libro(LibroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Aquí irían campos privados o internos que no ve el usuario
    notas_internas: Optional[str] = None 
    
    # Claves foráneas para relaciones (ver sección 3)
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")

# 3. CREATE: Lo que el usuario nos envía para crear
# Hereda de Base. No tiene ID (porque aún no existe).
class LibroCreate(LibroBase):
    pass 
    # Podrías añadir validaciones extra aquí, como password en texto plano

# 4. PUBLIC (READ): Lo que le mostramos al mundo
# Hereda de Base y añade el ID (porque ya existe).
# Excluye 'notas_internas' o 'password' automáticamente al no incluirlos.
class LibroPublic(LibroBase):
    id: int
```

### ¿Cómo se usa esto en `main.py`?
Observa cómo los tipos cambian en la función:

```python
@app.post("/books/", response_model=LibroPublic) # Devuelve el modelo Público
def create_book(book_in: LibroCreate, session: Session = Depends(get_session)):
    # 1. book_in es un LibroCreate (sin ID, seguro)
    
    # 2. Convertimos a modelo de Tabla
    # .model_validate() copia los campos coincidentes de uno a otro
    db_book = Libro.model_validate(book_in)
    
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    
    # 3. FastAPI convierte db_book (Tabla) a LibroPublic automáticamente
    return db_book 
```

---

## 3. Relaciones (Relationships): Conectando Tablas

En una app real, los datos están conectados. Un `Libro` pertenece a una `Categoria`, o un `Libro` tiene muchos `Comentarios`.

### Conceptos Clave
1.  **Foreign Key (FK)**: Es un campo numérico en la tabla (ej: `categoria_id`) que apunta al ID de otra tabla. Es el vínculo "físico".
2.  **relationship()**: Es un vínculo "mágico" a nivel de Python. Te permite acceder al objeto entero (`libro.categoria.nombre`) en lugar de solo ver el número ID.

### Ejemplo: Categoría y Libros (1 a N)

Una categoría tiene muchos libros. Un libro pertenece a una categoría.

#### Modelo `Categoria` (El lado "Uno")
```python
class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    
    # Relación inversa: "Busca en la clase Libro el campo 'categoria' y conéctate"
    libros: List["Libro"] = Relationship(back_populates="categoria")
```

#### Modelo `Libro` (El lado "Muchos")
```python
class Libro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    
    # 1. El vínculo físico (Foreign Key)
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    
    # 2. El vínculo Python (Relationship)
    # Popula este campo buscando la Categoria cuyo ID coincida con mi categoria_id
    categoria: Optional[Categoria] = Relationship(back_populates="libros")
```

### Usando Relaciones
¡Es automático! SQLModel hace los JOINS por ti cuando accedes a los atributos (lazy loading) o si lo pides explícitamente.

**Crear un libro con categoría:**
```python
def create_book_with_cat(session):
    categoria_ficcion = Categoria(nombre="Ficción")
    
    # Podemos asignar el objeto directo, SQLModel gestiona los IDs
    libro_nuevo = Libro(titulo="Dune", categoria=categoria_ficcion)
    
    session.add(libro_nuevo)
    session.commit() 
    # Esto guarda AMBOS: la categoría nueva y el libro.
```

**Leer datos relacionados:**
```python
# Obtener un libro y ver su categoría
libro = session.get(Libro, 1)
print(libro.categoria.nombre) # "Ficción"

# Obtener una categoría y ver sus libros
cat = session.get(Categoria, 1)
for libro in cat.libros:
    print(libro.titulo)
```

---

## 3.5. Casos Reales: Series y Secuelas

Aquí tienes cómo aplicaríamos esto específicamente para tus necesidades de Multimedia (Series y Películas).

### Jerarquía Completa: Serie -> Temporadas -> Capítulos
Aquí tenemos relaciones anidadas. Una `Serie` tiene `Temporadas`, y cada `Temporada` tiene `Capítulos`.

```python
class Serie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    
    # Serie tiene N Temporadas
    temporadas: List["Temporada"] = Relationship(back_populates="serie")

class Temporada(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: int     # Ej: 1
    titulo: str     # Ej: "Temporada 1: El inicio"
    
    # N Temporadas pertenecen a 1 Serie
    serie_id: Optional[int] = Field(default=None, foreign_key="serie.id")
    serie: Optional[Serie] = Relationship(back_populates="temporadas")

    # Temporada tiene N Capítulos
    capitulos: List["Capitulo"] = Relationship(back_populates="temporada")

class Capitulo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: int     # Ej: 1
    titulo: str     # Ej: "Piloto"
    duracion_minutos: int
    
    # N Capítulos pertenecen a 1 Temporada
    temporada_id: Optional[int] = Field(default=None, foreign_key="temporada.id")
    temporada: Optional[Temporada] = Relationship(back_populates="capitulos")
```

**Cómo consultar datos anidados:**
SQLModel (gracias a SQLAlchemy) permite navegar tan profundo como quieras.

```python
# Obtener una serie y ver todos sus capítulos organizados
serie = session.exec(select(Serie).where(Serie.titulo == "Breaking Bad")).first()

for temporada in serie.temporadas:
    print(f"Temporada {temporada.numero}")
    for capitulo in temporada.capitulos:
        print(f"  - Cap {capitulo.numero}: {capitulo.titulo}")
```

### Relación Película -> Secuela (Auto-referencia)
Esto es un poco más avanzado. ¿Cómo dices que "Dune 2" es la secuela de "Dune 1"? Ambas son filas en la misma tabla `Pelicula`.
Necesitamos que la tabla se apunte a sí misma.

```python
class Pelicula(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    
    # FK que apunta a "otra" fila de ESTA misma tabla
    # Si está vacío (None), es la primera película. Si tiene valor, es una secuela.
    precuela_id: Optional[int] = Field(default=None, foreign_key="pelicula.id")
    
    # Relación para acceder a la película anterior
    # remote_side es necesario en auto-referencias para decirle a SQLModel cuál es el ID al que apuntamos
    precuela: Optional["Pelicula"] = Relationship(
        back_populates="secuelas",
        sa_relationship_kwargs={"remote_side": "Pelicula.id"}
    )
    
    # Relación para acceder a la película siguiente (o lista de secuelas)
    secuelas: List["Pelicula"] = Relationship(back_populates="precuela")
```

**Uso:**
```python
# 1. Crear la original
dune_1 = Pelicula(titulo="Dune: Part One")
session.add(dune_1)
session.commit()
session.refresh(dune_1)

# 2. Crear la secuela apuntando a la original
dune_2 = Pelicula(titulo="Dune: Part Two", precuela=dune_1) 
# O también: precuela_id=dune_1.id
session.add(dune_2)
session.commit()

# 3. Navegar
print(dune_2.precuela.titulo) # "Dune: Part One"
print(dune_1.secuelas[0].titulo) # "Dune: Part Two"
```

---

## 4. Profundizando en `get_session` y Transacciones

```python
def get_session():
    with Session(engine) as session:
        yield session
```

### ¿Qué es `yield`?
Convierte la función en un **Generador**.
1.  **Entra petición**: FastAPI llama a `get_session`.
2.  **`with Session...`**: Se abre la conexión. Comienza una transacción.
3.  **`yield session`**: La función se *congela* aquí. Le presta la sesión a tu endpoint.
4.  **Tu Endpoint**: Usa la sesión. Si hay un error (excepción), salta.
5.  **Retorno (`finally`)**:
    *   Si todo fue bien en el endpoint, el código vuelve a `get_session` después del yield.
    *   Salimos del bloque `with`.
    *   **Automáticamente**: `session.close()`. La conexión vuelve al pool para ser reusada.

### `session.commit()` vs `session.flush()`
*   **`add()`**: "Anota esto en tu lista de tareas pendientes".
*   **`flush()`**: "Envía los comandos SQL a la base de datos (se generan IDs), pero **mantén la transacción abierta**". Los cambios aún no son definitivos y se pueden deshacer (rollback).
*   **`commit()`**: "Cierra la transacción. Haz los cambios permanentes y visibles para todos los demás usuarios". Llama a `flush()` automáticamente.

---

## 5. Recetario Avanzado de Consultas

SQLModel permite consultas complejas tipo SQL usando sintaxis Python.

### Filtrado (`WHERE`)
```python
# WHERE autor = 'Herbert' AND paginas > 300
statement = select(Libro).where(Libro.autor == "Frank Herbert", Libro.paginas_totales > 300)
resultados = session.exec(statement).all()
```

### Ordenación (`ORDER BY`) y Paginación (`LIMIT/OFFSET`)
```python
statement = (
    select(Libro)
    .order_by(Libro.fecha_publicacion.desc()) # Más recientes primero
    .offset(0)  # Saltar 0
    .limit(10)  # Traer 10
)
```

### Joins Explícitos
A veces quieres traer datos combinados en una sola consulta para eficiencia.
```python
# Traer Libros y sus Categorías juntos
statement = select(Libro, Categoria).join(Categoria)
results = session.exec(statement).all()
for libro, categoria in results:
    print(f"{libro.titulo} es de tipo {categoria.nombre}")
```
