import json
from typing import Dict, Callable, Any, NamedTuple, Tuple, List


def get_boolean(input: str) -> bool:
    return input.lower() in ('1', 'on', 'true')


class KindController(NamedTuple):
    "Provides a serialize and deserialize methods for each kind of preference"
    # Serialize to a string for saving to the database.
    serialize: Callable[[Any], str]
    # Deserialize to a Python type that is JSON seralizable.
    deserialize: Callable[[str], Any]


# The keys of this dict should be a ALLCAPS string with at most 10 characters.
KINDS: Dict[str, KindController] = {
    'BOOLEAN': KindController(str, get_boolean),
    'INTEGER': KindController(str, int),
    'NUMBER': KindController(str, float),
    'OBJECT': KindController(json.dumps, json.loads),
    'STRING': KindController(str, str),
}

# Choices is a tuple of tuples Which is used by our models to restrict the
# options for Kind, it looks like:
#
#    KIND_CHOICES = [
#        ('BOOLEAN', 'Boolean'),
#        ('INTEGER', 'Integer'),
#        ...
#    ]
KIND_CHOICES: List[Tuple[str, str]] = [
    (kind, kind.title()) for kind in KINDS
]
