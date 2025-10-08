from cs_mcp.db.models.base import Base
from typing import Optional
from cs_mcp.db.sqlalchemy import mc, M
from sqlalchemy import String


class ProgressNote(Base):
  __tablename__ = "progressnote"  # type: ignore

  prog_auto: M[Optional[int]] = mc(
      default=None, primary_key=True, autoincrement=True
  )
  prog_gubun: M[str] = mc(String(2))
  prog_saup: M[str] = mc(String(2))
  prog_weibgu: M[str] = mc(String(1))
  prog_chart: M[str] = mc(String(8))
  prog_yuhyung: M[str] = mc(String(2))
  prog_jinchal: M[str] = mc(String(2))
  prog_ymd: M[str] = mc(String(8))
  prog_ibymd: M[str] = mc(String(8))
  prog_dup: M[int] = mc()
  prog_time: M[Optional[str]] = mc(String(6), default=None)
  prog_progress: M[Optional[str]] = mc(default=None)
  prog_rtf: M[Optional[str]] = mc(default=None)
  prog_username: M[Optional[str]] = mc(String(20), default=None)
  prog_etc1: M[Optional[str]] = mc(String(255), default=None)
  prog_etc2: M[Optional[str]] = mc(String(255), default=None)
  prog_etc3: M[Optional[str]] = mc(String(255), default=None)
  prog_etc4: M[Optional[str]] = mc(String(255), default=None)
  prog_etc5: M[Optional[str]] = mc(String(255), default=None)
  prog_dc: M[str] = mc(String(1))
  prog_indate: M[Optional[str]] = mc(String(20), default=None)
  prog_update: M[Optional[str]] = mc(String(255), default=None)
  prog_dcdate: M[Optional[str]] = mc(String(255), default=None)
  prog_inuser: M[Optional[str]] = mc(String(20), default=None)
  prog_upuser: M[Optional[str]] = mc(String(20), default=None)
  prog_dcuser: M[Optional[str]] = mc(String(20), default=None)
  prog_insign: M[Optional[bytes]] = mc(default=None)
  prog_upsign: M[Optional[bytes]] = mc(default=None)
  prog_dcsign: M[Optional[bytes]] = mc(default=None)
  prog_incert: M[Optional[str]] = mc(default=None)
  prog_upcert: M[Optional[str]] = mc(default=None)
  prog_dccert: M[Optional[str]] = mc(default=None)
  prog_etc6: M[Optional[str]] = mc(String(255), default=None)
  prog_etc7: M[Optional[str]] = mc(String(255), default=None)
  prog_etc8: M[Optional[str]] = mc(String(255), default=None)
  prog_etc9: M[Optional[str]] = mc(String(255), default=None)
  prog_etc10: M[Optional[str]] = mc(String(255), default=None)
