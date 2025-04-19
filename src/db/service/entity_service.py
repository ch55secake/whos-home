from src.db.data.entity import Entity
from src.db.db_connector import DatabaseConnector


class EntityService:
    def __init__(self, table_name: str, _type: type[Entity]) -> None:
        self._table: str = table_name
        self._type: type[Entity] = _type
        self._connection: DatabaseConnector = DatabaseConnector()
        self._connection.connect()

    def create(self, entity: Entity) -> None:
        entity_dict = entity.to_dict()
        cols = ", ".join(entity_dict.keys())
        vals = ", ".join([":" + k for k in entity_dict.keys()])
        sql = f"INSERT INTO {self._table} ({cols}) VALUES ({vals});"
        self._connection.find_all(sql, entity_dict)

    def read(self, _id: int) -> Entity | None:
        entity = self._connection.find_one(f"SELECT * FROM {self._table} WHERE id = ?;", (_id,))
        return self._type(**dict(entity)) if entity is not None else None

    def read_all(self) -> list[Entity]:
        rows = self._connection.find_all(f"SELECT * FROM {self._table};")
        return [self._type(**dict(row)) for row in rows]

    def update(self, entity: Entity) -> Entity | None:
        if not self.exists(entity.id):
            return None
        update_sql = f"UPDATE {self._table} "
        set_strs = []
        entity_as_dict = entity.to_dict()
        for k in entity_as_dict.keys():
            if k == "id":
                continue
            set_strs.append(f"SET {k} = :{k}")
        update_sql += ", ".join(set_strs)
        update_sql += " WHERE id = :id"
        self._connection.find_one(update_sql, entity_as_dict)
        return entity

    def delete(self, _id: int) -> None:
        if not self.exists(_id):
            return
        self._connection.find_one(f"DELETE FROM {self._table} WHERE id = ?;", (_id,))

    def exists(self, _id: int) -> bool:
        return self._connection.find_one(f"SELECT * FROM {self._table} WHERE id = ?;", (_id,)) is not None
