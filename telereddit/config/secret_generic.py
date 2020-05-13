"""
Secret for generic environment.

Loaded when `TELEREDDIT_MACHINE` environment variabile not set on the current
machine.

.. caution::
    This file is public and **not crypted** by git-crypt.

.. tip::
    You can use this file to set the needed variables to get the project up and
    running after a fork.
"""

from telereddit.config.secret import Secret


secret_config = Secret(
    TELEGRAM_TOKEN="",
    TELEREDDIT_USER_AGENT="",
    SENTRY_TOKEN="",
    GFYCAT_CLIENT_ID="",
    GFYCAT_CLIENT_SECRET="",
    IMGUR_CLIENT_ID="",
)
