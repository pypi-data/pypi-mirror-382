import os

from intuned_cli.utils.error import CLIError
from runtime.types import IntunedJson


def get_base_url():
    return os.environ.get("INTUNED_API_BASE_URL") or os.environ.get("INTUNED_API_DOMAIN") or "https://app.intuned.io"


async def get_intuned_api_auth_credentials(
    *, intuned_json: IntunedJson, workspace_id: str | None, api_key: str | None
) -> tuple[str, str]:
    """
    Retrieves the Intuned API authentication credentials from environment variables.

    Returns:
        tuple: A tuple containing the workspace ID and API key.
    """
    workspace_id = workspace_id or intuned_json.workspace_id
    api_key = api_key or os.environ.get("INTUNED_API_KEY")

    if not workspace_id:
        raise CLIError("Workspace ID is required. Please provide it via command line options or Intuned.json")

    if not api_key:
        raise CLIError(
            "API key is required. Please provide it via command line options or INTUNED_API_KEY environment variable."
        )

    return workspace_id, api_key
