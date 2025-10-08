
from typing import Any
from fastmcp import FastMCP
import pandas as pd
from sqlalchemy import select

from cs_mcp.db.dependencies import get_db
from cs_mcp.db.models import Ns
from cs_mcp.tools.types import SymdType, ChartNumberType, EymdType


def ns_tools(mcp: FastMCP[Any]):
  @mcp.tool()
  async def search_nursing_record(
      chart: ChartNumberType,
      symd: SymdType,
      eymd: EymdType,
  ):
    """간호기록을 조회합니다.
       간호기간은 종료일자로부터 최대 1달로 제한합니다.

    args:
        chart: 차트번호(8자리 숫자)
        start: 시작일자(yyyyMMdd)
        end: 종료일자(yyyyMMdd)
    returns:
        일자: 기록일자
        간호문제: 간호문제
        간호처치: 간호처치
    """

    async with get_db() as session:

      # session 에서 wj 객체를 가져온다.
      ns = await session.execute(
          select(Ns).where(
              (Ns.ns_chart == chart)
              & (Ns.ns_ymd >= symd)
              & (Ns.ns_ymd <= eymd)
          )
      )
      nss = ns.scalars()

    datas = [
        {"일자": ns.ns_ymd, "간호문제:": ns.ns_neyong1, "간호처치": ns.ns_neyong2}
        for ns in nss
    ]

    df = pd.DataFrame(datas)
    return df.to_markdown(index=False)
