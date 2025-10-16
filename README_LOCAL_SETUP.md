docker compose up -d db
Guía rápida — Moverly Backend (Windows PowerShell)

1) Levantar la base de datos con Docker

```powershell
# Levantar solo el servicio de PostgreSQL
docker compose up -d db
```

2) Crear y activar el entorno virtual

```powershell
python -m venv .\venv
.\venv\Scripts\Activate.ps1
```

3) Instalar dependencias

```powershell
pip install -r requirements.txt
```

4) Ejecutar migraciones (Alembic)

```powershell
.\venv\Scripts\python.exe -m alembic upgrade head
```

5) Poblar datos de ejemplo (opcional)

```powershell
.\venv\Scripts\python.exe scripts\seed_data.py
```

6) Ejecutar la aplicación

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
# Abrir la documentación Swagger en el navegador
Start-Process 'http://127.0.0.1:8000/docs'
```

Si quieres, puedo añadir scripts de PowerShell para automatizar estos pasos.