from __future__ import annotations


class AutomationError(Exception):
    """Error base para automatizaciones con navegadores."""

    default_message = "Error en la automatización de navegador"

    def __init__(self, cliente: str | None = None, mensaje: str | None = None) -> None:
        self.cliente = cliente
        self.mensaje = mensaje or self.default_message
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        if self.cliente and self.mensaje:
            return f"[{self.cliente}] {self.mensaje}"
        return self.mensaje


class LoginError(AutomationError):
    """Representa errores genéricos de login en portales automatizados."""

    default_message = "Error durante el proceso de login"
    CAPTCHA_DETECTADO = "Se detectó un captcha en el portal de login"

    def __init__(self, cliente: str, mensaje: str | None = None) -> None:
        super().__init__(cliente, mensaje or self.default_message)


class LoginErrorAfip(LoginError):
    """Errores específicos del login en AFIP."""

    default_message = "Error durante el login en AFIP"

    def __init__(self, cliente: str, mensaje: str | None = None) -> None:
        super().__init__(cliente, mensaje or self.default_message)


class ConsultarNotificacionesError(AutomationError):
    """Error envoltorio para fallas inesperadas al consultar notificaciones."""

    default_message = "Error al consultar notificaciones"

    def __init__(self, cliente: str, mensaje: str | None = None) -> None:
        super().__init__(cliente, mensaje or self.default_message)
