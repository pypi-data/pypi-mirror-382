from sqlalchemy import String
from cs_mcp.db.models.base import Base
from typing import Optional
from cs_mcp.db.sqlalchemy import mc, M


class Wj(Base):
  __tablename__ = "wj"  # type: ignore

  wj_auto: M[Optional[int]] = mc(
      default=None, primary_key=True, autoincrement=True
  )
  wj_chart: M[str] = mc(String(8))
  wj_suname: M[str] = mc(String(50))
  wj_birthday: M[str] = mc(String(8))
