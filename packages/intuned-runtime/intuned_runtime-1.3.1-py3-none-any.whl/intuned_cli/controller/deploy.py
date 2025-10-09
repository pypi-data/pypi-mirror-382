import asyncio
import time
from itertools import cycle
from typing import Literal

import httpx
from pydantic import BaseModel

from intuned_cli.controller.save import save_project
from intuned_cli.utils.backend import get_base_url
from intuned_cli.utils.console import console
from intuned_cli.utils.error import CLIError

supported_playwright_versions = ["1.46.0", "1.52.0"]

project_deploy_timeout = 10 * 60
project_deploy_check_period = 5


class DeployStatus(BaseModel):
    status: Literal["completed", "failed", "pending"]
    message: str | None = None
    reason: str | None = None


async def check_deploy_status(
    *,
    project_name: str,
    workspace_id: str,
    api_key: str,
):
    base_url = get_base_url()
    url = f"{base_url}/api/v1/workspace/{workspace_id}/projects/create/{project_name}/result"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code < 200 or response.status_code >= 300:
            if response.status_code == 401:
                raise CLIError("Invalid API key. Please check your API key and try again.")
            if response.status_code == 404:
                raise CLIError(f"Project '{project_name}' not found in workspace '{workspace_id}'.")
            raise CLIError(f"Failed to check deploy status for project '{project_name}': {response.text}")

    data = response.json()
    try:
        deploy_status = DeployStatus.model_validate(data)
    except Exception as e:
        raise CLIError(f"Failed to parse deploy status response: {e}") from e

    return deploy_status


async def deploy_project(
    *,
    project_name: str,
    workspace_id: str,
    api_key: str,
):
    await save_project(
        project_name=project_name,
        workspace_id=workspace_id,
        api_key=api_key,
    )
    base_url = get_base_url()
    url = f"{base_url}/api/v1/workspace/{workspace_id}/projects/{project_name}/deploy"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        if response.status_code < 200 or response.status_code >= 300:
            if response.status_code == 401:
                raise CLIError("Invalid API key. Please check your API key and try again.")

            raise CLIError(
                f"[red bold]Invalid response from server:[/red bold]\n [bright_red]{response.status_code} {response.text}[/bright_red][red bold]\nProject deployment failed.[/red bold]"
            )

    start_time = time.time()

    async def update_console():
        for spinner in cycle("⠙⠹⠸⠼⠴⠦⠧⠇"):
            await asyncio.sleep(0.05)

            time_elapsed_text = f"{time.time() - start_time:.1f}"
            print("\r", end="", flush=True)
            console.print(
                f"{spinner} [cyan]Deploying[/cyan] [bright_black]({time_elapsed_text}s)[/bright_black] ", end=""
            )

    if console.is_terminal:
        update_console_task = asyncio.create_task(update_console())
    else:
        update_console_task = None
        console.print("[cyan]Deploying[/cyan]")

    try:
        while True:
            await asyncio.sleep(project_deploy_check_period)
            if not console.is_terminal:
                time_elapsed_text = f"{time.time() - start_time:.1f}"
                console.print(f"[cyan]Deploying[/cyan] [bright_black]({time_elapsed_text}s)[/bright_black]")

            try:
                deploy_status = await check_deploy_status(
                    project_name=project_name,
                    workspace_id=workspace_id,
                    api_key=api_key,
                )

                if deploy_status.status == "pending":
                    elapsed_time = time.time() - start_time
                    if elapsed_time > project_deploy_timeout:
                        raise CLIError(f"Deployment timed out after {project_deploy_timeout//60} minutes.")
                    continue

                if deploy_status.status == "completed":
                    if update_console_task:
                        update_console_task.cancel()
                    if console.is_terminal:
                        print("\r", " " * 100)
                    console.print("[green][bold]Project deployed successfully![/bold][/green]")
                    console.print(
                        f"[bold]You can check your project on the platform:[/bold] [cyan underline]{get_base_url()}/projects/{project_name}/details[/cyan underline]"
                    )
                    return

                error_message = (
                    f"[red bold]Project deployment failed:[/bold red]\n{deploy_status.message or 'Unknown error'}\n"
                )
                if deploy_status.reason:
                    error_message += f"Reason: {deploy_status.reason}\n"
                error_message += "[red bold]Project deployment failed[/red bold]"
                raise CLIError(
                    error_message,
                    auto_color=False,
                )
            except Exception:
                if console.is_terminal:
                    print("\r", " " * 100)
                raise
    finally:
        if update_console_task:
            update_console_task.cancel()
