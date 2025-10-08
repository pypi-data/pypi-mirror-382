from typing import Any, Callable
import pandas as pd
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from datetime import datetime
from dateutil.relativedelta import relativedelta

from cs_mcp.constants import inpatient_group_dict, ldl_description_dict, ldl_item_dict, ldl_keys
from cs_mcp.db.dependencies import get_db
from cs_mcp.db.models import LtcDrgList
from cs_mcp.tools.types import InpatientGroupType, LdlItemType


async def get_ltcdrg_items(symd: str, eymd: str, field: Any, where: Callable[[], Any]):
  async with get_db() as session:
    query = select(LtcDrgList) \
        .where(LtcDrgList.ldl_startymd >= symd) \
        .where(LtcDrgList.ldl_startymd <= eymd) \
        .where(LtcDrgList.ldl_index == "0") \
        .where(where()) \
        .options(load_only(LtcDrgList.ldl_chart, LtcDrgList.ldl_startymd, field))
    result = await session.scalars(query)
    return result.all()


async def get_ltcdrg_by_id(session: AsyncSession, id: int):
    # session 에서 wj 객체를 가져온다.
  ldl = await session.scalar(
      select(LtcDrgList)
      .where((LtcDrgList.ldl_auto == id))
  )
  return ldl


async def get_adl_scores(charts: list[str], symd: str, eymd: str):
  async with get_db() as session:
    query = select(LtcDrgList).where(
        (LtcDrgList.ldl_startymd >= symd)
        & (LtcDrgList.ldl_startymd <= eymd)
        & (LtcDrgList.ldl_index == "0")
        & (LtcDrgList.ldl_adl > 0)
        & (LtcDrgList.ldl_dc != "1")
    )
    if charts:
      query = query.where(LtcDrgList.ldl_chart.in_(charts))
    query.options(load_only(LtcDrgList.ldl_chart,
                  LtcDrgList.ldl_startymd, LtcDrgList.ldl_adl))

    ldls = await session.scalars(query)
    ldl_list = [(ldl.ldl_chart, ldl.ldl_startymd, ldl.ldl_adl)
                for ldl in ldls if (not charts or ldl.ldl_chart in charts)]
    df = pd.DataFrame(ldl_list, columns=["차트번호", "시작일자", "ADL"])
    return df.to_markdown(index=False)


async def get_ltcdrg_dates(chart: str):
  async with get_db() as session:
    # session 에서 wj 객체를 가져온다.
    ldls = await session.scalars(
        select(LtcDrgList)
        .where(
            (LtcDrgList.ldl_chart == chart) & (
                LtcDrgList.ldl_dc != "1")
        )
        .order_by(desc(LtcDrgList.ldl_startymd))
        .options(
            load_only(
                LtcDrgList.ldl_auto, LtcDrgList.ldl_startymd, LtcDrgList.ldl_yuhyung
            )
        )
    )
    return [
        {"Id": ldl.ldl_auto, "일자": ldl.ldl_startymd, "유형": ldl.ldl_yuhyung}
        for ldl in ldls
    ]


async def compare_ltcdrg(id_a: int, id_b: int):
  async with get_db() as session:
    # session 에서 wj 객체를 가져온다.
    ldl_a = await get_ltcdrg_by_id(session, id_a)
    ldl_b = await get_ltcdrg_by_id(session, id_b)

    if ldl_a is None or ldl_b is None:
      return "비교할 장기요양점검표가 없습니다."

    # LDL 필드에 대한 설명을 담은 dictionary
    ldl_a_dict = ldl_a.to_dict()
    ldl_b_dict = ldl_b.to_dict()

    different_keys = []
    for key in ldl_keys:
      if ldl_a_dict.get(key) != ldl_b_dict.get(key):
        different_keys.append(key)

    data = {
        f"{ldl_a.ldl_startymd}({ldl_a.ldl_auto})": [
            ldl_a_dict[key] for key in different_keys
        ],
        f"{ldl_b.ldl_startymd}({ldl_b.ldl_auto})": [
            ldl_b_dict[key] for key in different_keys
        ],
        "description": [ldl_description_dict[key] for key in different_keys],
    }

    df = pd.DataFrame(data)

    return df.to_markdown(index=False)


async def search_ltcdrg_items(symd: str, eymd: str, items: list[LdlItemType]):
  item_dict: dict[str, dict[str, Any]] = {}

  field_names = set[str]()
  for item in items:
    field_name = ldl_item_dict[item]
    field_names.add(field_name)
    field = getattr(LtcDrgList, field_name)

    result = []
    if item == "장기요양등급" or item == "망상" or item == "혼수" or item == "단기기억력장애" or item == "인식기술" or item == "이해시키는능력" or item == "의사표현" or item == "섬망":
      result = await get_ltcdrg_items(symd, eymd, field, where=lambda: field > "0")

    for r in result:
      key = f"{r.ldl_chart}_{r.ldl_startymd}"
      if key in item_dict:
        item_dict[key] = {**item_dict[key],
                          field_name: getattr(r, field_name)}
      else:
        item_dict[key] = {field_name: getattr(r, field_name)}

    result = [(row.ldl_chart, row.ldl_startymd, getattr(row, field_name))
              for row in result]
    # return result

  result_arrs = []
  for key, item in item_dict.items():
    chart, startymd = key.split("_")

    value_arr = []
    for field_name in field_names:
      value_arr.append(item.get(field_name, "None"))

    result_arrs.append([chart, startymd, *value_arr])

  descriptions = [ldl_description_dict.get(
      field_name, "") for field_name in field_names]

  return pd.DataFrame(result_arrs, columns=["차트번호", "시작일자", *descriptions]).to_markdown(index=False)


