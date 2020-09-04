"""Base class for secret configurations."""
from pyreddit.pyreddit.config.secret import Secret


class TeleredditSecret(Secret):
    """
    Secret configuration class.

    This contains all the necessary API keys for the software to run correctly.

    .. note::
        if the parameter `SENTRY_TOKEN` is omitted, Sentry issue tracking service
        will be disabled for the current configuration (i.e. the machine using
        the secret configuration). As a result, the config variable
        `SENTRY_ENABLED` will be False.

    Parameters
    ----------
    from_secret : Secret (Default value = None)
        If set, all the secret variables of `from_secret` will be copied in
        the current object. Override of these variables can be done by
        passing any other parameter as an argument.

    TELEGRAM_TOKEN : str (Default value = None)
        Telegram Bot API token.

    .. warning::
        Although all parameters are optional, the appliation will not work
        as intended if any param is missing (with the exception of
        `SENTRY_TOKEN`)

    """

    def __init__(self, from_secret=None, TELEGRAM_TOKEN=None):
        super().__init__()
        self.set_attr("TELEGRAM_TOKEN", TELEGRAM_TOKEN)
        self.from_secret = None  # free from_secret pointer
