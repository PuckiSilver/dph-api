import sqlite3
import secrets
import config
import disnake
import datetime
from usefuls.commons import *
import json


def authenticate(auth: str):
    """
    `dict` - If success returns user details\n
    `31` - If auth not supplied\n
    `32` - If auth is not basic\n
    `33` - If user is not existing\n
    """
    if not auth:
        return 31
    if not auth.startswith("Basic"):
        return 32

    token = auth[6:]

    conn = sqlite3.connect(config.DATA + "data.db")

    u = conn.execute(
        f"select username, rowid, role, bio, profile_icon, badges from users where token = '{token}'"
    ).fetchone()
    if not u:
        print("user doth not exists")
        return 33
    conn.close()

    if u[5]:
        print(u[5])
        badges = json.loads(u[5])
    else:
        badges = None
    return User(u[1], u[0], u[2], u[3], profile_icon=u[4], badges=badges)


class get_user:
    def from_username(self: str):
        conn = sqlite3.connect(config.DATA + "data.db")

        # Select
        u = conn.execute(
            f"select username, rowid, role, bio, profile_icon, badges from users where lower(username) = '{sanitise(self.lower())}'"
        ).fetchone()

        if not u:
            return None

        conn.close()

        if u[5]:
            badges = json.loads(u[5])
        else:
            badges = None
        return User(u[1], u[0], u[2], u[3], profile_icon=u[4], badges=badges)

    def from_id(self: int):
        conn = sqlite3.connect(config.DATA + "data.db")

        # Select
        u = conn.execute(
            f"select username, rowid, role, bio, profile_icon, badges from users where rowid = {self}"
        ).fetchone()

        if not u:
            return None

        conn.close()

        if u[5]:
            badges = json.loads(u[5])
        else:
            badges = None
        return User(u[1], u[0], u[2], u[3], profile_icon=u[4], badges=badges)

    def from_github_id(self: int):
        conn = sqlite3.connect(config.DATA + "data.db")

        # Select
        u = conn.execute(
            f"select username, rowid, role, bio, profile_icon, badges from users where github_id = {self}"
        ).fetchone()

        if not u:
            return None

        conn.close()

        if u[5]:
            badges = json.loads(u[5])
        else:
            badges = None
        return User(u[1], u[0], u[2], u[3], profile_icon=u[4], badges=badges)

    def from_discord_id(self: int):
        conn = sqlite3.connect(config.DATA + "data.db")

        # Select
        u = conn.execute(
            f"select username, rowid, role, bio, profile_icon, badges from users where discord_id = {self}"
        ).fetchone()

        if not u:
            return None

        conn.close()

        if u[5]:
            badges = json.loads(u[5])
        else:
            badges = None
        return User(u[1], u[0], u[2], u[3], profile_icon=u[4], badges=badges)

    def from_token(token: str):
        conn = sqlite3.connect(config.DATA + "data.db")

        # Select
        u = conn.execute(
            f"select username, rowid, role, bio, profile_icon, badges from users where token = '{sanitise(token)}'"
        ).fetchone()

        if not u:
            print("SillySilabearError: The user does not exist")
            return False

        conn.close()

        if u[5]:
            print(u[5])
            badges = json.loads(u[5])
        else:
            badges = None
        return User(u[1], u[0], u[2], u[3], profile_icon=u[4], badges=badges)


def get_user_token(github_id: int):
    conn = sqlite3.connect(config.DATA + "data.db")

    # Select
    u = conn.execute(
        f"select token from users where github_id = {github_id}"
    ).fetchone()

    conn.close()

    if not u:
        return None

    return u[0]


def get_user_token_from_discord_id(discord: int):
    conn = sqlite3.connect(config.DATA + "data.db")

    # Select
    u = conn.execute(f"select token from users where discord_id = {discord}").fetchone()

    conn.close()

    if not u:
        return None

    return u[0]


def create_user_account(
    ghubdata: dict,
):
    conn = sqlite3.connect(config.DATA + "data.db")

    token = secrets.token_urlsafe()

    # Create user entry in database
    conn.execute(
        f'INSERT INTO users (username, role, bio, github_id, token, profile_icon) VALUES ("{ghubdata["login"]}", "default", "A new Datapack Hub user!", {ghubdata["id"]}, "{token}", "{ghubdata["avatar_url"]}")'
    )

    conn.commit()
    conn.close()

    print("CREATED USER: " + ghubdata["login"])

    return token


