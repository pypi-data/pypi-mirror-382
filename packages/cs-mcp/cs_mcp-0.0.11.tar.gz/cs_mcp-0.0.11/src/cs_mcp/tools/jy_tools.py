from typing import Annotated, Any
from fastmcp import FastMCP
from pydantic import Field
from sqlalchemy import and_, select

from cs_mcp.db.dependencies import get_db
from cs_mcp.db.models.table_manager import TableManager
from cs_mcp.tools.types import ChartNumberType



def jy_tools(mcp: FastMCP[Any]):
  @mcp.tool()
  async def get_jy(
      chart_number: ChartNumberType,
      saup: Annotated[str, Field(description="사업자", max_length=2)],
      isHanbang: Annotated[bool, Field(description="한방: True")],
      year_month: Annotated[str, Field(description="년월(YYYYMM)", max_length=6)],
      start_day: Annotated[
          str, Field(description="당월 기간 중 처음일(DD)", max_length=2)
      ],
      end_day: Annotated[
          str, Field(description="당월 기간 중 마지막일(DD)", max_length=2)
      ],
  ):
    """차트번호로 진료내역(처방내역)을 조회합니다."""
    async with get_db() as session:
      dbcode = "han" if isHanbang else "jinryo"
      dbname = f"{dbcode}{saup}"
      start_ymd = f"{year_month}{start_day}"
      end_ymd = f"{year_month}{end_day}"
      Jy = TableManager().get_jy(dbname, year_month)

      jy = await session.execute(
          select(Jy).where(
              (Jy.jy_chart == chart_number)
              & (Jy.jy_ymd >= start_ymd)
              & (Jy.jy_ymd <= end_ymd)
              & (Jy.jy_dc != "1")
          )
      )

      jys = jy.scalars().all()
    if not jys:
      return f"차트번호 {chart_number}에 해당하는 진료내역이 없습니다."

    return [
        {
            "id": jy.jy_auto,
            "진료일자": jy.jy_ymd,  # type: ignore
            "처방코드": jy.jy_yscode,
            "진료내용": jy.jy_myung,  # type: ignore
        }
        for jy in jys
    ]

  @mcp.tool()
  async def del_jy(
      chart_number: ChartNumberType,
      saup: Annotated[str, Field(description="사업자", max_length=2)],
      isHanbang: Annotated[bool, Field(description="한방: True")],
      year_month: Annotated[str, Field(description="년월(YYYYMM)", max_length=6)],
      ids: Annotated[list[int], Field(description="삭제할 진료내역 ID 목록")],
  ):
    """차트번호로 진료내역(처방내역)을 삭제합니다."""
    async with get_db() as session:
      dbcode = "han" if isHanbang else "jinryo"
      dbname = f"{dbcode}{saup}"
      Jy = TableManager().get_jy(dbname, year_month)

      jys = await session.scalars(
          select(Jy).where(
              and_(
                  Jy.jy_chart == chart_number,
                  Jy.jy_dc != "1",
                  Jy.jy_auto.in_(ids),  # type: ignore
              )
          )
      )

      if not jys:
        return f"차트번호 {chart_number}에 해당하는 진료내역이 없습니다."

      for jy in jys:
        jy.jy_dc = "1"
        session.add(jy)

      await session.commit()

    return f"차트번호 {chart_number}의 진료내역을 삭제했습니다."
