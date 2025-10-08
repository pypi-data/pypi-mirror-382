from cs_mcp.configs import config
from cs_mcp.tools import advice_tools, jy_tools, ltcdrglist_tools, patient_info_tools, ns_tools, progress_note_tools, util_tools, vs_tools


def run_mcp():
  from fastmcp import FastMCP

  mcp = FastMCP("ClickMCP")

  patient_info_tools(mcp)
  advice_tools(mcp)
  ltcdrglist_tools(mcp)
  ns_tools(mcp)
  vs_tools(mcp)
  progress_note_tools(mcp)
  jy_tools(mcp)
  util_tools(mcp)
  if config.IS_DEBUG:
    mcp.run(
        transport="streamable-http",
        path="/mcp",  # Adjust the path as needed
        port=8001,
    )
  else:
    mcp.run(
        transport="stdio",  # Use stdio for standard input/output
    )
