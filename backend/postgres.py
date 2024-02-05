from datetime import date, datetime

from _decimal import Decimal
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import (
    ColumnProperty,
    DeclarativeBase,
    sessionmaker,
)

from backend.settings import settings
from sqlalchemy import select
from sqlalchemy.orm import Session

SQLALCHEMY_DATABASE_URI = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"  # pylint: disable=line-too-long

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=30,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    Base class for all Schemas
    """

    @classmethod
    def get_one(cls, db: Session, item_id: int):
        return db.execute(select(cls).filter(cls.id == item_id)).scalar_one()

    def dict(self):
        attr = [
            prop.key
            for prop in inspect(self.__class__).iterate_properties
            if isinstance(prop, ColumnProperty)
        ]

        d = {k: getattr(self, k) for k in attr}
        for k, v in d.items():
            if isinstance(v, (date, datetime)):
                d[k] = v.isoformat()
            if isinstance(v, Decimal):
                d[k] = f"{v.normalize():f}"
        return d


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
