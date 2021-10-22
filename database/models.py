from typing import Union


class Model:
    def execute(self, query: str, *params) -> None:
        raise NotImplementedError()

    def commit(self) -> None:
        raise NotImplementedError()

    def connected(self) -> bool:
        raise NotImplementedError()

    def error(self) -> str:
        raise NotImplementedError()

    def fetchone(self, as_dict: bool) -> Union[list, dict]:
        raise NotImplementedError()

    def fetchall(self, as_dict: bool) -> Union[list, dict]:
        raise NotImplementedError()


class PostgreSQLModel (Model):
    def __init__(self, database: str, user: str, password: str, host: str):
        import psycopg2
        try:
            self.connection = psycopg2.connect(dbname=database, user=user, password=password, host=host)
            self.cursor = self.connection.cursor()
            self.connected_flag = not self.connection.closed
        except Exception as ex:
            self.error_str = str(ex)
            self.connected_flag = False

    def execute(self, query: str, *params) -> None:
        if len(params) != 0:
            query = query.format(*params)
        self.cursor.execute(query)

    def commit(self) -> None:
        self.connection.commit()

    def connected(self) -> bool:
        return self.connected_flag

    def error(self) -> str:
        return self.error_str


class SQLLiteModel (Model):
    def __init__(self, db_file):
        import sqlite3
        try:
            self.connection = sqlite3.connect(db_file)
            self.cursor = self.connection.cursor()
            self.connected_flag = True
        except Exception as ex:
            self.error_str = str(ex)
            self.connected_flag = False

    def execute(self, query: str, *params) -> None:
        if len(params) != 0:
            query = query.format(*params)
        self.cursor.execute(query)

    def commit(self) -> None:
        self.connection.commit()

    def connected(self) -> bool:
        return self.connected_flag

    def error(self) -> str:
        return self.error_str

    def fetchone(self, as_dict: bool) -> Union[list, dict]:
        values = self.cursor.fetchone()
        if as_dict:
            names = [description[0] for description in self.cursor.description]
            return dict(zip(names, values))
        else:
            return values

    def fetchall(self, as_dict: bool) -> Union[list, dict]:
        values = self.cursor.fetchall()
        if as_dict:
            lst = []
            names = [description[0] for description in self.cursor.description]
            for value in values:
                lst.append(dict(zip(names, value)))
            return lst
        else:
            return values
