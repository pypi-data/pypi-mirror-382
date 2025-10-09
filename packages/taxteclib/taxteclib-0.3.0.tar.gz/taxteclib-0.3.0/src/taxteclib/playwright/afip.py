from __future__ import annotations

import json
import logging

from .base import BasePlaywrightFlow, PageProtocol
from .exceptions import ConsultarNotificacionesError, LoginError, LoginErrorAfip


class AfipLoginFlow(BasePlaywrightFlow):
    """Encapsula el flujo de login en el portal de AFIP utilizando Playwright."""

    def __init__(
        self,
        *,
        page: PageProtocol | None,
        cliente: str,
        cuit: str,
        clave_fiscal: str,
        logger: logging.Logger | None = None,
    ) -> None:
        if not cuit:
            raise ValueError("El CUIT no puede estar vacío.")
        if not clave_fiscal:
            raise ValueError("La clave fiscal no puede estar vacía.")

        super().__init__(
            page,
            cliente=cliente,
            logger=logger,
        )
        self._cuit = cuit.strip()
        self._clave_fiscal = clave_fiscal

    async def login(
        self,
        URL_AFIP_LOGIN: str = "https://auth.afip.gob.ar/contribuyente_/login.xhtml",
        success_selector: str | None = None,
        success_url: str | None = None,
        success_title: str | None = None,
    ) -> None:
        """Realiza el inicio de sesión en AFIP replicando las validaciones habituales."""

        self._log_info("Iniciando login de AFIP para %s", self.cliente)

        try:
            await self.page.goto(URL_AFIP_LOGIN, timeout=self.navigation_timeout)

            spinbutton = self.page.get_by_role("spinbutton")
            await spinbutton.click(timeout=self.interaction_timeout)
            await spinbutton.fill(self._cuit, timeout=self.interaction_timeout)
            await self.page.get_by_role("button", name="Siguiente").click(timeout=self.interaction_timeout)

            incorrect_login = await self.page.query_selector(":has-text('Número de CUIL/CUIT incorrecto')")
            if incorrect_login:
                raise LoginErrorAfip(self.cliente, "Número de CUIL/CUIT incorrecto")

            await self.page.get_by_text("Ingresar con Clave Fiscal ").wait_for(
                state="visible",
                timeout=self.interaction_timeout,
            )

            captcha_locator = self.page.locator("div#captcha")
            if await captcha_locator.is_visible():
                raise LoginError(self.cliente, LoginError.CAPTCHA_DETECTADO)

            clave_locator = self.page.get_by_label("TU CLAVE")
            await clave_locator.click(timeout=self.interaction_timeout)
            await clave_locator.fill(self._clave_fiscal, timeout=self.interaction_timeout)

            await self.page.get_by_role("button", name="Ingresar").click(timeout=self.interaction_timeout)
            await self.page.wait_for_load_state(
                "networkidle",
                timeout=self.navigation_timeout,
            )

            error_locator = self.page.locator('form[name="F1"]:has-text("Clave o usuario incorrecto")')
            if await error_locator.is_visible():
                raise LoginErrorAfip(self.cliente)

            password_change_locator = self.page.get_by_text("Por medidas de seguridad tenés que cambiar tu contraseña")
            if await password_change_locator.is_visible():
                raise LoginErrorAfip(
                    self.cliente,
                    "Es necesario cambiar clave fiscal",
                )

            if self.page.url == URL_AFIP_LOGIN:
                error_selector = await self.page.query_selector("#F1\\:msg")
                if error_selector:
                    mensaje_error = await error_selector.inner_text()
                    raise LoginErrorAfip(self.cliente, mensaje_error.strip())

            await self._confirm_success(success_selector, success_url, success_title)
            self._log_info(
                "Login en AFIP finalizado correctamente para %s",
                self.cliente,
            )

        except LoginErrorAfip:
            self._log_error(
                "Error de login en AFIP para %s",
                self.cliente,
                exc_info=True,
            )
            raise
        except Exception as exc:  # pragma: no cover - se envuelve igualmente
            self._log_error(
                "Error inesperado durante el login de AFIP para %s: %s",
                self.cliente,
                exc_info=True,
            )
            raise ConsultarNotificacionesError(
                self.cliente,
                f"Error inesperado: {exc}",
            ) from exc

    async def _confirm_success(
        self,
        success_selector: str | None,
        success_url: str | None,
        success_title: str | None,
    ) -> None:
        if success_selector:
            await self.page.wait_for_selector(
                success_selector,
                timeout=self.success_timeout,
            )
            self._log_info(
                "Login en AFIP confirmado mediante selector: %s",
                success_selector,
            )
            return

        if success_url:
            fragment = json.dumps(success_url)
            await self.page.wait_for_function(
                f"window.location.href && window.location.href.includes({fragment})",
                timeout=self.success_timeout,
            )
            self._log_info(
                "Login en AFIP confirmado mediante URL que contiene: %s",
                success_url,
            )
            return

        if success_title:
            value = json.dumps(success_title)
            await self.page.wait_for_function(
                f"document.title && document.title.includes({value})",
                timeout=self.success_timeout,
            )
            self._log_info(
                "Login en AFIP confirmado mediante título que contiene: %s",
                success_title,
            )
            return

        raise LoginErrorAfip(
            self.cliente,
            "No se proporcionó un criterio válido para confirmar el login exitoso.",
        )
