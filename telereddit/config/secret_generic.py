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

from telereddit.config.secret import TeleredditSecret
from pyreddit.pyreddit.config import secret_generic

secret_config = TeleredditSecret(
    from_secret=secret_generic.secret_config, TELEGRAM_TOKEN="",
)
