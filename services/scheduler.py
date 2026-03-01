import asyncio
import logging

from services.sheets_manager import ensure_all_user_month_sheets

LOGGER = logging.getLogger(__name__)


async def daily_sheets_maintenance_task() -> None:
    while True:
        try:
            ensure_all_user_month_sheets()
        except Exception:
            LOGGER.exception('Daily month sheets maintenance failed')
        await asyncio.sleep(60 * 60 * 24)
