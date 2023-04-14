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

    def requires_authorization(self) -> bool:
        return self.user is not None and self.password is not None
