from typing import Optional
from pydantic import BaseModel, Field


class BatchVitalSignData(BaseModel):
  hulap2: Optional[str] = Field(
      default=None, description="수축기 혈압(hulap2)")
  hulap1: Optional[str] = Field(
      default=None, description="이완기 혈압(hulap1)")
  maekbak: Optional[str] = Field(default=None, description="맥박(maekbak)")
  hohup: Optional[str] = Field(default=None, description="호흡수(hohup)")
  cheon: Optional[str] = Field(default=None, description="체온(cheon)")
  weight: Optional[str] = Field(default=None, description="체중(weight)")
  height: Optional[str] = Field(default=None, description="신장(height)")
  spo2: Optional[str] = Field(default=None, description="산소포화도(spo2)")
  # intake 필드의 description이 "맥박 산소포화도"로 되어 있는데, 보통 "섭취량"을 의미합니다. 확인 필요.
  # spo2와 중복되는 것 같습니다. 만약 섭취량이라면 description을 수정하세요.
  intake: Optional[str] = Field(
      default=None, description="섭취량(intake) 또는 다른 의미라면 수정"
  )
  urine: Optional[str] = Field(default=None, description="소변량(urine)")
  blood: Optional[str] = Field(default=None, description="혈액량(blood)")
  aspiration: Optional[str] = Field(
      default=None, description="흡인량(aspiration)"
  )
  drainage: Optional[str] = Field(
      default=None, description="배액량(drainage)")
  vomitus: Optional[str] = Field(
      default=None, description="구토량(vomitus)")
