# Multimedia Manager

Sistema de gestión multimedia (Series, Libros, Películas) con arquitectura backend/frontend separada.

## Estructura

- `backend/`: API REST construida con **FastAPI** y **SQLModel**.
- `frontend/web_simple/`: Cliente web básico (HTML/JS).
- `docker-compose.yml`: Base de datos **PostgreSQL**.

## Inicio Rápido

### 1. Base de Datos
Necesitas Docker instalado.
```bash
docker-compose up -d
```
Esto levantará PostgreSQL en el puerto 5432.

### 2. Backend (API)
Se recomienda usar un entorno virtual.

```bash
cd backend
# Crear entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload
```
La API estará disponible en `http://localhost:8000`.
Documentación automática en `http://localhost:8000/docs`.

