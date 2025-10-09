import logging
import os
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext

from runtime.context.context import IntunedContext
from runtime.env import get_functions_domain
from runtime.env import get_project_id
from runtime.env import get_workspace_id
from runtime.types import CaptchaSolverSettings
from runtime.utils.config_loader import load_intuned_json

logger = logging.getLogger(__name__)


def get_intuned_extension_path() -> Path | None:
    if "INTUNED_EXTENSION_PATH" not in os.environ:
        return None
    intuned_extension_path = Path(os.environ["INTUNED_EXTENSION_PATH"])
    if not intuned_extension_path.exists():
        return None
    return intuned_extension_path


def is_intuned_extension_enabled() -> bool:
    intuned_extension_path = get_intuned_extension_path()
    if intuned_extension_path is None:
        return False
    else:
        return True


async def get_intuned_worker(context: BrowserContext):
    if not is_intuned_extension_enabled():
        return None

    for attempt in range(5):
        for service_worker in context.service_workers:
            if "intunedWorker.js" in service_worker.url:
                return service_worker
        try:
            if attempt < 4:
                await context.wait_for_event("serviceworker", timeout=3000)
        except Exception as e:
            logger.warning(f"Error accessing service workers (attempt {attempt + 1}): {e}")

    logger.warning("Failed to get intuned worker after 5 attempts")
    return None


async def get_intuned_extension_settings() -> dict[str, Any]:
    intuned_json = await load_intuned_json()
    captcha_settings: CaptchaSolverSettings = (
        intuned_json.captcha_solver
        if intuned_json and intuned_json.captcha_solver is not None
        else CaptchaSolverSettings()
    )
    context = IntunedContext.current()
    return {
        **captcha_settings.model_dump(mode="json"),
        "workspaceId": get_workspace_id(),
        "projectId": get_project_id(),
        "token": context.functions_token,
        "baseUrl": get_functions_domain(),
    }


async def setup_intuned_extension():
    if not is_intuned_extension_enabled():
        return
    intuned_extension_path = get_intuned_extension_path()
    if intuned_extension_path is None:
        logger.warning("Intuned extension path not found, intuned extension might not work properly")
        return

    settings_path = intuned_extension_path / "intunedSettings.json"
    settings_data = await get_intuned_extension_settings()

    try:
        with open(settings_path, "w") as f:
            import json

            json.dump(settings_data, f)
    except Exception as e:
        logger.warning(f"Failed to write intuned settings to {settings_path}: {e}")
