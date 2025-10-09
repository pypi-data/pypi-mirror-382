import io
import json
import re
import uuid
from typing import Any

import httpx
import pathspec
import toml
from anyio import Path
from dotenv.main import DotEnv
from pydantic import BaseModel
from pydantic import ValidationError

from intuned_cli.types import DirectoryNode
from intuned_cli.types import FileNode
from intuned_cli.types import FileNodeContent
from intuned_cli.types import FileSystemTree
from intuned_cli.utils.api_helpers import load_intuned_json
from intuned_cli.utils.backend import get_base_url
from intuned_cli.utils.console import console
from intuned_cli.utils.error import CLIError
from intuned_cli.utils.exclusions import exclusions
from runtime.constants import api_key_header_name
from runtime.env import api_key_env_var_key
from runtime.env import project_env_var_key
from runtime.env import workspace_env_var_key

supported_playwright_versions = ["1.46.0", "1.52.0"]


class IntunedPyprojectToml(BaseModel):
    class _Tool(BaseModel):
        class _Poetry(BaseModel):
            dependencies: dict[str, Any]

        poetry: _Poetry

    tool: _Tool


async def validate_intuned_project():
    cwd = await Path().resolve()

    pyproject_toml_path = cwd / "pyproject.toml"

    if not await pyproject_toml_path.exists():
        raise CLIError("pyproject.toml file is missing in the current directory.")

    content = await pyproject_toml_path.read_text()
    json_content = toml.loads(content)
    try:
        pyproject_toml = IntunedPyprojectToml.model_validate(json_content)
    except Exception as e:
        raise CLIError(f"Failed to parse pyproject.toml: {e}") from e

    playwright_version = pyproject_toml.tool.poetry.dependencies.get("playwright")

    if playwright_version not in supported_playwright_versions:
        raise CLIError(
            f"Unsupported Playwright version '{playwright_version}'. "
            f"Supported versions are: {', '.join(supported_playwright_versions)}."
        )

    intuned_json = await load_intuned_json()

    api_folder = cwd / "api"
    if not await api_folder.exists() or not await api_folder.is_dir():
        raise CLIError("api directory does not exist in the current directory.")

    if intuned_json.auth_sessions.enabled:
        auth_sessions_folder = cwd / "auth-sessions"
        if not await auth_sessions_folder.exists() or not await auth_sessions_folder.is_dir():
            raise CLIError("auth-sessions directory does not exist in the api directory.")

    return intuned_json


def validate_project_name(project_name: str):
    if len(project_name) > 50:
        raise CLIError("Project name must be 50 characters or less.")

    project_name_regex = r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$"
    if not re.match(project_name_regex, project_name):
        raise CLIError("Project name can only contain lowercase letters, numbers, hyphens, and underscores in between.")

    try:
        import uuid

        uuid.UUID(project_name)
        raise CLIError("Project name cannot be a UUID.")
    except ValueError:
        # Not a valid UUID, continue
        pass


async def get_file_tree_from_project(path: Path, *, exclude: list[str] | None = None):
    # Create pathspec object for gitignore-style pattern matching
    spec = None
    if exclude:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", exclude)

    async def traverse(current_path: Path, tree: FileSystemTree):
        async for entry in current_path.iterdir():
            relative_path_name = entry.relative_to(path).as_posix()
            basename = entry.name

            # Check if this path should be excluded
            if spec and spec.match_file(relative_path_name):
                continue

            if await entry.is_dir():
                subtree = FileSystemTree(root={})
                tree.root[basename] = DirectoryNode(directory=subtree)
                # For directories, check if the directory itself is excluded
                # If not excluded, traverse into it
                await traverse(entry, subtree)
            elif await entry.is_file():
                tree.root[basename] = FileNode(file=FileNodeContent(contents=await entry.read_text()))

    results = FileSystemTree(root={})
    await traverse(path, results)
    return results


