from typing import List, Union

from blueness import module
from bluer_options.logger import log_list
from bluer_objects import file, objects
from bluer_objects.metadata import get_from_object

from bluer_sandbox import NAME
from bluer_sandbox.village.family import Family
from bluer_sandbox.village.person import Person
from bluer_sandbox.logger import logger

NAME = module.name(__file__, NAME)


class Village:
    persons: List[Person] = []

    families: List[Family] = []

    def get_person(
        self,
        name: str,
        add: bool = False,
    ) -> Union[Person, None]:
        for person in self.persons:
            if person.name == name:
                return person

        if add:
            person = Person(name=name)
            self.persons.append(person)
            return person

        return None

    def load(
        self,
        object_name: str,
        verbose: bool = False,
    ) -> bool:
        logger.info(f"{NAME}.load({object_name})")

        # loading persons
        persons = get_from_object(object_name, "persons")
        if verbose:
            logger.info(f"persons: {persons}")

        if not isinstance(persons, dict):
            logger.error(f"persons is a {persons.__class__.__name__}, expected dict.")
            return False

        self.persons = [
            Person(
                name=name,
                sex=info.get("sex", "female"),
                death=info.get("death", -1),
            )
            for name, info in persons.items()
        ]
        log_list(
            logger,
            "loaded",
            [person.as_str() for person in self.persons],
            "person(s)",
            max_count=1000,
        )

        # loading families
        families = get_from_object(object_name, "families")
        if verbose:
            logger.info(f"families: {families}")

        if not isinstance(families, dict):
            logger.error(f"families is a {families.__class__.__name__}, expected dict.")
            return False

        self.families = [
            Family(
                parents=[
                    self.get_person(
                        name.strip(),
                        add=True,
                    )
                    for name in parents.split(" + ")
                ],
                children=[
                    self.get_person(
                        name.strip(),
                        add=True,
                    )
                    for name in info.get("children", [])
                ],
                end=info.get("end", -1),
            )
            for parents, info in families.items()
        ]

        log_list(
            logger,
            "loaded",
            [family.as_str() for family in self.families],
            "family(s)",
            max_count=1000,
        )

        log_list(
            logger,
            "created",
            [person.as_str() for person in self.persons],
            "person(s)",
            max_count=1000,
        )

        return True