def get_user_ban_data(id: int):
    conn = sqlite3.connect(config.DATA + "data.db")

    banned_user = conn.execute(
        "select reason, expires from banned_users where id = " + str(id)
    ).fetchone()

    if not banned_user:
        return None

    conn.close()

    return {"reason": banned_user[0], "expires": banned_user[1]}


def log_user_out(id: int):
    conn = sqlite3.connect(config.DATA + "data.db")

    token = secrets.token_urlsafe()

    # Create user entry in database
    try:
        conn.execute(f'UPDATE users SET token = "{token}" WHERE rowid = {id}')
    except sqlite3.Error as err:
        return err

    conn.commit()
    conn.close()

    return "Success!"


class post:
    def site_log(user: str, action: str, content: str):
        usr = get_user.from_username(user)

        webhook = disnake.SyncWebhook.from_url(config.MOD_LOGS)
        emb = disnake.Embed(
            title=action,
            description=content,
            color=2829617,
            timestamp=datetime.datetime.now(),
        ).set_author(name=usr.username, icon_url=usr.profile_icon)
        webhook.send(embed=emb)
    def error(title: str, message: str):
        webhook = disnake.SyncWebhook.from_url(config.MOD_LOGS)
        emb = disnake.Embed(
            title=title,
            description=message,
            color=disnake.Color.red(),
            timestamp=datetime.datetime.now(),
        )
        webhook.send(embed=emb)
    def approval(approver: str, title: str, description: str, icon:str, author: int):
        author_obj = get_user.from_id(author)

        webhook = disnake.SyncWebhook.from_url(config.PROJ_LOGS)
        emb = disnake.Embed(
            title=title,
            description=description,
            color=2673743,
            timestamp=datetime.datetime.now(),
        ).set_author(name=f"Project approved by {approver}", icon_url="https://media.discordapp.net/attachments/1076912842269270037/1122514368979026021/utility12.png").set_footer(text=author_obj.username,icon_url=author_obj.profile_icon).set_thumbnail(icon)
        webhook.send(embed=emb)
    def deletion(approver: str, title: str, description: str, icon:str, author: int, reason: str):
        author_obj = get_user.from_id(author)

        webhook = disnake.SyncWebhook.from_url(config.PROJ_LOGS)
        emb = disnake.Embed(
            title=title,
            description=description,
            color=12597818,
            timestamp=datetime.datetime.now(),
        ).set_author(name=f"Project deleted by {approver}", icon_url="https://media.discordapp.net/attachments/1076912842269270037/1122514607572009040/utility8.png").set_footer(text=author_obj.username,icon_url=author_obj.profile_icon).set_thumbnail(icon).add_field("Reason",reason)
        webhook.send(embed=emb)
    def disabled(approver: str, title: str, description: str, icon:str, author: int, reason: str):
        author_obj = get_user.from_id(author)

        webhook = disnake.SyncWebhook.from_url(config.PROJ_LOGS)
        emb = disnake.Embed(
            title=title,
            description=description,
            color=12597818,
            timestamp=datetime.datetime.now(),
        ).set_author(name=f"Project disabled by {approver}", icon_url="https://media.discordapp.net/attachments/1076912842269270037/1122514607572009040/utility8.png").set_footer(text=author_obj.username,icon_url=author_obj.profile_icon).set_thumbnail(icon).add_field("Reason",reason)
        webhook.send(embed=emb)
    def in_queue(title: str, description: str, icon:str, author: int):
        author_obj = get_user.from_id(author)

        webhook = disnake.SyncWebhook.from_url(config.PROJ_LOGS)
        emb = disnake.Embed(
            title=title,
            description=description,
            color=12487214,
            timestamp=datetime.datetime.now(),
        ).set_author(name=f"Project awaiting approval", icon_url="https://media.discordapp.net/attachments/1076912842269270037/1122514541138432020/output-onlinepngtools.png").set_footer(text=author_obj.username,icon_url=author_obj.profile_icon).set_thumbnail(icon)
        webhook.send(embed=emb)


def user_owns_project(project: int, author: int):
    conn = sqlite3.connect(config.DATA + "data.db")
    proj = conn.execute(
        f"select rowid from projects where rowid = {str(project)} and author = {str(author)}"
    ).fetchall()
    conn.close()
    if len(proj) == 1:
        return True
    return False


def sanitise(query: str):
    return query.replace("'", r"\'").replace(";", r"\;")


if __name__ == "__main__":
    post.approval("Silabear","Hexenwerk","Magic datapack which adds wands, spells, etc. and will soon even be well polished!","https://files.datapackhub.net/icons/174209.png","Flynecraft")