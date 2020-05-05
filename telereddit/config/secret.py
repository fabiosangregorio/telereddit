"""
Base class for secret configurations.
"""


class Secret:
    """
    Secret configuration class. This contains all the necessary
    API keys for the software to run correctly.

    .. note::
        if the parameter `SENTRY_TOKEN` is omitted, Sentry issue tracking service
        will be disabled for the current configuration (i.e. the machine using
        the secret configuration). As a result, the config variable
        `SENTRY_ENABLED` will be False.
    """

    def set_attr(self, key, value=None):
        """
        Copy-constructor utility.

        Parameters
        ----------
        key : str
            Key to set.
        value : Any (Default value = None)
            Value to be assigned to the given key.
        """
        if value is not None:
            self[key] = value
        elif self.from_secret and self.from_secret[key]:
            self[key] = self.from_secret[key]
        else:
            self[key] = None

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __init__(
        self,
        from_secret=None,
        TELEGRAM_TOKEN=None,
        TELEREDDIT_USER_AGENT=None,
        SENTRY_TOKEN=None,
        GFYCAT_CLIENT_ID=None,
        GFYCAT_CLIENT_SECRET=None,
        IMGUR_CLIENT_ID=None,
    ):
        """
        Parameters
        ----------
        from_secret : Secret (Default value = None)
            If set, all the secret variables of `from_secret` will be copied in
            the current object. Override of these variables can be done by
            passing any other parameter as an argument.

        TELEGRAM_TOKEN : str (Default value = None)
            Telegram Bot API token.

        TELEREDDIT_USER_AGENT : str (Default value = None)
            Reddit API user agent. Used by Reddit to track requests from the
            application.

        SENTRY_TOKEN : str (Default value = None)

        GFYCAT_CLIENT_ID : str (Default value = None)

        GFYCAT_CLIENT_SECRET : str (Default value = None)

        IMGUR_CLIENT_ID : str (Default value = None)

        .. warning::
            Although all parameters are optional, the appliation will not work
            as intended if any param is missing (with the exception of
            `SENTRY_TOKEN`)
        """
        self.from_secret = from_secret
        self.set_attr("TELEGRAM_TOKEN", TELEGRAM_TOKEN)
        self.set_attr("TELEREDDIT_USER_AGENT", TELEREDDIT_USER_AGENT)
        self.set_attr("SENTRY_TOKEN", SENTRY_TOKEN)
        self.set_attr("GFYCAT_CLIENT_ID", GFYCAT_CLIENT_ID)
        self.set_attr("GFYCAT_CLIENT_SECRET", GFYCAT_CLIENT_SECRET)
        self.set_attr("IMGUR_CLIENT_ID", IMGUR_CLIENT_ID)
        self.set_attr("SENTRY_TOKEN", SENTRY_TOKEN)

        self.from_secret = None  # free from_secret pointer
