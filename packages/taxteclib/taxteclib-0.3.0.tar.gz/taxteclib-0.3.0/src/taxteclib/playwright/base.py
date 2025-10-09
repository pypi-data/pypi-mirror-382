from __future__ import annotations

import logging
from typing import Protocol


class LocatorProtocol(Protocol):
    async def click(self, *, timeout: int | None = None) -> object: ...

    async def fill(self, value: str, *, timeout: int | None = None) -> object: ...

    async def wait_for(self, *, state: str, timeout: int | None = None) -> object: ...

    async def is_visible(self) -> bool: ...

    async def inner_text(self) -> str: ...


class PageProtocol(Protocol):
    url: str

    async def goto(self, url: str, *, timeout: int | None = None) -> object: ...

    def get_by_role(self, role: str, name: str | None = None) -> LocatorProtocol: ...

    def get_by_label(self, label: str) -> LocatorProtocol: ...

    def get_by_text(self, text: str) -> LocatorProtocol: ...

    def locator(self, selector: str) -> LocatorProtocol: ...

    async def query_selector(self, selector: str) -> LocatorProtocol | None: ...

    async def wait_for_load_state(self, state: str, *, timeout: int | None = None) -> object: ...

    async def wait_for_selector(self, selector: str, *, timeout: int | None = None) -> LocatorProtocol: ...

    async def wait_for_function(self, expression: str, *, timeout: int | None = None) -> object: ...


class BasePlaywrightFlow:
    """Base class for reusable Playwright flows."""

    def __init__(
        self,
        page: PageProtocol | None,
        *,
        cliente: str,
        logger: logging.Logger | None = None,
        navigation_timeout: int = 180_000,
        interaction_timeout: int = 18_000,
        success_timeout: int = 60_000,
    ) -> None:
        if page is None:
            raise ValueError("Se requiere un objeto de página válido de Playwright.")
        if not cliente:
            raise ValueError("El identificador de cliente no puede estar vacío.")

        self.page = page
        self.cliente = cliente
        self.logger = logger or logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.navigation_timeout = navigation_timeout
        self.interaction_timeout = interaction_timeout
        self.success_timeout = success_timeout

    def set_timeouts(
        self,
        *,
        navigation: int | None = None,
        interaction: int | None = None,
        success: int | None = None,
    ) -> None:
        if navigation is not None:
            self.navigation_timeout = navigation
        if interaction is not None:
            self.interaction_timeout = interaction
        if success is not None:
            self.success_timeout = success

    def _log_debug(self, message: str, *args: object) -> None:
        if self.logger:
            self.logger.debug(message, *args)

    def _log_info(self, message: str, *args: object) -> None:
        if self.logger:
            self.logger.info(message, *args)

    def _log_warning(self, message: str, *args: object) -> None:
        if self.logger:
            self.logger.warning(message, *args)

    def _log_error(self, message: str, *args: object, exc_info: bool = False) -> None:
        if self.logger:
            self.logger.error(message, *args, exc_info=exc_info)
