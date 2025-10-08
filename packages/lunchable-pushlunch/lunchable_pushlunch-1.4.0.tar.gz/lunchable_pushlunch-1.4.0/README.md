<h1 align="center">lunchable-pushlunch</h1>

<div align="center">
    <p float="center">
        <img src=https://i.imgur.com/j253mXK.png
            width="35%" alt="push-notification">
        <img src=https://i.imgur.com/FyKDsG3.png
            width="60%" alt="lunchable">
    </p>
</div>

<p align="center">
LunchMoney Push Notifications
</p>

<p align="center">
  <a href="https://github.com/juftin/lunchable-pushlunch"><img src="https://img.shields.io/pypi/v/lunchable-pushlunch?color=blue&label=lunchable-pushlunch" alt="PyPI"></a>
  <a href="https://pypi.python.org/pypi/lunchable-pushlunch/"><img src="https://img.shields.io/pypi/pyversions/lunchable-pushlunch" alt="PyPI - Python Version"></a>
  <a href="https://github.com/juftin/lunchable-pushlunch/blob/main/LICENSE"><img src="https://img.shields.io/github/license/juftin/lunchable-pushlunch?color=blue&label=License" alt="GitHub License"></a>
  <a href="https://github.com/juftin/lunchable-pushlunch/actions/workflows/test.yaml?query=branch%3Amain"><img src="https://github.com/juftin/lunchable-pushlunch/actions/workflows/test.yaml/badge.svg?branch=main" alt="Testing Status"></a>
  <a href="https://github.com/go-task/task"><img src="https://img.shields.io/badge/task---?message=task&logo=task&color=teal&labelColor=grey" alt="task"></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv"></a>
  <a href="https://github.com/pre-commit/pre-commit"><img src="https://img.shields.io/badge/pre--commit-enabled-lightgreen?logo=pre-commit" alt="pre-commit"></a>
  <a href="https://juftin.github.io/lunchable-pushlunch/"><img src="https://img.shields.io/static/v1?message=docs&color=526CFE&logo=Material+for+MkDocs&logoColor=FFFFFF&label=" alt="docs"></a>
  <a href="https://github.com/semantic-release/semantic-release"><img src="https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg" alt="semantic-release"></a>
  <a href="https://gitmoji.dev"><img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg" alt="Gitmoji"></a>
</p>

`PushLunch` supports Push Notifications via [Pushover](https://pushover.net)
and [NTFY](https://ntfy.sh). Set your `--provider` flag to either `pushover`
or `ntfy`(or use the `PUSHLUNCH_PROVIDER` environment variable) to choose
your provider. Default is `pushover`.

Pushover supports iOS and Android Push notifications. To get started just provide your Pushover
`Key` (`--key` / `-k`) directly or via the `PUSHOVER_USER_KEY` environment variable.

NTFY is a simple HTTP-based pub-sub notification service. No need to sign up for an account,
just create a topic and use that as your `Key` (`--key` / `-k`) or set the `NTFY_TOPIC`
environment variable.

You can install lunchable with [pip](https://pypi.org/project/lunchable/) or
[pipx](https://pypa.github.io/pipx/). Make sure to use the
`lunchable[pushlunch]` extra to install the `pushlunch` plugin.
You can also use the `lunchable[plugins]` extra to install all the
known plugins.

```shell
pipx install "lunchable[pushlunch]"
```

```shell
pip install "lunchable[pushlunch]"
```

The below command checks for un-reviewed transactions in the current and previous
month and sends them as Push Notifications. The `--continuous` flag tells it to run
forever which will only send you a push notification once for each transaction.
By default it will check every 60 minutes, but this can be changed using the
`--interval` argument.

```shell
lunchable plugins pushlunch notify --continuous
```

## Run via Docker

```shell
docker run --rm \
    --env LUNCHMONEY_ACCESS_TOKEN=${LUNCHMONEY_ACCESS_TOKEN} \
    --env PUSHOVER_USER_KEY=${PUSHOVER_USER_KEY} \
    juftin/lunchable:latest \
    lunchable plugins pushlunch notify --continuous
```
