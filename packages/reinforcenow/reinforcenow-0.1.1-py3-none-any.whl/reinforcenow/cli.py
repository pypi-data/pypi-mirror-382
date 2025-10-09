# cli.py
# ReinforceNow CLI with non-blocking login by default and clear UX

import base64
import json
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

import click
import requests
from dotenv import load_dotenv

from reinforcenow.auth import (
    is_authenticated,
    get_auth_headers,
    login_flow,
    validate_token,
    TOKEN_FILE,
    begin_device_login,
    finish_device_login,
)
from reinforcenow.utils import stream_sse_response

# Load .env from current working directory (optional - has defaults)
load_dotenv()

# Configuration with production default (can be overridden via .env)
API_URL = os.getenv("API_URL", "http://api.reinforcenow.ai")


def get_template_dir():
    """Get the path to the bundled templates directory"""
    return Path(__file__).parent / "templates"


def _not_logged_in_exit(open_browser: bool = True) -> None:
    """
    Standardized behavior for commands that require auth:
    - Tell the user they must log in
    - Open the device authorization page (non-blocking)
    - Exit with code 1
    """
    click.echo("🔒 Not authenticated.")
    if open_browser:
        pending = begin_device_login()
        if pending:
            click.echo("🌐 Opened the authorization page in your browser (or copy the link shown).")
            click.echo("   After approving, run the command again or `reinforcenow login --wait` to finish.")
        else:
            click.echo("⚠️ Could not start the login flow. Please run `reinforcenow login`.")
    else:
        click.echo("Please run `reinforcenow login` to authenticate.")
    sys.exit(1)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--wait/--no-wait", default=False, help="Poll until authorization completes (blocking). Default: no-wait.")
@click.option("--force", is_flag=True, help="Ignore existing session and start a fresh login.")
def login(wait: bool, force: bool):
    """
    Start the device login flow. By default, we open the browser and return immediately.
    Use --wait to block until authorization completes.
    """
    try:
        code = login_flow(wait=wait, force=force)
        sys.exit(code)
    except Exception as e:
        click.echo(f"❌ Login failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--finish/--no-finish", default=True, help="Try to finish an in-progress device login (one-shot, non-blocking).")
@click.option("--wait", is_flag=True, help="Finish login and wait until authorization completes.")
def status(finish: bool, wait: bool):
    """Check authentication status and (optionally) finish any in-progress device login."""
    if TOKEN_FILE.exists():
        click.echo("🔍 Checking authentication status...")
        valid = validate_token()
        if valid:
            click.echo(" ✅ Authenticated - token appears valid")

            # Show token file and decoded expiry (best-effort JWT inspection)
            try:
                with open(TOKEN_FILE) as f:
                    data = json.load(f)
                access_token = data.get("access_token", "")
                click.echo(f" 🗂  Token file: {TOKEN_FILE}")

                if "." in access_token:
                    try:
                        parts = access_token.split(".")
                        if len(parts) >= 2:
                            payload = parts[1] + "=" * (-len(parts[1]) % 4)
                            decoded = base64.urlsafe_b64decode(payload.encode("utf-8"))
                            token_data = json.loads(decoded.decode("utf-8"))
                            if "exp" in token_data:
                                exp_timestamp = token_data["exp"]
                                exp_date = datetime.fromtimestamp(exp_timestamp)
                                click.echo(f" ⏳ Token expires: {exp_date}")
                    except Exception:
                        pass
            except Exception as e:
                click.echo(f"  ⚠️  Could not read token details: {e}")
        else:
            click.echo(" ❌ Not authenticated - token invalid or expired")
    else:
        click.echo(" 🔒 Not authenticated - no token found")

    # Optionally try to finish any pending device login
    if finish:
        rc = finish_device_login(wait=wait)
        if rc == 0:
            click.echo(" ✅ Session ready.")
        else:
            click.echo(" ℹ️  If you just approved in the browser, re-run with `--wait` to complete here.")


