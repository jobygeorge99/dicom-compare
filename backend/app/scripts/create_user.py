"""Create a user from the command line, e.g. the very first admin.

    python -m app.scripts.create_user --email admin@example.com --role admin

Why a script? The API's "create user" endpoint will be admin-only, so the
first admin has to come from somewhere else: this is the "bootstrap" problem.
"""

import argparse
import getpass
import sys

from app.core.security import hash_password
from app.db.models import Role, User
from app.db.session import SessionLocal
from app.services.auth import get_user_by_email, normalize_email

MIN_PASSWORD_LENGTH = 12


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a DICOM Compare user.")
    parser.add_argument("--email", required=True)
    parser.add_argument(
        "--role",
        choices=[role.value for role in Role],
        default=Role.ANALYST.value,
    )
    args = parser.parse_args(argv)

    # getpass hides what you type: the password never shows on screen or
    # lands in your shell history (it would if it were a --password flag).
    password = getpass.getpass("Password: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        print(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.", file=sys.stderr)
        return 1
    if getpass.getpass("Repeat password: ") != password:
        print("Passwords do not match.", file=sys.stderr)
        return 1

    with SessionLocal() as db:
        if get_user_by_email(db, args.email) is not None:
            print(f"A user with email {args.email} already exists.", file=sys.stderr)
            return 1

        user = User(
            email=normalize_email(args.email),
            password_hash=hash_password(password),
            role=Role(args.role),
        )
        db.add(user)
        db.commit()
        print(f"Created {user.role.value} user {user.email} (id {user.id}).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
