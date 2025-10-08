
from typing import Annotated, Any
from fastmcp import FastMCP
from typing import Annotated
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import load_only
from cs_mcp.db.dependencies import get_db
from cs_mcp.db.models import Wj
from cs_mcp.tools.types import ChartNumberType


def patient_info_tools(mcp: FastMCP[Any]):
  @mcp.tool()
  async def get_birth_by_chartnum(
      chart: Annotated[str, Field(description="차트번호임.")],
  ) -> str:
    """생년월일을 가져온다. 차트번호를 불러오기 위해서는 get_chart_by_name 를 호출하시오.
    args:
        chart (str): 차트번호
    """

    print("get_birth_by_chartnum called:", chart)
    async with get_db() as session:

      # session 에서 wj 객체를 가져온다.
      wj = await session.execute(
          select(Wj)
          .where(Wj.wj_chart == chart)
          .options(load_only(Wj.wj_birthday))
      )

      wj = wj.scalar()
      return wj.wj_birthday if wj is not None else ""

  @mcp.tool()
  async def get_charts_by_name(name: str):
    """이름 정보로 차트번호를 가져온다.
    args:
        name (str): 이름
    """

    print(f"get_charts_by_name called: {name}")

    async with get_db() as session:

      # session 에서 wj 객체를 가져온다.
      wj = await session.execute(
          select(Wj)
          .where(Wj.wj_suname == name)
          .options(load_only(Wj.wj_chart))
      )
    return [wj.wj_chart for wj in wj.scalars()]

  @mcp.tool()
  async def get_name_by_chart(charts: Annotated[list[ChartNumberType], Field(description="차트번호 목록")]):
    """차트번호로 이름을 가져온다.
    args:
        charts (list[str]): 차트번호 목록
    returns:
        Markdown table with 차트번호 and 이름
    """

    print(f"get_name_by_chart called: {charts}")

    results = []
    async with get_db() as session:
      for chart in charts:
        # session 에서 wj 객체를 가져온다.
        wj = await session.scalar(
            select(Wj)
            .where(Wj.wj_chart == chart)
            .options(load_only(Wj.wj_suname))
        )
        name = wj.wj_suname if wj is not None else ""
        results.append([chart, name])

    import pandas as pd
    df = pd.DataFrame(results, columns=["차트번호", "이름"])
    return df.to_markdown(index=False)
