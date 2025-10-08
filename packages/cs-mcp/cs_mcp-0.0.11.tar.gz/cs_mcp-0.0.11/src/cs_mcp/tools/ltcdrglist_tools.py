from datetime import datetime
from typing import Annotated, Any, Literal
from fastmcp import FastMCP
from pydantic import Field
from cs_mcp.db.services import ltcdrg_service
from cs_mcp.tools.types import ChartNumberType, EymdType, InpatientGroupType, LdlItemType, SymdType


def ltcdrglist_tools(mcp: FastMCP[Any]):
  @mcp.tool()
  async def search_ltcdrg_items(
          symd: SymdType,
          eymd: EymdType,
          items: list[LdlItemType]):
    """
    장기요양 점검표에서 지정한 기간(symd~eymd) 내에 특정 항목(item)이 존재하는 경우를 조회합니다.
    """

    return await ltcdrg_service.search_ltcdrg_items(symd, eymd, items)

  @mcp.tool()
  async def get_adl_scores(
      charts: Annotated[list[ChartNumberType], Field(description="차트번호 목록")],
      symd: SymdType,
      eymd: EymdType,
  ):
    """장기요양 ADL 점수 조회

    args:
        charts:
          - 차트번호 목록
          - 빈 목록([])일 경우, 지정된 기간의 모든 환자 조회
    """

    return await ltcdrg_service.get_adl_scores(charts, symd, eymd)

  @mcp.tool()
  async def compare_ltcdrg(
      id_a: Annotated[int, Field(description="비교할 ID")],
      id_b: Annotated[int, Field(description="비교할 ID")],
  ):
    """장기요양점검표를 비교합니다.

    Args:
        id_a: First record ID.
        id_b: Second record ID.

    Output:
        Markdown table showing only the fields with different values, including field descriptions.
    """

    return await ltcdrg_service.compare_ltcdrg(id_a, id_b)

  @mcp.tool()
  async def get_ltcdrg_dates(
      chart_number: ChartNumberType,
  ):
    """특정 환자의 장기요양정검표 작성날짜를 조회합니다.

    args:
        chart_number: 차트번호(8자리 숫자)
    returns:
        Id: ID
        일자: 작성일자
        유형: 유형
    """
    return await ltcdrg_service.get_ltcdrg_dates(chart_number)

  @mcp.tool()
  async def compare_adl(
      symd_a: Annotated[str, Field(description="StartDate A(YYYYMMMM)", max_length=8)],
      eymd_a: Annotated[str, Field(description="EndDate A(YYYYMMMM)", max_length=8)],
      symd_b: Annotated[str, Field(description="StartDate B(YYYYMMMM)", max_length=8)],
      eymd_b: Annotated[str, Field(description="EndDate B(YYYYMMMM)", max_length=8)],
      status: Literal["Increase", "Decrease", "Unchanged"] = "Increase",
  ):
    """장기요양점검표 ADL 점수를 비교합니다.

    args:
      status: Status of comparison, "Increase" (default), "Decrease", or "Unchanged".
        - "Increase": Show records where ADL score increased from period A to B.
        - "Decrease": Show records where ADL score decreased from period A to B.
        - "Unchanged": Show records where ADL score remained the same from period A to B.
    """

    return await ltcdrg_service.compare_adl(symd_a, eymd_a, symd_b, eymd_b, status)

  @mcp.tool()
  async def get_inpatient_groups(
      symd: Annotated[str, Field(description="StartDate(YYYYMMMM)", max_length=8)],
      eymd: Annotated[str, Field(description="EndDate(YYYYMMMM)", max_length=8)],
      group: InpatientGroupType,
  ):
    """특정 기간 내 장기요양 입원군(군 분류)을 조회합니다.

    args:
        group: 장기요양 의료 등급 선택
            - None (default): 모든 등급 조회
            - "최고도": 최고도 등급
            - "고도": 고도 등급
            - "중도": 중도 등급
            - "경도": 경도 등급
            - "선택입원": 선택입원 등급
    returns:
        Markdown table with 차트번호, 시작일자, 장기요양등급, 군 분류
    """

    return await ltcdrg_service.get_inpatient_groups(symd, eymd, group)

  @mcp.tool()
  async def compare_inpatient_group(
      symd_a: Annotated[str, Field(description="StartDate A(YYYYMMMM)", max_length=8)],
      eymd_a: Annotated[str, Field(description="EndDate A(YYYYMMMM)", max_length=8)],
      group_a: InpatientGroupType,
      symd_b: Annotated[str, Field(description="StartDate B(YYYYMMMM)", max_length=8)],
      eymd_b: Annotated[str, Field(description="EndDate B(YYYYMMMM)", max_length=8)],
      group_b: InpatientGroupType,
      status: Literal["Increase", "Decrease", "Unchanged"] = "Increase",
  ):
    """장기요양 입원군(군 분류)을 비교합니다.

    args:
      status: Status of comparison, "Increase" (default), "Decrease", or "Unchanged".
        - "Increase": 등급이 높아진 경우 (예: 고도 → 최고도)
        - "Decrease": 등급이 낮아진 경우 (예: 최고도 → 고도)
        - "Unchanged": 등급이 변경되지 않은 경우
    """

    return await ltcdrg_service.compare_inpatient_group(symd_a, eymd_a, group_a, symd_b, eymd_b, group_b, status)

  @mcp.tool()
  async def check_dementia_due_date(
      dementia_check_type: Literal["MMSE", "GDR", "CDS"] = "MMSE",
      reference: Annotated[str, Field(
          description="YYYYMMDD", max_length=8)] = datetime.now().strftime("%Y%m%d"),
      check_months: Annotated[int, Field(
          description="Check Terms(Default: 6 Months)", ge=1, le=12)] = 6,
      prior_to: Annotated[int, Field(
          description="마감 x일 전(Default: 14 days)", ge=1, le=30)] = 14,
  ):
    """장기요양점검표 치매검사 만료일자를 확인합니다.

    args:
      reference: 기준일자(Default 오늘 날짜)
      previousMonth: 이전 월 기간(Default 6개월)
      dueDays: 도래일수(Default 14일)

    **참고**: 별도 정보가 없는 경우, Default 값으로 사용
    """

    return await ltcdrg_service.check_dementia_due_date(dementia_check_type, reference, check_months, prior_to)
