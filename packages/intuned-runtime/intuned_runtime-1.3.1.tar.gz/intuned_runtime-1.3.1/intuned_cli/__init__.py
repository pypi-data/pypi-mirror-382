import os
import sys

import arguably
from dotenv import find_dotenv
from dotenv import load_dotenv

from intuned_cli.utils.console import console
from intuned_cli.utils.error import CLIError
from intuned_cli.utils.error import log_automation_error
from runtime.context.context import IntunedContext
from runtime.errors.run_api_errors import RunApiError

from . import commands


def run():
    dotenv = find_dotenv(usecwd=True)
    if dotenv:
        load_dotenv(dotenv, override=True)
        from runtime.env import cli_env_var_key

        os.environ[cli_env_var_key] = "true"
        os.environ["RUN_ENVIRONMENT"] = "AUTHORING"

        if not os.environ.get("FUNCTIONS_DOMAIN"):
            from intuned_cli.utils.backend import get_base_url

            os.environ["FUNCTIONS_DOMAIN"] = get_base_url().replace("/$", "")
    try:
        with IntunedContext():
            arguably.run(name="intuned")
            sys.exit(0)
    except CLIError as e:
        if e.auto_color:
            console.print(f"[bold red]{e.message}[/bold red]")
        else:
            console.print(e.message)
    except RunApiError as e:
        log_automation_error(e)
    except KeyboardInterrupt:
        console.print("[bold red]Aborted[/bold red]")
    except Exception as e:
        console.print(
            f"[red][bold]An error occurred: [/bold]{e}\n[bold]Please report this issue to the Intuned team.[/bold]"
        )
    sys.exit(1)


__all__ = ["commands", "run"]
