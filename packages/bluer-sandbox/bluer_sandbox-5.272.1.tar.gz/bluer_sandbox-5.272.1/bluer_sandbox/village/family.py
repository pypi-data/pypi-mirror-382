from typing import List

from bluer_sandbox.village.person import Person


class Family:
    def __init__(
        self,
        parents: List[Person] = [],
        children: List[Person] = [],
        end: int = -1,
    ):
        self.parents = parents
        self.children = children
        self.end = end

    def as_str(
        self,
        verbose: bool = False,
    ) -> str:
        return "[{}]{}{}".format(
            " + ".join(
                [person.as_str() if verbose else person.name for person in self.parents]
            ),
            (
                ""
                if not self.children
                else " -> {}".format(
                    " + ".join(
                        [
                            child.as_str() if verbose else child.name
                            for child in self.children
                        ]
                    )
                )
            ),
            ("" if self.end == -1 else f" (ended {self.end})"),
        )
