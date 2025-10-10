import argparse
import random
import string
import logging

# Load environment variables from local .env if present
try:
    from dotenv import load_dotenv, find_dotenv  # type: ignore

    # Load .env from current dir or nearest parent
    load_dotenv(find_dotenv(usecwd=True), override=False)
except Exception:
    pass

from .csv_io import create_report_csv, append_report_row, dict_rows
from .nc_api import (
    is_user_absent,
    create_nextcloud_user,
    update_user_field,
    assign_user_to_group,
)


def generate_random_password(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Nextcloud Bulk User Creation",
        description="Script to create multiple users in Nextcloud",
        epilog="Enjoy the program! :)",
    )
    parser.add_argument("filename")
    parser.add_argument(
        "--quota",
        help="Default storage quota for created users (e.g., 10GB, 500MB)",
        default=None,
    )
    parser.add_argument(
        "--language", help="Default UI language (e.g., ru, en)", default=None
    )
    parser.add_argument(
        "--input",
        help="Path to input CSV (defaults to positional filename)",
        default=None,
    )
    parser.add_argument(
        "--output", help="Path to output recap CSV", default="users_passwds.csv"
    )
    parser.add_argument("--delimiter", help="CSV delimiter (default ;)", default=";")
    parser.add_argument(
        "--groups-delimiter",
        help="Delimiter inside the groups field (default ,)",
        default=",",
    )
    parser.add_argument(
        "--password-length",
        type=int,
        help="Generated password length (default 10)",
        default=10,
    )
    parser.add_argument(
        "--welcome",
        action="store_true",
        help="Do not set password; send welcome email instead (email required)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Dry-run without changes"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--timeout", type=int, default=15, help="HTTP request timeout in seconds"
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Number of retry attempts on network errors",
    )
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Update existing users (email/displayname/quota/groups)",
    )
    args = parser.parse_args()
    return args


def create_csv_file(name: str, *, delimiter: str) -> None:
    create_report_csv(name, delimiter=delimiter)


def main(
    filename,
    quota,
    language,
    input_path,
    output_path,
    delimiter,
    groups_delim,
    password_length,
    welcome,
    dry_run,
    verbose,
    timeout,
    retries,
    update_existing,
):
    """Run bulk processing of users from CSV using Nextcloud OCS API."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("ncbulk.script")

    create_csv_file(output_path, delimiter=delimiter)

    for lower_row in dict_rows(input_path, delimiter=delimiter):
        username = (lower_row.get("username", "") or "").strip()
        email = (lower_row.get("email", "") or "").strip()
        displayname = (lower_row.get("displayname", "") or "").strip()
        groups_field = (
            lower_row.get("groups", lower_row.get("group", "")) or ""
        ).strip()
        groups = (
            [g.strip() for g in groups_field.split(groups_delim) if g.strip()]
            if groups_field
            else []
        )
        row_quota = (lower_row.get("quota", "") or "").strip() or quota
        row_language = (lower_row.get("language", "") or "").strip() or language

        if not username:
            logger.warning("Skipping row without username.")
            continue

        if welcome and not email:
            logger.warning(
                "Welcome mode requested but no email for user '%s'.", username
            )

        password = None if welcome else generate_random_password(password_length)

        if is_user_absent(username, timeout=timeout, retries=retries, verbose=verbose):
            if dry_run:
                logger.info(
                    "[DRY-RUN] Create user %s groups=%s quota=%s lang=%s",
                    username,
                    groups,
                    row_quota,
                    row_language,
                )
                created_ok = True
                api_error = None
            else:
                user = create_nextcloud_user(
                    username,
                    password,
                    groups,
                    language=row_language,
                    timeout=timeout,
                    retries=retries,
                    verbose=verbose,
                )
                created_ok = bool(user is True)
                api_error = None if created_ok else user
            if created_ok:
                if not dry_run:
                    if email:
                        update_user_field(
                            username,
                            "email",
                            email,
                            timeout=timeout,
                            retries=retries,
                            verbose=verbose,
                        )
                    if displayname:
                        update_user_field(
                            username,
                            "displayname",
                            displayname,
                            timeout=timeout,
                            retries=retries,
                            verbose=verbose,
                        )
                    if row_quota:
                        update_user_field(
                            username,
                            "quota",
                            row_quota,
                            timeout=timeout,
                            retries=retries,
                            verbose=verbose,
                        )

                append_report_row(
                    path=output_path,
                    delimiter=delimiter,
                    username=username,
                    email=email,
                    displayname=displayname,
                    groups=groups,
                    password=password,
                    status="Created",
                )
                logger.info("User %s created successfully!", username)
            else:
                logger.error("Error creating user %s: %s", username, api_error)
        else:
            logger.info("User %s already exists!", username)
            if update_existing:
                if dry_run:
                    logger.info("[DRY-RUN] Update existing user %s", username)
                else:
                    if email:
                        update_user_field(
                            username,
                            "email",
                            email,
                            timeout=timeout,
                            retries=retries,
                            verbose=verbose,
                        )
                    if displayname:
                        update_user_field(
                            username,
                            "displayname",
                            displayname,
                            timeout=timeout,
                            retries=retries,
                            verbose=verbose,
                        )
                    if row_quota:
                        update_user_field(
                            username,
                            "quota",
                            row_quota,
                            timeout=timeout,
                            retries=retries,
                            verbose=verbose,
                        )
                    for g in groups:
                        assign_user_to_group(
                            username,
                            g,
                            timeout=timeout,
                            retries=retries,
                            verbose=verbose,
                        )
                append_report_row(
                    path=output_path,
                    delimiter=delimiter,
                    username=username,
                    email=email,
                    displayname=displayname,
                    groups=groups,
                    password="" if welcome else None,
                    status="Updated" if update_existing else "Skipped",
                )
            else:
                append_report_row(
                    path=output_path,
                    delimiter=delimiter,
                    username=username,
                    email=email,
                    displayname=displayname,
                    groups=groups,
                    password="" if welcome else None,
                    status="Skipped",
                )


if __name__ == "__main__":
    cli_args = parse_args()
    if getattr(cli_args, "filename", None):
        main(
            filename=cli_args.filename,
            quota=cli_args.quota,
            language=cli_args.language,
            input_path=cli_args.input or cli_args.filename,
            output_path=cli_args.output,
            delimiter=cli_args.delimiter,
            groups_delim=cli_args.groups_delimiter,
            password_length=cli_args.password_length,
            welcome=cli_args.welcome,
            dry_run=cli_args.dry_run,
            verbose=cli_args.verbose,
            timeout=cli_args.timeout,
            retries=cli_args.retries,
            update_existing=cli_args.update_existing,
        )
    else:
        logging.getLogger("ncbulk.script").error("No file specified")
