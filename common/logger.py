from datetime import datetime
from db.models import Log
from db.query import insert_log
from socket import gethostname

def log_to_db(user_id: int, log_type: str, detail: str = "",
              location: str = "desktop", device_info: str = "", error_code: str = None):
    log = Log(
        log_id=None,
        user_id=user_id,
        log_type=log_type,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        detail=detail,
        location=location,
        device_info=device_info or gethostname(),
        error_code=error_code,
        ip_address="127.0.0.1"  # 또는 실제 IP 조회 함수 사용
    )
    log_id = insert_log(log)
    print(f"[LOG] 저장됨 (log_id={log_id}, type={log_type})")
