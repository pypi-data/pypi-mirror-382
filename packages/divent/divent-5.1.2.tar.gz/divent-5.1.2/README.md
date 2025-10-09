# Divent
> The discord scheduled event calendar generator

[![Docker Hub](https://img.shields.io/docker/pulls/xefir/divent)](https://hub.docker.com/r/xefir/divent)

Simple website that guides you to invite a bot to read and format scheduled events to a subscribable calendar.

## Installing / Getting started

### 1) Create the bot

- Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
- Enable the `Build-A-Bot` option in the `Bot` panel.
- Click on `Reset Token` and keep it in a safe place, you will need it.
- Click on `Reset Secret` in the `OAuth2` panel, copy both `Client ID` and `Client Secret` and keep it in a safe place, you will need it.
- Configure the rest of your app and bot as you like (name, icon, username, etc.)

### 2) With Docker

- Install [Docker](https://docs.docker.com/get-docker/)
- Run
```bash
docker run -p 5000 \
    -e DISCORD_TOKEN=your_bot_token \
    -e OAUTH2_CLIENT_ID=your_client_id \
    -e OAUTH2_CLIENT_SECRET=your_client_secret \
    xefir/divent
```

### 2) Without Docker

- Install [Python 3](https://www.python.org/downloads/)
- Install [Pip](https://pip.pypa.io/en/stable/installation/)
- Run `pip install divent`
- Run
```bash
DISCORD_TOKEN=your_bot_token \
OAUTH2_CLIENT_ID=your_client_id \
OAUTH2_CLIENT_SECRET=your_client_secret \
divent
```

### 3) Open your browser

The app is accessible at http://localhost:5000

## Links

- [Project homepage](https://divent.crystalyx.net/)
- [Source repository](https://git.crystalyx.net/Xefir/Divent)
- [Issue tracker](https://git.crystalyx.net/Xefir/Divent/issues)
- [My other projects](https://git.crystalyx.net/Xefir)
- [The WTFPL licence](http://www.wtfpl.net/)
- [Docker hub](https://hub.docker.com/r/xefir/divent)
- [Pypi](https://pypi.org/project/Divent/)
- [Donations](https://paypal.me/Xefir)