def mapFileTreeToIdeFileTree(file_tree: FileSystemTree):
    """
    Maps the file tree to IDE parameters format by processing parameters directory
    and converting it to ____testParameters structure.
    """

    if not file_tree:
        return

    parameters_node = file_tree.root.get("parameters")
    if parameters_node is None:
        return

    if not isinstance(parameters_node, DirectoryNode):
        return

    api_parameters_map: dict[str, list[dict[str, Any]]] = {}
    cli_parameters = list(parameters_node.directory.root.keys())
    test_parameters = DirectoryNode(directory=FileSystemTree(root={}))

    for parameter_key in cli_parameters:
        # If parameter of type directory, discard it and continue
        parameter = parameters_node.directory.root[parameter_key]

        if isinstance(parameter, DirectoryNode):
            continue

        if not parameter.file.contents.strip():
            continue

        try:
            parameter_payload = json.loads(parameter.file.contents)
        except json.JSONDecodeError:
            continue

        if "__api-name" not in parameter_payload:
            continue

        api = parameter_payload["__api-name"]
        # Create parameter value by excluding __api-name
        parameter_value = {k: v for k, v in parameter_payload.items() if k != "__api-name"}

        test_parameter: dict[str, Any] = {
            "name": parameter_key.replace(".json", ""),
            "lastUsed": False,
            "id": str(uuid.uuid4()),
            "value": json.dumps(parameter_value),
        }

        if api not in api_parameters_map:
            api_parameters_map[api] = []
        api_parameters_map[api].append(test_parameter)

    for api, parameters in api_parameters_map.items():
        # By default, last one used is the last one in the map
        if len(parameters) > 0:
            parameters[-1]["lastUsed"] = True

        test_parameters.directory.root[f"{api}.json"] = FileNode(
            file=FileNodeContent(contents=json.dumps(parameters, indent=2))
        )

    del file_tree.root["parameters"]
    file_tree.root["____testParameters"] = test_parameters


class SaveProjectResponse(BaseModel):
    id: str


async def save_project(
    *,
    project_name: str,
    workspace_id: str,
    api_key: str,
):
    base_url = get_base_url()
    url = f"{base_url}/api/v1/workspace/{workspace_id}/projects/{project_name}"
    print(f"calling {url}")
    headers = {
        api_key_header_name: api_key,
        "Content-Type": "application/json",
    }
    cwd = await Path().resolve()
    file_tree = await get_file_tree_from_project(cwd, exclude=exclusions)
    mapFileTreeToIdeFileTree(file_tree)

    payload: dict[str, Any] = {
        "codeTree": file_tree.model_dump(mode="json"),
        "platformType": "CLI",
        "language": "python",
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=payload)
        if response.status_code < 200 or response.status_code >= 300:
            if response.status_code == 401:
                raise CLIError("Invalid API key. Please check your API key and try again.")

            raise CLIError(
                f"[red bold]Invalid response from server:[/red bold]\n [bright_red]{response.status_code} {response.text}[/bright_red][red bold]\nProject save failed.[/red bold]"
            )

    console.print("[green]Project saved successfully.[/green]")
    try:
        response = SaveProjectResponse.model_validate(response.json())
    except ValidationError:
        console.print(f"[yellow]Could not parse response:[/yellow]\n {response.text}")
        return

    dotenv_path = cwd / ".env"
    if not await dotenv_path.exists():
        content_to_write = f"""{workspace_env_var_key}={workspace_id}
{project_env_var_key}={response.id}
{api_key_env_var_key}={api_key}
"""
        await dotenv_path.write_text(content_to_write)
        console.print("[green]Created .env with project credentials.[/green]")
        return

    dotenv_content = await dotenv_path.read_text()
    dotenv = DotEnv(
        dotenv_path=None,
        stream=io.StringIO(dotenv_content),
    ).dict()
    content_to_append = ""
    if dotenv.get(project_env_var_key) is None or dotenv.get(project_env_var_key) != response.id:
        content_to_append += f"{project_env_var_key}={response.id}"
    if dotenv.get(workspace_env_var_key) is None:
        content_to_append += f"\n{workspace_env_var_key}={workspace_id}"
    if dotenv.get(api_key_env_var_key) is None:
        content_to_append += f"\n{api_key_env_var_key}={api_key}"

    await dotenv_path.write_text(f"{dotenv_content}\n{content_to_append}\n")
    console.print("[green]Updated .env with project credentials.[/green]")
