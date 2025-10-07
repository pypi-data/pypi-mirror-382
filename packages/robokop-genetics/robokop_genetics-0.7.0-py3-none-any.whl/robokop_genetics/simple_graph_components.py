from dataclasses import dataclass, field
from robokop_genetics.util import Text


@dataclass
class SimpleNode:
    id: str
    type: str
    name: str
    properties: dict = field(default_factory=dict)
    synonyms: set = field(default_factory=set)

    def __post_init__(self):
        if not self.synonyms:
            self.synonyms = {self.id}

    def get_synonyms_by_prefix(self, prefix: str):
        """Returns curies for any synonym with the input prefix"""
        return set(filter(lambda x: Text.get_curie(x) == prefix, self.synonyms))

    def add_synonyms(self, new_synonym_set: set):
        self.synonyms.update(new_synonym_set)


@dataclass
class SimpleEdge:
    source_id: str
    target_id: str
    provided_by: str
    input_id: str
    predicate_id: str
    predicate_label: str
    ctime: int
    properties: dict = field(default_factory=dict)
