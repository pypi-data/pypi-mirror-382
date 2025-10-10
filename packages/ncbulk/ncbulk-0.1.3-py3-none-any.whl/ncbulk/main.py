from __future__ import annotations

# This file mirrors previous main.py with package-relative imports

import os
import sys
from dataclasses import dataclass
from typing import List, Optional
import getpass
import csv

try:
    from dotenv import load_dotenv, find_dotenv  # type: ignore

    # Load .env from current dir or nearest parent
    load_dotenv(find_dotenv(usecwd=True), override=False)
except Exception:
    pass


@dataclass
class WizardState:
    input_path: str = "list.csv"
    output_path: str = "users_passwds.csv"
    delimiter: str = ";"
    groups_delim: str = ","
    quota: Optional[str] = None
    language: Optional[str] = None
    welcome: bool = False
    update_existing: bool = False
    dry_run: bool = False
    verbose: bool = False
    password_length: int = 10
    timeout: int = 15
    retries: int = 2
    url: Optional[str] = None
    admin_username: Optional[str] = None
    admin_password: Optional[str] = None


def sniff_delimiter(sample_path: str, fallback: str = ";") -> str:
    try:
        with open(sample_path, "r", newline="") as f:
            sample = f.read(2048)
        dialect = csv.Sniffer().sniff(sample, delimiters=[";", ",", "\t", "|"])
        return dialect.delimiter
    except Exception:
        return fallback


