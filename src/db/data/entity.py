from dataclasses import dataclass, astuple, asdict


@dataclass
class Entity:
    # Can be None when initializing to make use of db autoincrement
    id: int | None

    def to_row(self) -> tuple:
        return astuple(self)

    def to_dict(self) -> dict:
        return dict(asdict(self).items())
