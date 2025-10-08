
from typing import Any
from fastmcp import FastMCP
import pandas as pd
from sqlalchemy import select

from cs_mcp.db.dependencies import get_db
from cs_mcp.tools.types import SymdType, ChartNumberType, EymdType


def progress_note_tools(mcp: FastMCP[Any]):
  @mcp.tool()
  async def get_progressnotes(
      chart: ChartNumberType,
      symd: SymdType,
      eymd: EymdType,
  ):
    """차트번호로 경과기록을 가져온다."""
    from cs_mcp.db.models import ProgressNote

    async with get_db() as session:

      # session 에서 wj 객체를 가져온다.
      progress = await session.execute(
          select(ProgressNote).where(
              (ProgressNote.prog_chart == chart)
              & (ProgressNote.prog_ymd >= symd)
              & (ProgressNote.prog_ymd <= eymd)
              & (ProgressNote.prog_dc != "1")
              & (ProgressNote.prog_gubun == "A")
          )
      )
      progresses = progress.scalars().all()

    datas = [
        {
            "일자": prog.prog_ymd,
            "작성자": prog.prog_username,
            "내용": prog.prog_progress,
        }
        for prog in progresses
    ]
    df = pd.DataFrame(datas)
    return df.to_markdown(index=False)
