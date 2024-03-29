<p align="center"><a href="https://telegram.me/tele_reddit_bot"><img height="200" width="200"
      src="https://raw.githubusercontent.com/fabiosangregorio/telereddit/master/docs/images/logo.png" alt="telereddit" /></a></p>
<h1 align="center">Telereddit</h1>

<p align="center">
  <a href="https://github.com/fabiosangregorio/telereddit/actions?query=workflow%3Adocs"><img
      src="https://github.com/fabiosangregorio/telereddit/workflows/docs/badge.svg" alt="Docs status"></a>
  <a href="https://github.com/fabiosangregorio/telereddit/actions?query=workflow%3Atest"><img
      src="https://github.com/fabiosangregorio/telereddit/workflows/test/badge.svg" alt="Test status"></a>
  <a href="https://github.com/fabiosangregorio/telereddit/actions?query=workflow%3Alint"><img
      src="https://github.com/fabiosangregorio/telereddit/workflows/lint/badge.svg" alt="Lint status"></a>
  <a href='https://coveralls.io/github/fabiosangregorio/telereddit?branch=master'><img src='https://coveralls.io/repos/github/fabiosangregorio/telereddit/badge.svg?branch=master' alt='Coverage Status' /></a>
  <a
    href="https://www.codacy.com/app/fabio.sangregorio/telereddit?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=fabiosangregorio/telereddit&amp;utm_campaign=Badge_Grade"><img
      src="https://api.codacy.com/project/badge/Grade/76515a362977419b91de831466e1bf9a" alt="Codacy Badge"></a>
  <a href="https://codeclimate.com/github/fabiosangregorio/telereddit/maintainability"><img
      src="https://api.codeclimate.com/v1/badges/bef15455da0878eae539/maintainability" alt="Maintainability"></a>
  <img class="docs-coverage" src="https://img.shields.io/badge/docs-100%25-brightgreen" alt="Docs coverage">
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"
      alt="Code style: black"></a>
</p>

Add this bot on Telegram: [telegram.me](https://telegram.me/tele_reddit_bot)!

Telereddit is a Telegram bot which lets you easily see shared Reddit posts previews directly in the group chat. This bot will also automatically send a random post from a subreddit when you name it.

## Like the project?
 <a href="https://www.buymeacoffee.com/fabiosang" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/lato-orange.png" alt="Buy Me A Coffee" width="150"></a>


## Features

### Post sharing

<p align="center">
  <img src="https://media.giphy.com/media/Q7GO3X5BUdNCMZeDU9/giphy.gif" alt="Post sharing" />
</p>

### Random post from a subreddit

<p align="center">
  <img src="https://media.giphy.com/media/ViIfu7Zue9Ig5vo0O5/giphy.gif" alt="Random post from a subreddit" />
</p>

Get it on [telegram.me](https://telegram.me/tele_reddit_bot)!

## Installation

1. Clone the repository
1. Install requirements
    ```bash
    pip install -r requirements.txt
    ```
1. Set up Telegram token and API keys by duplicating and filling out `./telereddit/config/template.env`
1. Set the environment variable `REDDIT_BOTS_MACHINE` to the name of the env file (e.g.: for `dev.env` set
   `REDDIT_BOTS_MACHINE=DEV`)
1. Start the bot
    ```bash
    python -m telereddit
    ```
1. Enjoy

## Bugs and feature requests
If you want to report a bug or would like a feature to be added, feel free to open an issue.


## Versioning
We follow Semantic Versioning. The version X.Y.Z indicates:

* X is the major version (backward-incompatible),
* Y is the minor version (backward-compatible), and
* Z is the patch version (backward-compatible bug fix).
 
## License
**[GPL v3](https://www.gnu.org/licenses/gpl-3.0)** - Copyright 2020 © <a href="http://fabio.sangregorio.dev"
  target="_blank">fabio.sangregorio.dev</a>.
  
