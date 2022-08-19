from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, SessionBase
from contextlib import contextmanager


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()  # transaction
        except Exception as e:
            self.session.rollback()  # rollback
            raise e


db = SQLAlchemy(session_options={"expire_on_commit": False})