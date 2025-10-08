from datetime import datetime, timedelta, timezone
from typing import Any
from fastmcp import FastMCP

import json
from typing import Annotated, Literal
from pydantic import Field
from cs_mcp.libs import temp_dict


def util_tools(mcp: FastMCP[Any]):
  @mcp.tool()
  async def get_today():
    """현재 일시를 반환합니다. 시간 정보가 필요한데 없으면 이 툴을 호출하세요.

    다음 키워드에 주로 사용:
    - 현재
    - 이번(주, 달)    
    - 오늘
    - 지금
    """
    # 한국 표준시 (KST, UTC+9)로 현재 시간 출력
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y.%m.%d %H:%M:%S")

  @mcp.tool()
  async def clear_temp():
    """TempKey를 사용 시 메모리를 해제합니다. 반드시 마지막에 한번만 호출하세요."""
    temp_dict.clear()
    return {"status": "cleared"}

  @mcp.tool()
  async def compare_two_files(
      temp_key_a:  Annotated[str, Field(description="첫 번째 TempKey")],
      temp_key_b: Annotated[str, Field(description="두 번째 TempKey")],
      # 차집합,교집합 매개변수
      kind: Annotated[
          Literal["intersection", "only_in_a", "only_in_b"], Field(
          description="분석할 집합의 종류 (intersection: 두 집합 모두에 있는 값, only_in_a: 첫 번째 집합에만 있는 값, only_in_b: 두 번째 집합에만 있는 값)")]
  ):
    """두 TempKey에 해당하는 데이터를 비교하여 intersection or 차집합을 분석합니다."""
    a = temp_dict.get(temp_key_a)
    b = temp_dict.get(temp_key_b)
    if a is None or b is None:
      return {"error": "Invalid TempKey"}
    a_set = set(a)
    b_set = set(b)

    result = []
    if kind == "intersection":
      intersection = list(a_set & b_set)
      result = {"intersection": intersection}
    elif kind == "only_in_a":
      only_in_a = list(a_set - b_set)
      result = {"only_in_a": only_in_a}
    elif kind == "only_in_b":
      only_in_b = list(b_set - a_set)
      result = {"only_in_b": only_in_b}

    return f"""결과:
{json.dumps(result, ensure_ascii=False, indent=2)}

---
모든 작업이 완료되면 반드시 "clear_temp" 툴을 호출하여 메모리를 해제하세요.
"""
