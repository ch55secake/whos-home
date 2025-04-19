from src.db.data.user import User
from src.db.db_connector import DatabaseConnector


class UserService:
    def __init__(self):
        self.__connection = DatabaseConnector()
        self.__connection.connect()

    def create(self, entity: User) -> None:
        entity_dict = entity.to_dict()
        cols = ", ".join(entity_dict.keys())
        vals = [":" + k for k in entity_dict.keys()]
        sql = f"INSERT INTO users ({cols}) VALUES ({vals});"
        self.__connection.find_all(sql)

    def read(self, _id: int) -> User | None:
        user = self.__connection.find_one("SELECT * FROM users WHERE id = ?;", (_id,))
        return User(**dict(user)) if user is not None else None

    def read_all(self) -> list[User]:
        users_rows = self.__connection.find_all("SELECT * FROM users;")
        return [User(**dict(row)) for row in users_rows]

    def update(self, entity: User) -> User | None:
        if not self.exists(entity.id):
            return None
        update_sql = "UPDATE users "
        set_strs = []
        entity_as_dict = entity.to_dict()
        for k in entity_as_dict.keys():
            if k == 'id':
                continue
            set_strs.append(f"SET {k} = :{k}")
        update_sql += ", ".join(set_strs)
        update_sql += " WHERE id = :id"
        self.__connection.find_one(update_sql, entity_as_dict)
        return entity

    def delete(self, _id: int) -> None:
        if not self.exists(_id):
            return
        self.__connection.find_one("DELETE FROM users WHERE id = ?;", _id)

    def exists(self, _id: int) -> bool:
        return self.__connection.find_one("SELECT * FROM users WHERE id = ?;", (_id,)) is not None