from dataclasses import dataclass
import re
from typing import Iterable, Protocol, Dict

class QualifierProtocol(Protocol):
    def qualify(self, values: Iterable[str]) -> Dict[str, bool]:
        pass


@dataclass(frozen=True, slots=True)
class PatternMatchQualifier(QualifierProtocol):
    regex: str = None
    values: Iterable[str] = None

    def __post_init__(self):
        if self.regex is None and self.values is None:
            raise ValueError(f"At least one of regex or id must be filled")

    def qualify(self, values: Iterable[str]) -> Dict[str, bool]:
        ret = {}
        for value in values:

            if self.regex is not None and not re.match(self.regex, value):
                ret[value] = False

            if self.values is not None and value not in self.values:
                ret[value] = False

            ret[value] = True

        return ret
