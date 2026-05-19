# AulaTrack

Aplicacion de escritorio local para gestion de calificaciones escolares, pensada para uso offline por docentes.

## Stack

- Python
- PySide6
- SQLite

## Principios del proyecto

- 100% offline
- Simplicidad operativa
- Captura rapida con teclado
- UI moderna, ligera y consistente
- Arquitectura pequena pero escalable

## Estructura base

- `ui/`: ventanas, vistas y widgets reutilizables
- `database/`: conexion, esquema y repositorios futuros
- `models/`: entidades y estructuras tipadas
- `services/`: logica de negocio y calculos
- `themes/`: tokens visuales y estilos
- `assets/`: iconos e imagenes
- `docs/`: decisiones de arquitectura y producto

## Documentacion inicial

- [Arquitectura MVP](C:/Users/jona/Desktop/aulatrack/docs/architecture.md)
- [Esquema SQLite](C:/Users/jona/Desktop/aulatrack/database/schema.sql)

## Requisitos

- Python 3.11 o superior
- Windows con PowerShell

## Arranque rapido

La forma mas simple de probar la app es ejecutar:

```powershell
.\run.ps1
```

Ese script:

- crea `.venv` si no existe
- instala dependencias desde `requirements.txt`
- inicia la aplicacion

## Build para Windows

Para generar una carpeta distribuible con `AulaTrack.exe`:

```powershell
.\build.ps1
```

Ese script:

- reutiliza `.venv`
- instala `PyInstaller`
- empaqueta la app en `dist/AulaTrack/`
- incluye el esquema SQLite necesario para inicializar la base

Despues del build, el ejecutable queda en:

```text
dist/AulaTrack/AulaTrack.exe
```

En modo empaquetado, la app guarda sus datos y logs junto al ejecutable:

- `dist/AulaTrack/data/aulatrack.db`
- `dist/AulaTrack/data/logs/aulatrack.log`

## Arranque manual

Si prefieres hacerlo paso a paso:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Si en tu equipo no funciona `python`, intenta con:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py main.py
```

## Como revisar el MVP actual

1. Abre `Grupos` y crea uno o varios grupos.
2. Selecciona un grupo y agrega alumnos en el panel derecho.
3. Edita y elimina registros para validar el flujo CRUD.
4. Vuelve a `Dashboard` para confirmar que los indicadores cambian.

## Datos locales

- La base SQLite se guarda en [data/aulatrack.db](C:/Users/jona/Desktop/aulatrack/data/aulatrack.db)
- Si quieres reiniciar una prueba desde cero, cierra la app y elimina ese archivo