async def get_ldl_with_adl(symd: str, eymd: str):
  async with get_db() as session:
    result = await session.scalars(
        select(LtcDrgList)
        .where(LtcDrgList.ldl_startymd >= symd)
        .where(LtcDrgList.ldl_startymd <= eymd)
        .where(LtcDrgList.ldl_adl > 0)
        .where(LtcDrgList.ldl_index == "0")
        .options(load_only(LtcDrgList.ldl_chart, LtcDrgList.ldl_startymd, LtcDrgList.ldl_adl))
    )
    return result.all()


async def compare_adl(symd_a: str, eymd_a: str, symd_b: str, eymd_b: str, status: str = "Increase"):
  # a월 데이터 조회
  list_a = await get_ldl_with_adl(symd_a, eymd_a)
  list_b = await get_ldl_with_adl(symd_b, eymd_b)

  charts = {ldl.ldl_chart for ldl in list_a} | {
      ldl.ldl_chart for ldl in list_b}

  records = []

  for chart in charts:
    a_scores = [
        (ldl.ldl_startymd, ldl.ldl_adl) for ldl in list_a if ldl.ldl_chart == chart and ldl.ldl_adl]
    b_scores = [
        (ldl.ldl_startymd, ldl.ldl_adl) for ldl in list_b if ldl.ldl_chart == chart and ldl.ldl_adl]

    if a_scores:
      max_a = max(a_scores, key=lambda x: x[1])
      a_startymd, max_a_score = max_a
    else:
      a_startymd, max_a_score = "", 0

    if b_scores:
      max_b = max(b_scores, key=lambda x: x[1])
      b_startymd, max_b_score = max_b
    else:
      b_startymd, max_b_score = "", 0

    if status == "Increase":
      if a_scores and b_scores and max_b_score > max_a_score:
        records.append(
            (chart, a_startymd, max_a_score, b_startymd, max_b_score))
    elif status == "Decrease":
      if a_scores and b_scores and max_b_score < max_a_score:
        records.append(
            (chart, a_startymd, max_a_score, b_startymd, max_b_score))
    else:  # Unchanged
      if a_scores and b_scores and max_b_score == max_a_score:
        records.append(
            (chart, a_startymd, max_a_score, b_startymd, max_b_score))

  df = pd.DataFrame(
      records, columns=["차트번호", "A 시작일자", "A ADL", "B 시작일자", "B ADL"])
  return df.to_markdown(index=False)


async def get_ldl_with_inpatient_group(symd: str, eymd: str, grade_code: str = ""):
  async with get_db() as session:
    query = select(LtcDrgList)
    query = query.where(LtcDrgList.ldl_startymd >= symd)
    query = query.where(LtcDrgList.ldl_startymd <= eymd)
    query = query.where(LtcDrgList.ldl_etc4 != "")
    query = query.where(LtcDrgList.ldl_index == "0")
    if grade_code:
      query = query.where(LtcDrgList.ldl_etc4.like(f"{grade_code}%"))
    query = query.options(load_only(LtcDrgList.ldl_chart,
                          LtcDrgList.ldl_startymd, LtcDrgList.ldl_etc4))
    result = await session.scalars(query)
    return result.all()


