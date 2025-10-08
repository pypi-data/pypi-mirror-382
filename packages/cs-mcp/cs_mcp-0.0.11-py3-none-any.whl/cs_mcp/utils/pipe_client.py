# from typing import Any, Literal, Optional
# from pydantic import BaseModel
# import win32file


# class PipeSendData(BaseModel):
#     """Data to be sent to the pipe."""

#     type: Literal["open_form", "load_chart", "ping", "write_progress_note", "write_batch_vital_sign"]
#     target: Optional[str] = None
#     message: Optional[str] = None
#     data: Optional[dict[str, Any]] = None


# class PipeClient:
#     def __init__(self, pipe_name="메인화면_pipe"):
#         self.pipe_name = rf"\\.\pipe\{pipe_name}"
#         self.pipe = None

#     def __enter__(self):
#         self.pipe = win32file.CreateFile(
#             self.pipe_name,
#             win32file.GENERIC_READ | win32file.GENERIC_WRITE,
#             0,
#             None,
#             win32file.OPEN_EXISTING,
#             0,
#             None,
#         )
#         return self  # with 문의 as 구문에 전달될 객체

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self.pipe:
#             self.pipe.close()  # type: ignore
#             self.pipe = None  # 파이프 닫았음을 명시

#     def read_message(self):
#         data: bytes
#         result, data = win32file.ReadFile(self.pipe, 4096)  # type: ignore
#         return data.decode("utf-8")

#     def send(self, data: PipeSendData):
#         win32file.WriteFile(self.pipe, data.model_dump_json().encode("utf-8"))  # type: ignore


# # with PipeServer("test_pipe") as pipe:
# #     # 응답 전송
# #     response = "서버에서 보낸 응답"
# #     pipe.send_message(response)
# #     print("응답 전송 완료")

# #     # 메시지 수신
# #     message = pipe.read_message()
# #     print(f"수신된 메시지: {message}")
