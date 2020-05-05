"""
Project-wide configuration module.

Summary
-------
The configuration of the application is done at program startup by
`telereddit.config.config`.

All the API keys, identity keys and tokens are configured in the `secret_*.py`
files. These modules are dinamically loaded when loading the configuration,
based on the `TELEREDDIT_MACHINE` environment variable.

`secret_dev`, `secret_prod` and `secret_github` are crypted using the GPG
standard via git-crypt.
"""
