# Plan de Implementación Backend: Gestión Completa (CRUD)

Este es el plan realista para tener un sistema **completamente funcional**. Para "gestionarlo todo", necesitas 4 operaciones básicas para cada tipo de contenido (Series, Películas, Libros).

En programación esto se llama **CRUD**:
- **C**reate (Crear): Añadir nuevo contenido.
- **R**ead (Leer): Ver qué tienes guardado.
- **U**pdate (Actualizar): Corregir errores o cambiar datos.
- **D**elete (Borrar): Eliminar lo que no quieras.

## 1. Gestión de Películas (`/movies`)
Implementaremos estos 5 endpoints (funciones):
- [ ] `POST /movies`: **Crear** una película nueva.
- [ ] `GET /movies`: **Leer (Listar)** todas las películas.
- [ ] `GET /movies/{id}`: **Leer** una sola película por su ID (para ver detalles).
- [ ] `PATCH /movies/{id}`: **Actualizar** datos de una película (ej. corregir el año).
- [ ] `DELETE /movies/{id}`: **Borrar** una película.

## 2. Gestión de Series (`/series`)
Idéntico a películas, pero con datos específicos de series (temporadas, etc.).
- [ ] `POST /series`
- [ ] `GET /series`
- [ ] `GET /series/{id}`
- [ ] `PATCH /series/{id}`
- [ ] `DELETE /series/{id}`

## 3. Gestión de Libros (`/books`)
- [ ] `POST /books`
- [X] `GET /books`
- [X] `GET /books/{id}`
- [ ] `PATCH /books/{id}`
- [ ] `DELETE /books/{id}`

## Estrategia de Código (Para no liarnos)
Para mantenerlo sencillo pero ordenado, no meteremos todo en un solo archivo gigante.
1.  Mantendremos los modelos en `app/models/media.py`.
2.  Crearemos un archivo nuevo `app/api.py` (o similar) para escribir estas funciones de forma limpia, o si prefieres, lo haremos en `main.py` pero usando comentarios grandes para separar secciones.

## Siguientes Pasos
Mi recomendación es implementar **primero todo el bloque de Películas**. Una vez que entiendas cómo hacer el CRUD de películas, hacer el de Series y Libros será copiar, pegar y cambiar 4 palabras.
