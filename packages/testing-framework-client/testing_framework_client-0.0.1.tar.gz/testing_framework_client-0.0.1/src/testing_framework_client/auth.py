import json
from colorama import Fore
import os
import subprocess
import time
import webbrowser
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
import shutil
import sys

import requests
from dotenv import load_dotenv
from .printing import (
    print_instruction,
    print_error,
    print_success,
    print_warning,
    print_info,
    print_title,
)

load_dotenv()

TOKEN_FILE = Path(".tf_client_tokens.json")


# --- Helper Functions ---
def open_file_in_editor(file_path: Path):
    """
    Opens a file using $EDITOR, falling back to VS Code or the system default opener.
    """

    def try_open(cmd, description):
        try:
            print_info(f"Opening {file_path} with {description}...")
            subprocess.run(cmd, check=True)
            return True
        except FileNotFoundError:
            print_error(f"{description} not found.")
        except subprocess.CalledProcessError as e:
            print_error(f"{description} exited with an error: {e}")
        except Exception as e:
            print_error(f"Unexpected error using {description}: {e}")
        return False

    editor = os.environ.get("EDITOR")

    # 1. $EDITOR
    if editor and try_open([editor, str(file_path)], f"$EDITOR ({editor})"):
        return

    # 2. VS Code
    if shutil.which("code") and try_open(["code", str(file_path)], "VS Code"):
        return

    # 3. System default
    if sys.platform.startswith("darwin"):
        try_open(["open", str(file_path)], "macOS default opener")
    elif os.name == "nt":
        print_info(f"Opening {file_path} with Windows default application...")
        try:
            os.startfile(str(file_path))  # type: ignore[attr-defined]
        except Exception as e:
            print_error(f"Failed to open {file_path}: {e}")
    else:
        try_open(["xdg-open", str(file_path)], "system default opener")


# --- Data Class for Token ---
@dataclass
class Token:
    """Represents an OAuth token with automatic expiration tracking."""

    access_token: str
    expires_in: int
    refresh_token: Optional[str] = None
    refresh_expires_in: Optional[int] = None

    # These fields are calculated automatically after initialization.
    expiry_in_absolute: float = field(init=False, default=0.0)
    refresh_expires_in_absolute: float = field(init=False, default=0.0)

    def __post_init__(self):
        """Calculate absolute expiration timestamps after the object is created."""
        current_time = time.time()
        self.expiry_in_absolute = current_time + self.expires_in
        if self.refresh_expires_in:
            self.refresh_expires_in_absolute = current_time + self.refresh_expires_in

    @classmethod
    def from_json_file(cls, path: Path) -> Optional["Token"]:
        """Loads a token from a JSON file, returning None if it fails."""
        if not path.exists():
            return None

        try:
            json_data = json.loads(path.read_text())
            return cls(**json_data)
        except (json.JSONDecodeError, TypeError) as e:
            print_error(f"Failed to parse token file '{path}': {e}")
            return None

    def to_json_file(self, path: Path):
        """Saves the token to a file as nicely formatted JSON."""
        # print(f"Saving token to {path}")
        path.write_text(json.dumps(asdict(self), indent=2))

    def is_expired(self) -> bool:
        """Checks if the access token is expired."""
        return time.time() >= self.expiry_in_absolute

    def is_refresh_expired(self) -> bool:
        """Checks if the refresh token is expired or doesn't exist."""
        if not self.refresh_token or not self.refresh_expires_in_absolute:
            return True
        return time.time() >= self.refresh_expires_in_absolute


