class Secret():
    # copy-constructor utility
    def set_attr(self, key, value=None):
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

    def __init__(self,
                 from_secret=None,
                 TELEGRAM_TOKEN=None,
                 SENTRY_TOKEN=None,
                 GFYCAT_CLIENT_ID=None,
                 GFYCAT_CLIENT_SECRET=None,
                 IMGUR_CLIENT_ID=None):
        self.from_secret = from_secret
        self.set_attr('TELEGRAM_TOKEN', TELEGRAM_TOKEN)
        self.set_attr('SENTRY_TOKEN', SENTRY_TOKEN)
        self.set_attr('GFYCAT_CLIENT_ID', GFYCAT_CLIENT_ID)
        self.set_attr('GFYCAT_CLIENT_SECRET', GFYCAT_CLIENT_SECRET)
        self.set_attr('IMGUR_CLIENT_ID', IMGUR_CLIENT_ID)
        self.set_attr('SENTRY_TOKEN', SENTRY_TOKEN)

        self.from_secret = None  # free from_secret pointer
