import pandas as pd

from typing import Any
from fastmcp import FastMCP
from sqlalchemy import select

from cs_mcp.db.dependencies import get_db
from cs_mcp.db.models import Vs
from cs_mcp.tools.types import ChartNumberType, EymdType, SymdType


def vs_tools(mcp: FastMCP[Any]):
  @mcp.tool()
  async def get_vitalsigns(
      chart: ChartNumberType,
      symd: SymdType,
      eymd: EymdType,
  ):
    """차트번호로 바이탈사인을 가져온다."""

    async with get_db() as session:

      # session 에서 wj 객체를 가져온다.
      vitals = await session.execute(
          select(Vs).where(
              (Vs.vs_chart == chart) & (
                  Vs.vs_ymd >= symd) & (Vs.vs_ymd <= eymd)
          )
      )
      vitalsigns = vitals.scalars()

    data = [
        {
            "일자": vs.vs_ymd,
            "작성시간": vs.vs_time,
            "수축기 혈압": vs.vs_hulap2,
            "이완기 혈압": vs.vs_hulap1,
            "맥박": vs.vs_maekbak,
            "호흡수": vs.vs_hohup,
            "체온": vs.vs_cheon,
            "체중": vs.vs_weight,
            "신장": vs.vs_height,
            "산소포화도": vs.vs_spo2,
            "섭취량": vs.vs_intake,
            "소변량": vs.vs_urine,
            "혈액량": vs.vs_blood,
            "흡인량": vs.vs_aspiration,
            "배액량": vs.vs_drainage,
            "구토량": vs.vs_vomitus,
            "작성자": vs.vs_username,
        }
        for vs in vitalsigns
    ]

    df = pd.DataFrame(data)
    return df.to_markdown(index=False)

  # @mcp.tool()
  # def write_batch_vital_sign_tool(
  #     vs_data: dict[ChartNumberType, BatchVitalSignData],
  # ):
  #   """바이탈사인을 일괄 입력합니다.

  #   Args:
  #       vs_data: 차트번호를 키로 하고 바이탈사인 데이터를 값으로 하는 딕셔너리입니다.
  #           - 키: 환자의 차트번호(8자리 숫자)
  #           - 값: BatchVitalSignData 객체로 다음 필드를 포함할 수 있습니다:
  #               - hulap2: 수축기 혈압 (mmHg)
  #               - hulap1: 이완기 혈압 (mmHg)
  #               - maekbak: 맥박 (회/분)
  #               - hohup: 호흡수 (회/분)
  #               - cheon: 체온 (°C)
  #               - weight: 체중 (kg)
  #               - height: 신장 (cm)
  #               - spo2: 산소포화도 (%)
  #               - intake: 섭취량 (ml)
  #               - urine: 소변량 (ml)
  #               - blood: 혈액량 (ml)
  #               - aspiration: 흡인량 (ml)
  #               - drainage: 배액량 (ml)
  #               - vomitus: 구토량 (ml)

  #   Returns:
  #       str: 성공 시 "성공" 메시지를 반환합니다.

  #   Example:
  #       {"00000123": {"hulap2": "120", "hulap1": "80", "cheon": "36.5"}}
  #   """

  #   return "성공"
