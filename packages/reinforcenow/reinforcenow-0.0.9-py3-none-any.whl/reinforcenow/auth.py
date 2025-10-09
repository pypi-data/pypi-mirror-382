import os
import time
import json
import webbrowser
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env from current working directory (optional - has defaults)
load_dotenv()

# Configuration with production defaults (can be overridden via .env)
BASE_URL = os.getenv("REINMAX_BASE_URL", "https://www.reinforcenow.ai").rstrip("/")
CLIENT_ID = os.getenv("REINMAX_CLIENT_ID", "better-auth-cli")
USER_AGENT = os.getenv("REINMAX_USER_AGENT", "Reinmax-CLI/1.0")
DEVICE_AUTH_URL = os.getenv("REINMAX_DEVICE_AUTH_URL", f"{BASE_URL}/api/auth/device/code")
TOKEN_URL = os.getenv("REINMAX_TOKEN_URL", f"{BASE_URL}/api/auth/device/token")

TOKEN_FILE = Path.home() / ".reinmax" / "token.json"


def _require_env():
    """Environment variables are now optional with defaults"""
    pass


def login_flow():
    _require_env()

    # Request device code
    resp = requests.post(
        DEVICE_AUTH_URL,
        data={"client_id": CLIENT_ID, "scope": "openid profile email offline_access"},
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": USER_AGENT},
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Device authorization failed: {resp.text}")
    payload = resp.json()

    device_code = payload["device_code"]
    user_code = payload["user_code"]
    verification_uri = payload["verification_uri"]
    verification_uri_complete = payload.get("verification_uri_complete")
    interval = int(payload.get("interval", 5))
    expires_in = int(payload.get("expires_in", 600))

    print("\n🔐 To log in:")
    print(f"   👉 Open: {verification_uri}")
    print(f"   🧾 Enter code: {user_code}\n")

    try:
        webbrowser.open(verification_uri_complete or verification_uri)
    except Exception:
        pass

    # 2) Poll for token
    print("⏳ Waiting for authorization...")
    start = time.time()
    current_interval = interval

    while time.time() - start < expires_in:
        # Debug: show what we're sending
        token_request_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
            "client_id": CLIENT_ID,
        }

        tok = requests.post(
            TOKEN_URL,
            data=token_request_data,
            headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": USER_AGENT},
            timeout=30,
        )

        # Debug output
        if tok.status_code != 200 and tok.status_code != 400:
            print(f"Debug: Token URL: {TOKEN_URL}")
            print(f"Debug: Request data: {token_request_data}")
            print(f"Debug: Response status: {tok.status_code}")
            print(f"Debug: Response body: {tok.text}")

        if tok.status_code == 200:
            token_data = tok.json()
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_FILE, "w") as f:
                json.dump(token_data, f)
            print("✅ Login successful!\n")
            return

        try:
            err_data = tok.json()
            err = err_data.get("error")
        except Exception:
            err = None
            err_data = None

        if err == "authorization_pending":
            time.sleep(current_interval)
            continue
        elif err == "slow_down":
            current_interval += 5
            time.sleep(current_interval)
            continue
        elif err == "access_denied":
            raise RuntimeError("❌ Access denied by user.")
        elif err in ("expired_token", "invalid_grant"):
            raise RuntimeError(f"❌ Device code expired/invalid: {tok.text}")
        else:
            # Debug output for unknown errors
            print(f"⚠️  Unexpected response (status {tok.status_code}): {tok.text}")
            if err_data:
                print(f"   Error data: {err_data}")
            time.sleep(current_interval)
            continue

    raise TimeoutError("⏱ Login timed out. Please run `reinmax login` again.")


def is_authenticated():
    """Check if user is authenticated with a valid token"""
    return TOKEN_FILE.exists() and validate_token()


def validate_token():
    """Validate the stored token by making a request to the auth server"""
    if not TOKEN_FILE.exists():
        return False
    
    try:
        with open(TOKEN_FILE) as f:
            data = json.load(f)
        
        access_token = data.get('access_token')
        if not access_token:
            return False
        
        # Make a request to validate the token
        # Using the Better Auth get-session endpoint to validate
        validation_url = f"{BASE_URL}/api/auth/get-session"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": USER_AGENT
        }
        
        resp = requests.get(validation_url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            # Token is valid
            return True
        elif resp.status_code == 401:
            # Token is invalid/expired - remove it
            TOKEN_FILE.unlink(missing_ok=True)
            return False
        else:
            # Other error - assume token might be valid but server has issues
            return True
            
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        # Token file is corrupted - remove it
        TOKEN_FILE.unlink(missing_ok=True)
        return False
    except requests.RequestException:
        # Network error - assume token is valid to avoid unnecessary re-auth
        return True
    except Exception:
        # Any other error - assume token is invalid
        TOKEN_FILE.unlink(missing_ok=True)
        return False


def get_auth_headers():
    if not TOKEN_FILE.exists():
        raise RuntimeError("Not authenticated. Run `reinmax login`.")
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    return {"Authorization": f"Bearer {data['access_token']}"}