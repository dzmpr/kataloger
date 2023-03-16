class Repository:
    def __init__(
        self,
        name: str,
        address: str,
        user: str | None = None,
        password: str | None = None,
    ):
        self.name = name
        self.address = address
        self.user = user
        self.password = password
