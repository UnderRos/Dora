# interface/log.py

from db.models import Log
from db.query import insert_log

def handle_log_write(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        log_type = payload.get("logType")
        timestamp = payload.get("timestamp")
        detail = payload.get("detail")
        location = payload.get("location")
        device_info = payload.get("deviceInfo")
        error_code = payload.get("errorCode")
        ip_address = payload.get("ipAddress")

        if not (user_id and log_type and timestamp):
            return {"result": "fail", "reason": "필수 정보 누락"}

        log = Log(
            log_id=None,
            user_id=user_id,
            log_type=log_type,
            timestamp=timestamp,
            detail=detail,
            location=location,
            device_info=device_info,
            error_code=error_code,
            ip_address=ip_address
        )

        log_id = insert_log(log)

        return {
            "result": "success",
            "logId": log_id,
            "errorCode": error_code,
            "ipAddress": ip_address,
            "deviceInfo": device_info
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}
