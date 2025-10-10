# taxteclib

`taxteclib` es una librería Python que centraliza módulos y utilidades comunes para los proyectos de BPS Tax Tec (Argentina). Está pensada para contener funciones, clases y helpers reutilizables que faciliten la construcción de servicios y herramientas internas.

## Características

- Paquete ligero, compatible con Python 3.12
- Estructura lista para pruebas y CI
- Contiene utilidades comunes para la organización BPS Tax Tec ARG
- Helpers de automatización con Playwright listos para reutilizar en distintos proyectos


## Clases disponibles

En el paquete `taxteclib` actualmente están disponibles las siguientes clases principales:

- `SqlServerClient`: Cliente para insertar registros de monitoreo en SQL Server.
- `GithubRepoUpdater`: Clase para actualizar desde un repositorio de GitHub y aplicar SQLs de un ZIP.
- `AfipLoginFlow`: Helper asincrónico para automatizar el login en el portal de AFIP con Playwright.


Puedes consultar la documentación de cada clase en los archivos fuente dentro de `src/taxteclib/`.

### Ejemplo de uso: SqlServerClient

```python
from taxteclib.database_logger import SqlServerClient, EstadoMonitoreo
from datetime import datetime

cliente_db = SqlServerClient()
registro = cliente_db.insertar_monitoreo(
	username="usuario",
	proceso="Proceso de ejemplo",
	estado=EstadoMonitoreo.CORRECTO,
	iniciado=datetime(2025, 9, 25, 10, 0),
	finalizado=datetime(2025, 9, 25, 10, 15),
	cliente="Cliente",
	items_count=42,
)
print(f"Registro insertado con ID: {registro.id}")
```

### Ejemplo de uso: GithubRepoUpdater

```python
from taxteclib.github_updater import GithubRepoUpdater

updater = GithubRepoUpdater(owner="mi_owner", repo="mi_repo")
updater.update(extract_zip=True)
```

### Ejemplo de uso: Playwright AFIP login

```python
import asyncio
import logging
import os
from playwright.async_api import async_playwright
from taxteclib.playwright.afip import AfipLoginFlow
from taxteclib.playwright.exceptions import LoginErrorAfip
from dotenv import load_dotenv


async def main() -> None:
    load_dotenv()
    cuit = os.getenv("CUIT")
    clave_fiscal = os.getenv("CLAVE_FISCAL")
    if not cuit or not clave_fiscal:
        raise ValueError("Debes definir CUIT y CLAVE_FISCAL en el archivo .env")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        flow = AfipLoginFlow(
            page=page,
            cliente="ACME",
            cuit=cuit,
            clave_fiscal=clave_fiscal,
            logger=logging.getLogger("afip-login"),
        )

        try:
            await flow.login(success_selector="#buscadorInput")
        except LoginErrorAfip as exc:
            logging.error("Falló el login de AFIP: %s", exc)
        else:
            logging.info("Login correcto, continuar con el flujo deseado.")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
```

> **Tip:** Luego de instalar la librería, recordá ejecutar `playwright install` para descargar los navegadores necesarios.

## Instalación (desarrollo)

Recomendado: crear un entorno virtual y usar las utilidades del proyecto.

Con venv:

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
```

Si usas `uv` (opcional) y el Makefile del repo:

```pwsh
make local-setup
make install
```

## Uso básico

Ejemplo mínimo usando la clase de ejemplo incluida:

```python
from taxteclib.dummy_class import Dummy

dummy = Dummy()
assert dummy.add(2, 3) == 5
print('2 + 3 =', dummy.add(2, 3))
```


## Ejecutar pruebas

La suite de tests usa `pytest`. Para correrlas localmente:

```pwsh
# dentro del entorno virtual
make test
# o
pytest -q
```

### Tests que requieren credenciales

Algunos tests (por ejemplo, los de Playwright/AFIP) requieren credenciales reales y variables de entorno. Estos están marcados con `@pytest.mark.requires_credentials`.

Para ejecutar **solo los tests que no requieren credenciales** (por ejemplo, en CI o si no tienes acceso a AFIP):

```pwsh
make test-no-credentials
# o
pytest -m "not requires_credentials"
```

Para ejecutar **todos los tests** (incluyendo los que requieren credenciales):

```pwsh
make test
# o
pytest
```

Recuerda definir las variables necesarias en un archivo `.env` si ejecutas los tests que requieren credenciales.

## Contribuir

1. Crea una rama con un nombre descriptivo
2. Asegúrate de pasar los hooks y tests locales (`make local-setup`)
3. Envía un Pull Request contra `main`

Para estilos y checks el repo incluye `ruff` y hooks de pre-commit.

## Licencia

Consulta el archivo `LICENSE` del repositorio para detalles.