from __future__ import annotations

from typing import List, Optional

from ..client import AsyncCostManagerClient, CostManagerClient
from ..config_manager import ConfigManager, TriggeredLimit
from .base import BaseLimitManager


class TriggeredLimitManager(BaseLimitManager):
    """Manage triggered limits fetched from the API and stored locally."""

    def __init__(
        self,
        client: CostManagerClient | AsyncCostManagerClient,
        config_manager: ConfigManager | None = None,
    ) -> None:
        super().__init__(client)
        self.config_manager = config_manager or ConfigManager(client)

    def update_triggered_limits(self) -> None:
        data = self.client.get_triggered_limits() or {}
        if isinstance(data, dict):
            tl_data = data.get("triggered_limits", data)
        else:
            tl_data = data
        self.config_manager.write_triggered_limits(tl_data)

    async def update_triggered_limits_async(self) -> None:
        data = await self.client.get_triggered_limits() or {}
        if isinstance(data, dict):
            tl_data = data.get("triggered_limits", data)
        else:
            tl_data = data
        self.config_manager.write_triggered_limits(tl_data)

    def check_triggered_limits(
        self,
        api_key_id: str,
        service_key: Optional[str] = None,
        customer_key: Optional[str] = None,
    ) -> List[TriggeredLimit]:
        limits = self.config_manager.get_triggered_limits(
            service_key=service_key,
            customer_key=customer_key,
        )
        return [l for l in limits if l.api_key_id == api_key_id]
