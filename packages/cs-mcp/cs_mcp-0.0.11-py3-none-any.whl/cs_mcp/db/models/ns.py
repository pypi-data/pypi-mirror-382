from typing import Optional 
from sqlalchemy import String

from cs_mcp.db.models.base import Base
from cs_mcp.db.sqlalchemy import mc, M


class Ns(Base):
  __tablename__ = "ns"  # type: ignore

  ns_auto: M[Optional[int]] = mc(
      default=None, primary_key=True, autoincrement=True
  )
  ns_chart: M[str] = mc(String(8))
  ns_ymd: M[str] = mc(String(50))
  ns_neyong1: M[str] = mc()
  ns_neyong2: M[str] = mc()
