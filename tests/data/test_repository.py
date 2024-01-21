from typing import Optional

from yarl import URL

from kataloger.data.repository import Repository


class TestRepository:
    def test_repository_should_require_authorization_when_user_and_password_is_not_none(self):
        self._test_require_authorization(
            user="repoUser",
            password="repoPassword",
            expected_requires_authorization=True,
        )

    def test_repository_should_not_require_authorization_when_user_is_not_none_but_password_is_none(self):
        self._test_require_authorization(
            user="repoUser",
            password=None,
            expected_requires_authorization=False,
        )

    def test_repository_should_not_require_authorization_when_password_is_not_none_but_user_is_none(self):
        self._test_require_authorization(
            user=None,
            password="repoPassword",
            expected_requires_authorization=False,
        )

    def test_repository_should_not_require_authorization_when_user_and_password_is_none(self):
        self._test_require_authorization(
            user=None,
            password=None,
            expected_requires_authorization=False,
        )

    @staticmethod
    def _test_require_authorization(
        user: Optional[str],
        password: Optional[str],
        expected_requires_authorization: bool,
    ):
        repository: Repository = Repository(
            name="repository",
            address=URL("https://reposito,ry/"),
            user=user,
            password=password,
        )

        assert repository.requires_authorization() == expected_requires_authorization
