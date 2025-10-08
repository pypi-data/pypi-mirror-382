from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# 1. MetaData 객체 생성 시 schema 지정
#    (모든 테이블이 동일한 스키마를 공유할 경우)
SCHEMA_NAME = "cs2002"
metadata = MetaData(schema=SCHEMA_NAME)


class Base(DeclarativeBase):
  metadata = metadata

  def to_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}