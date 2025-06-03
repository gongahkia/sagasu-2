![](https://img.shields.io/badge/sagasu_2.0.0-passing-green) 

# `Sagasu 2`

<p align="center">
    <img src="./asset/logo/sagasu-2.png" width=55% height=55%>
</p>

`Sagasu 2` exists in the following forms.

1. ***Live Telegram Bot*** [@sagasu2_bot](https://t.me/sagasu2_bot)
2. ***Live Web App*** at [sagasu-two.vercel.app](https://sagasu-two.vercel.app/)

## Rationale

...

## Stack

### Telegram Bot

* *Frontend*: [Telegram Bot API](https://core.telegram.org/)
* *Backend*: [Python](https://www.python.org/)
* *Cache*: [Redis](https://redis.io/)
* *Encryption*: ...
* ...

### Web App

* *Frontend*: [React](https://react.dev/), [Next.js](https://nextjs.org/)
* *Backend*: [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/)
* *Cache*: [Redis](https://redis.io/)
* *Package*: [Docker](https://www.docker.com/)
* *Encryption*: ...

## Architecture

### [Telegram Bot](./telegram_bot/)

...

### [Web App](./web/)

...

## Usage

The below instructions are for locally running `Sagasu 2`. Note the most direct way to use `Sagasu 2` would be to [**use the Telegram Bot/Web App**](#sagasu-2).

1. First run the below.

```console
$ python3 -m venv myenv
$ source myenv/bin/activate
$ make
```

2. Then create a `.env` file with the following details at `./src/`.

```env
TELEGRAM_BOT_TOKEN=XXX
SMU_FBS_USERNAME=XXX
SMU_FBS_PASSWORD=XXX
REDIS_URL=redis://localhost:6379/0
```

3. Then run the below.

```console
docker-compose up redis core
docker-compose up telegram-bot
docker-compose up web-backend
cd web/frontend && npm start
```

## Other notes

[`Sagasu-2`](https://github.com/gongahkia/sagasu-2) stands on the shoulders of [`Sagasu`](https://github.com/gongahkia/sagasu).