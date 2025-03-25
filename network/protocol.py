from typing import Any, Dict
from utils import to_mysql_time_format_with_ms, to_mysql_datetime_format

# 기본 통신 프로토콜 정의
ENCODING = "utf-8"
BUFFER_SIZE = 4096

# 요청 메시지 생성
def make_request(command: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "command": command,
        "payload": payload
    }

# 응답 메시지 생성 (기본 성공 응답)
def make_success_response(data: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "resultCode": 1000,
        "resultMsg": "SUCCESS",
        "data": data or {}
    }

# 응답 메시지 생성 (오류 응답)
def make_error_response(code: int, msg: str) -> Dict[str, Any]:
    return {
        "resultCode": code,
        "resultMsg": msg
    }
