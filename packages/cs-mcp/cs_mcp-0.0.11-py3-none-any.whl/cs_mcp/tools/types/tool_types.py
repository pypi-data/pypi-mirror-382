from typing import Annotated, Literal

from pydantic import Field


ChartNumberType = Annotated[str, Field(
    description="차트번호(8자리 숫자)", max_length=8)]
SymdType = Annotated[str, Field(description="시작일자(YYYYMMDD)", min_length=8, max_length=8)]
EymdType = Annotated[str, Field(description="종료일자(YYYYMMDD)", min_length=8, max_length=8)]

LdlItemType = Literal[
    "장기요양등급", "혼수", "섬망", "망상", "단기기억력장애",
              "인식기술", "이해시키는능력", "의사표현"]
InpatientGroupType = Annotated[
    Literal["최고도", "고도", "중도", "경도", "선택입원"],
    Field(description="장기요양 입원군"),
]
