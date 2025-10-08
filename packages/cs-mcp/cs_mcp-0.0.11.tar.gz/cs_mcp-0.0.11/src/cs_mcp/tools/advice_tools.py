import httpx

from typing import Annotated, Any
from fastmcp import FastMCP
from pydantic import Field


def advice_tools(mcp: FastMCP[Any]):
  @mcp.tool()
  async def advice_eclick(question: Annotated[str, Field(description="질문")], page: Annotated[int, Field(description="페이지", ge=1, le=3)] = 1):
    """
    eclick 질문에 대한 응답을 가져옵니다.

    만일 질문에 대한 정확한 응답이 없으면 페이지를 늘려서 조회하세요.
    """
    url = "https://ai.click-soft.co.kr/vector-store/api/advices"
    async with httpx.AsyncClient() as client:
      response = await client.post(url, json={"question": question, "page": page})
      response.raise_for_status()
    return response.json()
