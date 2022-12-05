import pymysql

class Database:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', user='root', password='test1234', db='testdb', charset='utf8')
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def execute(self, query, args={}):
        self.cursor.execute(query, args)
    
    def execute_fetchone(self, query, args={}):
        self.cursor.execute(query, args)
        record = self.cursor.fetchone()
        return record
    
    def execute_fetchall(self, query, args={}):
        self.cursor.execute(query, args)
        record = self.cursor.fetchall()
        return record   
    
    def commit(self):
        self.db.commit()

# Database의 객체만 만들면 서버생성,커서생성 자동으로해주고
# 커서에명령어입력하는것만 따로 떼어낸 클래스임