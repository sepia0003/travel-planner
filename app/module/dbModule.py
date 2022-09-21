import pymysql

class Database:
    def __init__(self):
        self.db = pymysql.connect(host='localhost', user='root', password='test1234', db='travel_planner_db', charset='utf8')
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

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