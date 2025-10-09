import os

import pytest
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from taxteclib.playwright.afip import AfipLoginFlow

pytestmark = pytest.mark.asyncio


# Test de integración real: valida que el login no lanza excepciones con credenciales válidas
@pytest.mark.asyncio
async def test_afip_login_no_exceptions() -> None:
    load_dotenv()
    cuit = os.getenv("CUIT")
    clave_fiscal = os.getenv("CLAVE_FISCAL")
    assert cuit and clave_fiscal, "Debes definir CUIT y CLAVE_FISCAL en el archivo .env"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        flow = AfipLoginFlow(
            page=page,
            cliente="ACME",
            cuit=cuit,
            clave_fiscal=clave_fiscal,
        )
        await flow.login(success_selector="#buscadorInput")
        await browser.close()
