class OkStatus:
    def __init__(self, data=None):
        self.ok = True
        self.data = data


class KoStatus:
    def __init__(self, err_msg, err_code=None):
        self.ok = False
        self.data = None
        self.err_msg = err_msg
        self.err_code = err_code
