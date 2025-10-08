from typing import Type

from sqlalchemy import MetaData
from cs_mcp.db.models.jinryo.jy import Jy


class TableManager:
    def __init__(self):
        self._jy_cache = {}

    def get_jy(self, schema: str, ym: str) -> Type[Jy]:
        cache_key = f"{schema}.jy{ym}"

        # 캐시에서 확인
        if cache_key in self._jy_cache:
            return self._jy_cache[cache_key]

        # 새로운 Jy 클래스 생성
        class JyDynamic(Jy):
            metadata = MetaData(schema=schema)
            __tablename__ = f"jy{ym}"  # type: ignore

        # 캐시에 저장
        self._jy_cache[cache_key] = JyDynamic

        return JyDynamic
