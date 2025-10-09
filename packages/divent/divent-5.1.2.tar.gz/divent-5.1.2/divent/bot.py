import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from os import getenv, path

from disnake import Asset, Client, Guild, Intents, Member, User
from disnake.guild_scheduled_event import GuildScheduledEvent
from dotenv import load_dotenv
from hypercorn.middleware import ProxyFixMiddleware
from ics import Calendar, ContentLine, Event
from ics.alarm import DisplayAlarm
from oauthlib.oauth2 import OAuth2Error
from quart import Quart, redirect, render_template, request, session, url_for
from requests_oauthlib import OAuth2Session  # type: ignore

load_dotenv()

DISCORD_TOKEN = getenv("DISCORD_TOKEN")
OAUTH2_CLIENT_ID = getenv("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = getenv("OAUTH2_CLIENT_SECRET")
if not DISCORD_TOKEN:
    raise Exception("Missing DISCORD_TOKEN")
if not OAUTH2_CLIENT_ID:
    raise Exception("Missing OAUTH2_CLIENT_ID")
if not OAUTH2_CLIENT_SECRET:
    raise Exception("Missing OAUTH2_CLIENT_SECRET")

QUART_DEBUG = getenv("QUART_DEBUG", False)
if QUART_DEBUG:
    logging.basicConfig(level=logging.DEBUG)

API_BASE_URL = getenv("API_BASE_URL", "https://discordapp.com/api")
AUTHORIZATION_BASE_URL = f"{API_BASE_URL}/oauth2/authorize"
TOKEN_URL = f"{API_BASE_URL}/oauth2/token"

CATALOG_CACHE = {}
EVENTS_CACHE = {}


class Discord(Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!", flush=True)

        for guild in self.guilds:
            for scheduled_event in guild.scheduled_events:
                EVENTS_CACHE[scheduled_event.id] = [
                    member.id
                    for member in await scheduled_event.fetch_users().flatten()
                ]

        print("Events synchronised!", flush=True)

    async def on_guild_scheduled_event_subscribe(
        self, event: GuildScheduledEvent, user: Member | User
    ):
        EVENTS_CACHE[event.id].append(user.id)

    async def on_guild_scheduled_event_unsubscribe(
        self, event: GuildScheduledEvent, user: Member | User
    ):
        EVENTS_CACHE[event.id].remove(user.id)

    async def on_guild_scheduled_event_create(self, event: GuildScheduledEvent):
        EVENTS_CACHE[event.id] = [
            member.id for member in await event.fetch_users().flatten()
        ]

    async def on_guild_scheduled_event_delete(self, event: GuildScheduledEvent):
        EVENTS_CACHE.pop(event.id)


intents = Intents.default()
intents.guild_scheduled_events = True
intents.members = True
client = Discord(intents=intents)

app = Quart(__name__)
app.config["SECRET_KEY"] = OAUTH2_CLIENT_SECRET
app.config["EXPLAIN_TEMPLATE_LOADING"] = QUART_DEBUG
app.asgi_app = ProxyFixMiddleware(app.asgi_app)  # type: ignore


def get_guild_by_id(guild_id: str) -> Guild | None:
    if guild_id:
        for guild in client.guilds:
            if str(guild.id) == guild_id or guild.vanity_url_code == guild_id:
                return guild
    return None


@app.errorhandler(500)
async def errorhandler(error: Exception):
    print(f"\33[31m{error}\33[m", flush=True)
    return await render_template("error.html.j2", error=str(error)), 500


@app.errorhandler(404)
async def not_found(error: Exception):
    return await render_template("error.html.j2", error=str(error)), 404


def token_updater(token: str):
    session["oauth2_token"] = token


def make_session(
    token: dict[str, str] | None = None, state: str | None = None
) -> OAuth2Session:
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=["identify", "guilds"],
        redirect_uri=f"{request.host_url}callback",
        auto_refresh_kwargs={
            "client_id": OAUTH2_CLIENT_ID,
            "client_secret": OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater,
    )


def i18n(str: str) -> str:
    lang = request.accept_languages.best_match(["en", "fr"])

    if lang not in CATALOG_CACHE:
        catalog_file = f"{path.dirname(__file__)}/translations/{lang}.json"
        if path.exists(catalog_file):
            with open(catalog_file) as catalog_json:
                catalog = json.load(catalog_json)
                CATALOG_CACHE[lang] = catalog

    if lang in CATALOG_CACHE and str in CATALOG_CACHE[lang]:
        return CATALOG_CACHE[lang][str]

    return str


def days_before_failure() -> int:
    nextYear = datetime.today().year + 5 - ((datetime.today().year + 5) % 5)
    nextDate = datetime(year=nextYear, month=6, day=3)
    nextDelta = nextDate - datetime.now()

    return nextDelta.days


@app.context_processor
def context_processor():
    return dict(
        _=i18n,
        client=client,
        days_before_failure=days_before_failure(),
    )


def login_required(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        if session.get("oauth2_token"):
            return await fn(*args, **kwargs)

        session["redirect_url"] = request.path
        return redirect(url_for(".login"))

    return wrapper


@app.route("/")
async def index():
    return await render_template("index.html.j2")


@app.route("/login")
async def login():
    discord = make_session()
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session["oauth2_state"] = state
    return redirect(authorization_url)


@app.route("/callback")
async def callback():
    request_values = await request.values
    if request_values.get("error"):
        return errorhandler(request_values.get("error"))

    try:
        discord = make_session(state=session.get("oauth2_state"))
        token = discord.fetch_token(
            TOKEN_URL,
            client_secret=OAUTH2_CLIENT_SECRET,
            authorization_response=request.url,
        )
        token_updater(token)
    except OAuth2Error as e:
        return errorhandler(e)

    return redirect(session.pop("redirect_url", url_for(".guilds")))


@app.route("/guilds")
@login_required
async def guilds():
    guild = request.args.get("guild")

    if guild:
        return redirect(url_for(".subscribe", entity_id=guild))

    try:
        discord = make_session(token=session.get("oauth2_token"))
        user = discord.get(f"{API_BASE_URL}/users/@me").json()
        user_guilds = discord.get(f"{API_BASE_URL}/users/@me/guilds").json()
    except OAuth2Error:
        return redirect(url_for(".login"))

    common_guilds = []
    for bot_guild in client.guilds:
        for user_guild in user_guilds:
            if str(bot_guild.id) == user_guild["id"]:
                common_guilds.append(bot_guild)

    return await render_template(
        "guilds.html.j2",
        user=user,
        avatar=Asset._from_avatar(None, user["id"], user["avatar"]),
        common_guilds=common_guilds,
    )


@app.route("/subscribe/<entity_id>")
@login_required
async def subscribe(entity_id: str):
    guild = get_guild_by_id(entity_id)

    if guild:
        try:
            discord = make_session(token=session.get("oauth2_token"))
            user_guilds = discord.get(f"{API_BASE_URL}/users/@me/guilds").json()
        except OAuth2Error:
            return redirect(url_for(".login"))

        if not any(str(guild.id) == user_guild["id"] for user_guild in user_guilds):
            return redirect(url_for(".login"))

        return await render_template(
            "subscribe.html.j2",
            avatar=guild.icon,
            entity_id=guild.vanity_url_code or guild.id,
        )

    try:
        user = await client.get_or_fetch_user(int(entity_id))
    except ValueError:
        return redirect(url_for(".login"))

    if user and str(user.id) == entity_id:
        return await render_template(
            "subscribe.html.j2", avatar=user.avatar, entity_id=user.id
        )

    return redirect(url_for(".login"))


def make_event(scheduled_event: GuildScheduledEvent) -> Event:
    event = Event()

    event.summary = scheduled_event.name
    event.begin = scheduled_event.scheduled_start_time
    event.duration = timedelta(hours=2)
    event.uid = str(scheduled_event.id)
    event.description = scheduled_event.description
    event.url = scheduled_event.url
    event.location = (
        scheduled_event.entity_metadata.location
        if scheduled_event.entity_metadata
        else None
    )

    alarm = DisplayAlarm()
    alarm.trigger = timedelta(hours=-1)
    event.alarms.append(alarm)

    return event


@app.route("/<entity_id>.ics")
async def ical(entity_id: str):
    guild = get_guild_by_id(entity_id)

    if guild:
        calendar = Calendar()

        calendar.extra.append(ContentLine(name="REFRESH-INTERVAL", value="PT1H"))
        calendar.extra.append(ContentLine(name="X-PUBLISHED-TTL", value="PT1H"))

        calendar.extra.append(ContentLine(name="NAME", value=guild.name))
        calendar.extra.append(ContentLine(name="X-WR-CALNAME", value=guild.name))

        if guild.description:
            calendar.extra.append(
                ContentLine(name="DESCRIPTION", value=guild.description)
            )
            calendar.extra.append(
                ContentLine(name="X-WR-CALDESC", value=guild.description)
            )

        for scheduled_event in guild.scheduled_events:
            event = make_event(scheduled_event)
            calendar.events.append(event)

        return calendar.serialize()

    try:
        user = await client.get_or_fetch_user(int(entity_id))
    except ValueError:
        return redirect(url_for(".login"))

    if user:
        calendar = Calendar()

        calendar.extra.append(ContentLine(name="REFRESH-INTERVAL", value="PT1H"))
        calendar.extra.append(ContentLine(name="X-PUBLISHED-TTL", value="PT1H"))

        calendar.extra.append(ContentLine(name="NAME", value=client.user.display_name))
        calendar.extra.append(
            ContentLine(name="X-WR-CALNAME", value=client.user.display_name)
        )

        for guild in client.guilds:
            for scheduled_event in guild.scheduled_events:
                if (
                    scheduled_event.id in EVENTS_CACHE
                    and user.id in EVENTS_CACHE[scheduled_event.id]
                ):
                    event = make_event(scheduled_event)
                    calendar.events.append(event)

        return calendar.serialize()

    return redirect(url_for(".login"))


def run():
    client.loop.create_task(client.start(DISCORD_TOKEN))
    app.run("0.0.0.0", loop=client.loop)
