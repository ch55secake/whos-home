from src.db.service.entity_service import EntityService
from src.db.data.user import User


class UserService(EntityService):
    def __init__(self):
        super().__init__("users", User)

    def create(self, entity: User) -> None:
        super().create(entity)

    def read(self, _id: int) -> User | None:
        return super().read(_id)

    def read_all(self) -> list[User]:
        return super().read_all()

    def update(self, entity: User) -> User | None:
        return super().update(entity)
