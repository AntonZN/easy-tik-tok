#A simple parody of TikTok

Example Lightweight API for building tiktok-like applications

## Requirements

* [Docker](https://www.docker.com/).
* [Docker Compose](https://docs.docker.com/compose/install/).
* [Poetry](https://python-poetry.org/)
* [Tortoise](https://tortoise-orm.readthedocs.io/)
* [Aerich](https://github.com/tortoise/aerich/)
* [FFmpeg](https://www.ffmpeg.org/)


## Features API

* Full async
* Simple jwt auth
* VIDEO: Viewing video feed, add video, play video(streaming response), like/dislike video, comment
* USER: create, view, follow, simple profile
* Storing uploaded videos on a local server(default) or AWS S3 platform(azure cloud, yandex cloud) -> need change conf
* Encoding uploaded videos with ffmpeg


## Quick Start
Rename `env_template -> .env` and edit.
```
docker-compose up -d --build
```

Automatic interactive documentation with Swagger UI (from the OpenAPI backend): http://app.localhost/api/v1/docs/

Alternative automatic documentation with ReDoc (from the OpenAPI backend): http://app.localhost/api/v1/redoc/

Traefik UI, to see how the routes are being handled by the proxy: http://localhost:8080

Create the first migration and apply it to the database:

```
docker-compose exec app aerich init-db
```

## Create Migration

Make a change to the model. Then, run:

```
docker-compose exec app aerich migrate
docker-compose exec app aerich upgrade
```

## FFmpeg to encode uploaded videos

### Video and audio encoding for playback in Android and iOS devices
* [mobile.video.encoding](https://gist.github.com/pinge/b9f9ce1e4d399503f7c80df4c5d09f22)