def preview_csv(path: str, delimiter: str, max_rows: int = 5) -> List[List[str]]:
    rows: List[List[str]] = []
    try:
        with open(path, "r", newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for i, row in enumerate(reader):
                rows.append(row)
                if i >= max_rows:
                    break
    except FileNotFoundError:
        pass
    return rows


def prompt_bool(label: str, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        resp = input(f"{label} [{suffix}]: ").strip().lower()
        if not resp:
            return default
        if resp in ("y", "yes", "true", "1"):
            return True
        if resp in ("n", "no", "false", "0"):
            return False
        print("Please answer y or n.")


def prompt_str(label: str, default: Optional[str] = None) -> Optional[str]:
    prompt = f"{label}" + (f" [{default}]" if default is not None else "") + ": "
    resp = input(prompt).strip()
    return resp if resp else default


def prompt_int(label: str, default: int) -> int:
    while True:
        resp = input(f"{label} [{default}]: ").strip()
        if not resp:
            return default
        try:
            return int(resp)
        except ValueError:
            print("Please enter an integer.")


def prompt_secret(label: str, has_default: bool) -> Optional[str]:
    suffix = "[set]" if has_default else "[empty]"
    try:
        value = getpass.getpass(f"{label} {suffix}: ")
    except Exception:
        value = input(f"{label} {suffix}: ")
    value = value.strip()
    if not value and has_default:
        return None
    return value if value else None


def run_wizard() -> WizardState:
    state = WizardState()

    print("ncbulk — Nextcloud Bulk Users — Interactive Wizard")
    print("Press Enter to accept defaults in brackets.")
    print(
        "You can store credentials in a .env file (NEXTCLOUD_URL, NEXTCLOUD_ADMIN_USERNAME, NEXTCLOUD_ADMIN_PASSWORD)."
    )
    print("If present, they are loaded automatically as defaults.")

    env_url = os.getenv("NEXTCLOUD_URL")
    env_user = os.getenv("NEXTCLOUD_ADMIN_USERNAME")
    env_pass_set = os.getenv("NEXTCLOUD_ADMIN_PASSWORD") is not None

    state.url = prompt_str("Nextcloud URL", env_url) or env_url
    state.admin_username = prompt_str("Admin username", env_user) or env_user
    new_password = prompt_secret("Admin password", has_default=env_pass_set)
    state.admin_password = (
        new_password
        if new_password is not None
        else os.getenv("NEXTCLOUD_ADMIN_PASSWORD")
    )

    if prompt_bool("Save credentials to .env (plaintext)", False):
        try:
            env_exists = os.path.exists(".env")
            if env_exists:
                print("Warning: .env already exists.")
                append = prompt_bool(
                    "Append to existing .env instead of overwrite?", True
                )
            else:
                append = False
            mode = "a" if append else "w"
            with open(".env", mode) as f:
                if append:
                    f.write("\n")
                if state.url:
                    f.write(f"NEXTCLOUD_URL={state.url}\n")
                if state.admin_username:
                    f.write(f"NEXTCLOUD_ADMIN_USERNAME={state.admin_username}\n")
                if state.admin_password is not None:
                    f.write(f"NEXTCLOUD_ADMIN_PASSWORD={state.admin_password}\n")
            print(".env saved (consider securing this file).")
        except Exception as exc:
            print(f"Failed to write .env: {exc}")

    print("Input CSV: path to the source list with a header row.")
    state.input_path = (
        prompt_str("Input CSV path", state.input_path) or state.input_path
    )
    if os.path.exists(state.input_path):
        state.delimiter = sniff_delimiter(state.input_path, fallback=state.delimiter)
        print(f"Detected delimiter: '{state.delimiter}'")
        rows = preview_csv(state.input_path, state.delimiter)
        if rows:
            print("Preview:")
            for r in rows:
                print("  ", " | ".join(r))
        else:
            print("No preview available (file empty or unreadable).")
    else:
        print("Input file does not exist yet (you can create it and rerun).")

    print("Output CSV: recap file with generated passwords (if not in welcome mode).")
    state.output_path = (
        prompt_str("Output CSV path", state.output_path) or state.output_path
    )
    print("CSV delimiter: used to parse input and write output (options: ; , \t |).")
    state.delimiter = (
        prompt_str("CSV delimiter (; , \t |)", state.delimiter) or state.delimiter
    )
    print("Groups delimiter: separator for multiple groups inside one CSV cell.")
    state.groups_delim = (
        prompt_str("Groups delimiter", state.groups_delim) or state.groups_delim
    )

    print("Quota: default storage quota (e.g., 10GB, 500MB). Row 'quota' overrides it.")
    state.quota = prompt_str("Default quota (e.g., 10GB) or empty", state.quota)
    print(
        "Language: default UI language code (e.g., ru, en). Row 'language' overrides."
    )
    state.language = prompt_str(
        "Default language (e.g., ru, en) or empty", state.language
    )

    print("Password length: length for generated passwords when not in welcome mode.")
    state.password_length = int(prompt_int("Password length", state.password_length))
    print("HTTP timeout: seconds to wait for each HTTP request before failing.")
    state.timeout = int(prompt_int("HTTP timeout (s)", state.timeout))
    print("HTTP retries: number of retry attempts on transient HTTP/network errors.")
    state.retries = int(prompt_int("HTTP retries", state.retries))

    print(
        "Welcome mode: do not set passwords; Nextcloud sends a welcome email (email required)."
    )
    state.welcome = prompt_bool("Welcome mode (no password, send email)", state.welcome)
    print(
        "Update existing: update email/displayname/quota and add user to listed groups."
    )
    state.update_existing = prompt_bool("Update existing users", state.update_existing)
    print("Dry-run: perform no changes, only show what would happen.")
    state.dry_run = prompt_bool("Dry-run (no changes)", state.dry_run)
    print("Verbose: print extra HTTP attempt logs to help diagnose issues.")
    state.verbose = prompt_bool("Verbose HTTP logging", state.verbose)

    if not os.path.exists(state.input_path):
        print("You can generate a starter CSV with the right header.")
        if prompt_bool("Generate CSV template now?", True):
            try:
                with open(state.input_path, "w") as tmpl:
                    tmpl.write("username;email;displayname;groups;quota;language\n")
                print(f"Template created at {state.input_path}")
            except Exception as exc:
                print(f"Failed to create template: {exc}")

    print("\nReview your settings:")
    print(f"  URL: {state.url}")
    print(f"  Admin username: {state.admin_username}")
    print(
        "  Admin password: ****"
        if state.admin_password
        else "  Admin password: (not set)"
    )
    print(f"  Input CSV: {state.input_path}")
    print(f"  Output CSV: {state.output_path}")
    print(f"  CSV delimiter: {state.delimiter}")
    print(f"  Groups delimiter: {state.groups_delim}")
    print(f"  Default quota: {state.quota or '(none)'}")
    print(f"  Default language: {state.language or '(none)'}")
    print(f"  Password length: {state.password_length}")
    print(f"  HTTP timeout: {state.timeout}")
    print(f"  HTTP retries: {state.retries}")
    print(f"  Welcome mode: {state.welcome}")
    print(f"  Update existing: {state.update_existing}")
    print(f"  Dry-run: {state.dry_run}")
    print(f"  Verbose: {state.verbose}")

    if not prompt_bool("Proceed with these settings?", True):
        print("Cancelled by user.")
        sys.exit(0)

    return state


def main():
    try:
        state = run_wizard()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return

    # defer heavy logic to script.main
    try:
        from .script import main as process
    except Exception as exc:
        print(f"Failed to import processing module: {exc}")
        sys.exit(1)

    if state.url is not None:
        os.environ["NEXTCLOUD_URL"] = state.url
    if state.admin_username is not None:
        os.environ["NEXTCLOUD_ADMIN_USERNAME"] = state.admin_username
    if state.admin_password is not None:
        os.environ["NEXTCLOUD_ADMIN_PASSWORD"] = state.admin_password

    process(
        filename=state.input_path,
        quota=state.quota,
        language=state.language,
        input_path=state.input_path,
        output_path=state.output_path,
        delimiter=state.delimiter,
        groups_delim=state.groups_delim,
        password_length=state.password_length,
        welcome=state.welcome,
        dry_run=state.dry_run,
        verbose=state.verbose,
        timeout=state.timeout,
        retries=state.retries,
        update_existing=state.update_existing,
    )


if __name__ == "__main__":
    main()
