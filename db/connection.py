import mysql.connector
from mysql.connector import Error
from core.settings import DB_CONFIG

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True, buffered=True)
            print("[DB] 연결 성공")
        except Error as e:
            print(f"[DB] 연결 실패: {e}")
            self.conn = None

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("[DB] 연결 종료")

    def execute(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            return self.cursor
        except Error as e:
            print(f"[DB] 쿼리 실행 오류: {e}")
            return None

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def lastrowid(self):
        return self.cursor.lastrowid


