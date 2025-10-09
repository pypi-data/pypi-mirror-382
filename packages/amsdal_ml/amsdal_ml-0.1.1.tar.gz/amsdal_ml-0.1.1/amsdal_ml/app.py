from __future__ import annotations

from typing import TYPE_CHECKING

# During type checking, point to the known-available fallback.
if TYPE_CHECKING:
    from amsdal.contrib.app_config import AppConfig as BaseAppConfig
else:
    try:
        # At runtime prefer the real AMSDAL core if present.
        from amsdal.configs.app import AppConfig as BaseAppConfig  # type: ignore[import-not-found]
    except Exception:  # pragma: no cover
        from amsdal.contrib.app_config import AppConfig as BaseAppConfig


class MLPluginAppConfig(BaseAppConfig):
    name = "amsdal_ml"
    verbose_name = "AMSDAL ML Plugin"

    def on_ready(self) -> None:
        pass

    def on_server_startup(self) -> None:
        pass
