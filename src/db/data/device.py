from dataclasses import dataclass, astuple, asdict

from db.service.user_service import UserService
from src.db.data.user import User


@dataclass
class Device:
    id: int | None
    device_name: str
    owned_by: int | None

    def to_row(self) -> tuple:
        return astuple(self)

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items()}

    def get_owned_by_user(self) -> User | None:
        return UserService().read(self.owned_by) if self.owned_by is not None else None