# --- Main Authentication Client ---
class AuthClient:
    """Handles OAuth flow, token storage, and authenticated API requests."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("TESTING_FRAMEWORK_BASE_URL")
        if not self.base_url:
            raise ValueError(
                "TESTING_FRAMEWORK_BASE_URL must be set via parameter or in a .env file"
            )
        self.token: Optional[Token] = self._load_token()

    def _load_token(self) -> Optional[Token]:
        """Loads the token from the default file on initialization."""
        # print(f"Attempting to load token from {TOKEN_FILE}")
        token = Token.from_json_file(TOKEN_FILE)
        if token:
            print_info("Successfully loaded token from file.")
        else:
            print_info("No valid token file found.")
        return token

    def _save_and_set_token(self, token_data: dict):
        """Creates a Token instance from a dictionary, saves it, and sets it."""
        try:
            self.token = Token(**token_data)
            self.token.to_json_file(TOKEN_FILE)
            print_info("New token has been successfully stored.")
        except TypeError as e:
            print_instruction(
                f"Failed to create Token from server data. Missing required keys: {e}"
            )
            self.token = None

    def _fetch_token_via_browser(self):
        """Guides the user through the manual browser-based token retrieval process."""
        input(
            Fore.BLUE
            + "\nToken is missing or expired. Press Enter to open your browser to log in..."
        )

        auth_url = f"{self.base_url}/public/auth-token"
        print_info(f"Opening browser to: {auth_url}")
        webbrowser.open(auth_url)

        print_title("\n--- ACTION REQUIRED ---")
        print_instruction("1. Log in in your browser.")
        print_instruction("2. You will be redirected to a page with a JSON response.")
        print_instruction("3. Copy the entire JSON object.")
        input(
            Fore.BLUE
            + f"4. Press Enter here to open '{TOKEN_FILE}' in your editor to paste the JSON..."
        )

        # Prepare the token file for pasting.
        TOKEN_FILE.write_text("")
        open_file_in_editor(TOKEN_FILE)

        while True:
            input("Press Enter after you have saved the JSON content in the file...")
            token_candidate = Token.from_json_file(TOKEN_FILE)
            if token_candidate:
                self.token = token_candidate
                print_info("Token successfully read from file.")
                break
            else:
                print_warning(
                    f"File '{TOKEN_FILE}' is empty or contains invalid JSON. Please check the file and try again."
                )

    def _refresh_token(self):
        """
        Refreshes the access token using the refresh token.
        Falls back to the browser flow if refreshing fails.
        """
        if not self.token or not self.token.refresh_token:
            print_warning("No refresh token available. Triggering browser login.")
            self._fetch_token_via_browser()
            return

        print_info("Attempting to refresh the access token...")
        try:
            resp = requests.post(
                f"{self.base_url}/public/auth-token/refresh",
                data={"refresh_token": self.token.refresh_token},
                timeout=10,
            )

            if resp.status_code in (400, 401):
                print_warning(
                    "Refresh token is invalid or expired. Starting new browser login."
                )
                self._fetch_token_via_browser()
                return

            resp.raise_for_status()
            self._save_and_set_token(resp.json())

        except requests.RequestException as e:
            print_error(f"Failed to refresh token due to a network error: {e}")
            print_info("Falling back to browser-based authentication.")
            self._fetch_token_via_browser()

    def _ensure_valid_token(self):
        """
        Guarantees a valid token is present, fetching or refreshing as needed.
        This is the main entry point for all token logic.
        """
        # 1. No token at all, or the refresh token itself is expired. Must use browser.
        if self.token is None or self.token.is_refresh_expired():
            print_info(
                "Token not found or refresh token expired. Starting new login flow."
            )
            self._fetch_token_via_browser()
        # 2. Access token is expired, but we can try refreshing.
        elif self.token.is_expired():
            print_info("Access token has expired. Attempting to refresh.")
            self._refresh_token()

        # Final check
        if not self.token or self.token.is_expired():
            raise RuntimeError("Unable to obtain a valid token.")

    def request(self, path: str, method: str = "GET", **kwargs):
        """
        Makes an authorized request, automatically handling token validity.
        """
        self._ensure_valid_token()

        # This check is necessary because _ensure_valid_token can fail.
        if not self.token:
            raise RuntimeError("Authentication token is not available.")

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token.access_token}"
        url = f"{self.base_url}{path}"

        # print(f"Making request: {method} {url}")
        response = requests.request(method, url, headers=headers, **kwargs)

        # If the token expired between the check and the request, refresh and retry once.
        if response.status_code == 401:
            print_warning(
                "Received 401 Unauthorized. Token may have just expired. Retrying once."
            )
            self._refresh_token()

            if not self.token:
                raise RuntimeError(
                    "Authentication token is not available after refresh attempt."
                )

            headers["Authorization"] = (
                f"Bearer {self.token.access_token}"  # Bug Fix: Use the new token
            )
            response = requests.request(method, url, headers=headers, **kwargs)

        return response


# --- Example Usage ---
if __name__ == "__main__":
    # This block demonstrates how to use the AuthClient.
    # It will only run when the script is executed directly.
    try:
        # The client will automatically load a token from .tf_client_tokens.json if it exists.
        # If the token is expired or the file doesn't exist, it will trigger the
        # browser-based login flow.
        client = AuthClient()

        # Make an authorized request.
        # The client handles token refreshing automatically.
        print_info("Making an example API request to '/users/me'")
        # Replace '/users/me' with an actual endpoint from your API.
        api_path = "/users/me"

        try:
            # Example using a GET request
            res = client.request(api_path, method="GET")
            res.raise_for_status()  # Raises an exception for 4xx or 5xx status codes

            print_success(f"Successfully received response from {api_path}:")
            # Pretty-print JSON response if possible
            try:
                print(json.dumps(res.json(), indent=2))
            except json.JSONDecodeError:
                print(res.text)

        except requests.HTTPError as e:
            print_error(
                f"API request failed with status {e.response.status_code}: {e.response.text}"
            )
        except requests.RequestException as e:
            print_error(f"A network error occurred: {e}")

    except ValueError as e:
        print_error(f"Configuration error: {e}")
    except RuntimeError as e:
        print_error(f"A runtime error occurred during authentication: {e}")
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user.")
