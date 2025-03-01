import functools
import logging
import random
import secrets
import time
from typing import Any
import re

from sqlalchemy import Connection, CursorResult, create_engine, text

import config
from utilities import weblogs
from utilities.commons import PlayerBanData

connection = create_engine("sqlite:///" + config.DATA + "data.db").connect()


def make_connection() -> Connection:
    return connection


def exec_query(conn: Connection, query: str, **params: Any) -> CursorResult[Any]:
    q = text(query)

    if params:
        q = q.bindparams(**params)
    return conn.execute(q)


def commit_query(command: str, **params: Any) -> CursorResult[Any]:
    conn = make_connection()
    result = exec_query(conn, command, **params)
    conn.commit()
    return result


def log(msg: object, level: int = logging.INFO):
    logging.basicConfig(level=level, format=config.PYTHON_LOGGING_CONF)
    logging.log(level=level, msg=msg)


def create_user_account(
    github_data: dict[str, Any],
) -> str:
    conn = make_connection()

    token = secrets.token_urlsafe()

    check = exec_query(
        conn,
        "select username from users where username = :login;",
        login=github_data["login"],
    ).all()
    if not check:
        username = github_data["login"]
    else:
        username = github_data["login"] + str(random.randint(1, 99999))

    # Create user entry in database
    exec_query(
        conn,
        'INSERT INTO users (username, role, bio, github_id, token, profile_icon, join_date) VALUES (:g_login, "default", "A new Datapack Hub user!", :id, :token, :avatar, :join)',
        g_login=username,
        id=github_data["id"],
        token=token,
        avatar=github_data["avatar_url"],
        join=time.time(),
    )

    conn.commit()

    log("CREATED USER: " + github_data["login"])

    return token


def get_user_ban_data(id: int) -> PlayerBanData | None:
    conn = make_connection()

    banned_user = exec_query(
        conn,
        "select reason, expires from banned_users where id = :id",
        id=id,
    ).one_or_none()

    if banned_user is None:
        return None

    return {"reason": banned_user[0], "expires": banned_user[1]}


@functools.lru_cache
def user_owns_project(project: int, author: int):
    conn = make_connection()
    proj = exec_query(
        conn,
        "select rowid from projects where rowid = :project and author = :author",
        project=project,
        author=author,
    ).all()

    return len(proj) == 1


# def get_user_data(id: int, data: list[str])
#     ).one()


def send_notif(conn: Connection, title: str, msg: str, receiver: int):
    exec_query(
        conn,
        "INSERT INTO notifs VALUES (:title, :msg, False, 'default', :uid})",
        title=title,
        msg=msg,
        uid=receiver,
    )


# Custom sorting function for semver
def semver_key(version: str) -> tuple[int, int, int]:
    # Replace 'x' in the version with a high number for comparison
    version = version.replace("x", "999999")
    # Use regex to match major, minor, and patch numbers
    match = re.match(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", version)

    if match:
        # If there is a match, extract major, minor, and patch numbers
        groups = map(int, match.groups())
        return (groups[0],
                groups[1] if len(groups) >= 2 else 0,
                groups[2] if len(groups) == 3 else 0)
    else:
        # If no match is found, return a tuple of zeros
        return 0, 0, 0


if __name__ == "__main__":
    weblogs.approval(
        "Silabear",
        "Hexenwerk",
        "Magic datapack which adds wands, spells, etc. and will soon even be well polished!",
        "https://files.datapackhub.net/icons/174209.png",
        1,
        "hexenwerk",
    )
