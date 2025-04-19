from dataclasses import dataclass, astuple, asdict


@dataclass
class User:
    id: int | None
    name: str | None

    def to_row(self) -> tuple:
        return astuple(self)

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items()}
