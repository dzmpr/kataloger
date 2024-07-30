import re
from functools import total_ordering
from itertools import zip_longest
from typing import List

from kataloger.update_resolver.universal.version import Version


@total_ordering
class UniversalVersion(Version):
    __regex = re.compile(r"^([0-9]{,10}(?:\.[0-9]{1,10}){,20})(?:[-.]([a-zA-Z.-]{1,100})([0-9]{1,10})?)?$")

    __pre_release_names = ("dev", "alpha", "beta", "rc")

    def __init__(self, version: str):
        super().__init__(version)
        match = self.__regex.match(version)
        self.numeric_part: str = match.group(1)
        self.pre_release_name: str = match.group(2)

        pre_release_number = match.group(3)
        if pre_release_number is None:
            pre_release_number = 0
        self.pre_release_number: int = int(pre_release_number)

    def is_pre_release(self) -> bool:
        return self.pre_release_name is not None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UniversalVersion):
            return False

        return self.raw == other.raw

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, UniversalVersion):
            return False

        if self == other:
            return False

        def to_digits_list(version_part: str) -> List[int]:
            return list(map(int, version_part.split(".")))

        # Compare numeric part of version. Missing digits assumed as 0.
        self_digits = to_digits_list(self.numeric_part)
        other_digits = to_digits_list(other.numeric_part)
        for self_digit, other_digit in zip_longest(self_digits, other_digits, fillvalue=0):
            if self_digit < other_digit:
                return True
            if self_digit > other_digit:
                return False

        # Numeric part is equal, lets compare pre-release part.
        if self.is_pre_release() and other.is_pre_release():
            if self.pre_release_name == other.pre_release_name:
                # Pre-release prefixes are equals, compare pre-release numbers
                if self.pre_release_number < other.pre_release_number:
                    return True
            else:
                # Pre-release prefixes are different, compare pre-release prefixes
                self_pr_index = self._pre_release_index()
                other_pr_index = other._pre_release_index()
                if self_pr_index < other_pr_index:
                    return True
                if self_pr_index > other_pr_index:
                    return False
            return False

        return self.is_pre_release() and not other.is_pre_release()

    def _pre_release_index(self) -> int:
        lowercase_pre_release_name = self.pre_release_name.lower()
        if lowercase_pre_release_name in self.__pre_release_names:
            return self.__pre_release_names.index(lowercase_pre_release_name)
        return -1

    @classmethod
    def can_handle(cls, version: str) -> bool:
        return cls.__regex.match(version) is not None