@cli.command()
def logout():
    """Clear authentication token."""
    if TOKEN_FILE.exists():
        try:
            TOKEN_FILE.unlink()
            click.echo("✅ Successfully logged out (token removed).")
        except Exception as e:
            click.echo(f"⚠️  Could not remove token file: {e}")
    else:
        click.echo("ℹ️  Already logged out - no token found.")


@cli.command()
def start():
    """Initialize a new project with template files."""
    project_dir = Path("./project")
    template_dir = get_template_dir()

    # Create project directory
    project_dir.mkdir(exist_ok=True)

    # List of template files to copy
    template_files = [
        "tools.py",
        "env.py",
        "reward.py",
        "project.toml",
        "config.json",
        "dataset.json",
    ]

    click.echo("📦 Initializing new project with template files...")

    success_count = 0
    failed_files = []

    for filename in template_files:
        source = template_dir / filename
        destination = project_dir / filename

        try:
            shutil.copy2(source, destination)
            click.echo(f"  ✓ Created {filename}")
            success_count += 1
        except FileNotFoundError:
            click.echo(f"  ✗ Template not found: {filename}")
            failed_files.append(filename)
        except Exception as e:
            click.echo(f"  ✗ Error copying {filename}: {e}")
            failed_files.append(filename)

    # Summary
    click.echo(f"\n✨ Project initialized!")
    click.echo(f"   Successfully created: {success_count}/{len(template_files)} files")

    if failed_files:
        click.echo(f"   Failed to create: {', '.join(failed_files)}")
    else:
        click.echo(f"   All files created successfully!")
        click.echo(f"   Files are available in: ./project/")
        click.echo(f"\n📝 Next steps:")
        click.echo(f"   1. Edit the files in ./project/ to customize your RL environment")
        click.echo(f"   2. Run 'reinforcenow run' to start training")


def _ensure_auth_or_launch_login() -> None:
    """
    For commands that require auth: if not authenticated,
    open the auth page and exit immediately (non-blocking).
    """
    if is_authenticated():
        return
    _not_logged_in_exit(open_browser=True)


@cli.command()
@click.option("--project_name", required=False)
@click.option("--project_id", required=False)
def pull(project_name, project_id):
    _ensure_auth_or_launch_login()

    payload = {"project_name": project_name, "project_id": project_id}
    try:
        response = requests.post(f"{API_URL}/pull", json=payload, headers=get_auth_headers(), stream=True, timeout=300)
    except requests.RequestException as e:
        click.echo(f"❌ Network error: {e}")
        sys.exit(1)

    stream_sse_response(response)


@cli.command()
@click.argument("params", nargs=-1)
def run(params):
    _ensure_auth_or_launch_login()

    payload = {
        "files": {},
        "params": dict(p.split("=", 1) for p in params if "=" in p),
    }

    # Read files from project directory
    for fname in ["tools.py", "env.py", "reward.py", "project.toml", "config.json", "dataset.json"]:
        file_path = f"./project/{fname}"
        try:
            with open(file_path, "r") as f:
                payload["files"][fname] = f.read()
        except FileNotFoundError:
            click.echo(f" File not found: {file_path}")
            click.echo(" Run 'reinforcenow start' first to initialize project template files.")
            sys.exit(1)
        except Exception as e:
            click.echo(f" Error reading {file_path}: {e}")
            sys.exit(1)

    try:
        response = requests.post(f"{API_URL}/run", json=payload, headers=get_auth_headers(), stream=True, timeout=300)
    except requests.RequestException as e:
        click.echo(f"❌ Network error: {e}")
        sys.exit(1)

    stream_sse_response(response)


@cli.command()
@click.option("--run_id", required=True)
def stop(run_id):
    _ensure_auth_or_launch_login()

    try:
        response = requests.post(f"{API_URL}/stop", json={"run_id": run_id}, headers=get_auth_headers(), timeout=60)
        click.echo(response.text)
    except requests.RequestException as e:
        click.echo(f"❌ Network error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