async def compare_inpatient_group(symd_a: str, eymd_a: str, group_a: str, symd_b: str, eymd_b: str, group_b: str, status: str = "Increase"):
  # 등급 점수 (높은 등급일수록 높은 점수)
  grade_score = {"A1": 5, "A2": 4, "A3": 3, "A6": 2, "A7": 1}

  a_code = inpatient_group_dict.get(group_a, "")
  b_code = inpatient_group_dict.get(group_b, "")

  # a월 데이터 조회 (group_a에 해당하는 등급만)
  list_a = await get_ldl_with_inpatient_group(symd_a, eymd_a, a_code)

  list_b = await get_ldl_with_inpatient_group(symd_b, eymd_b, b_code)

  charts = {ldl.ldl_chart for ldl in list_a} | {
      ldl.ldl_chart for ldl in list_b}

  records = []

  for chart in charts:
    a_grades = [
        (ldl.ldl_startymd, ldl.ldl_etc4) for ldl in list_a if ldl.ldl_chart == chart and ldl.ldl_etc4]
    b_grades = [
        (ldl.ldl_startymd, ldl.ldl_etc4) for ldl in list_b if ldl.ldl_chart == chart and ldl.ldl_etc4]

    if a_grades:
      # 가장 최근 등급 (startymd가 큰 것)
      latest_a = max(a_grades, key=lambda x: x[0])
      a_startymd, a_grade = latest_a
      a_level = grade_score.get(a_grade[:2], 0)  # A1, A2 등
    else:
      a_startymd, a_grade, a_level = "", "", 0

    if b_grades:
      latest_b = max(b_grades, key=lambda x: x[0])
      b_startymd, b_grade = latest_b
      b_level = grade_score.get(b_grade[:2], 0)
    else:
      b_startymd, b_grade, b_level = "", "", 0

    if status == "Increase":
      # 등급이 높아짐 (점수가 높아짐)
      if a_grades and b_grades and b_level > a_level:
        records.append((chart, a_startymd, a_grade, b_startymd, b_grade))
    elif status == "Decrease":
      # 등급이 낮아짐 (점수가 낮아짐)
      if a_grades and b_grades and b_level < a_level:
        records.append((chart, a_startymd, a_grade, b_startymd, b_grade))
    else:  # Unchanged
      if a_grades and b_grades and b_level == a_level:
        records.append((chart, a_startymd, a_grade, b_startymd, b_grade))

  df = pd.DataFrame(
      records, columns=["차트번호", "A 시작일자", "A 등급", "B 시작일자", "B 등급"])
  return df.to_markdown(index=False)


async def get_inpatient_groups(symd: str, eymd: str, group: InpatientGroupType):
  code = inpatient_group_dict.get(group, "")
  async with get_db() as session:
    query = (
        select(LtcDrgList)
        .where(LtcDrgList.ldl_startymd >= symd)
        .where(LtcDrgList.ldl_startymd <= eymd)
        .where(LtcDrgList.ldl_etc4 != "")
        .where(LtcDrgList.ldl_index == "0")
        .where(LtcDrgList.ldl_etc4.like(f"{code}%"))
        .options(load_only(LtcDrgList.ldl_chart, LtcDrgList.ldl_startymd, LtcDrgList.ldl_etc4))
    )
    result = await session.scalars(query)
    ldl_list = [
        (ldl.ldl_chart, ldl.ldl_startymd, ldl.ldl_etc4)
        for ldl in result
    ]
    total_count = len(ldl_list)
    unique_patients = len(set(chart for chart, _, _ in ldl_list))
    df = pd.DataFrame(ldl_list, columns=["차트번호", "시작일자", "분류코드"])
    summary = f"총 수량: {total_count}\n환자수: {unique_patients}\n\n"
    return summary + df.to_markdown(index=False)


async def check_dementia_due_date(
    dementia_check_type: str,
    reference: str,
    check_months: int,
    prior_to: int,
):
    """장기요양점검표 치매검사 만료일자를 확인합니다."""

    field_dict = {
        "MMSE": {
            "yn": "ldl_c6_a",
            "date": "ldl_c6_b2"
        },
        "CDR": {
            "yn": "ldl_c7_a",
            "date": "ldl_c7_b2"
        },
        "GDS": {
            "yn": "ldl_c7_c",
            "date": "ldl_c7_d2"
        },
    }
    fields = field_dict[dementia_check_type]
    yn_field = fields['yn']
    date_field = fields['date']

    yn_attr = getattr(LtcDrgList, yn_field)
    date_attr = getattr(LtcDrgList, date_field)

    # 6개월 전 날짜 계산
    reference_date = datetime.strptime(reference, "%Y%m%d").date()
    reference_date = reference_date - relativedelta(months=check_months)
    symd = reference_date.strftime("%Y%m%d")

    async with get_db() as session:
      query = select(LtcDrgList).where(
          (yn_attr == "1") &
          (date_attr != None) &
          (date_attr != "") &
          (LtcDrgList.ldl_dc != "1") &
          (LtcDrgList.ldl_startymd > symd) &
          (LtcDrgList.ldl_startymd <= reference)
      ).options(load_only(LtcDrgList.ldl_chart, LtcDrgList.ldl_startymd, date_attr))
      results = await session.scalars(query)

      custom_datas = []
      for r in results:
        date = getattr(r, date_field)
        due_date = datetime.strptime(
            date, "%Y%m%d").date() + relativedelta(months=check_months)

        # due_date - rdate 일수가 14일 보다 작거나 같은 경우
        if (due_date - reference_date).days <= prior_to:
          custom_datas.append({
              "차트번호": r.ldl_chart,
              "작성일자": r.ldl_startymd,
              f"{dementia_check_type} 검사일자": date,
              "만료일자": due_date.strftime("%Y%m%d"),
              "남은일수": (due_date - reference_date).days
          })

      # custom_datas 를 pd table 로 변환
      df = pd.DataFrame(custom_datas)
      if df.empty:
        return "조회된 데이터가 없습니다."
      df = df.sort_values(by=["남은일수", "차트번호"])
      return df.to_markdown(index=False)
