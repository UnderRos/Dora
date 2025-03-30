from datetime import datetime

def to_mysql_time_format_with_ms(hms_str: str) -> str:
    dt = datetime.strptime(hms_str, "%H:%M:%S.%f")
    return dt.strftime("%H:%M:%S.%f")[:-3]

def to_mysql_datetime_format(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")
