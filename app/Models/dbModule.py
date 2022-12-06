import pymysql

class Database:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', user='root', password='test1234', db='testdb', charset='utf8')
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def makelocationtable(self):
        query = '''
            CREATE TABLE testtable(
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                lon FLOAT NOT NULL,
                lat FLOAT NOT NULL,
                util FLOAT NOT NULL,
                open TIME NOT NULL,
                close TIME NOT NULL
            );
        '''

    def addlocation(self, location_info): #c
        query = '''
            INSERT INTO testtable(lon, lat, util, open, close)
            VALUES(%s, %s, %s, %s, %s);
        '''
        self.cursor.execute(query, location_info)
        self.conn.commit()

    def getlocationlist(self): #r
        query = '''
            SELECT *
            FROM testtable;
        '''
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        return result

    def deletelocationlist(self): #d
        query = '''
            DELETE FROM testtable;
        '''
        self.cursor.execute(query)
        self.conn.commit()
       



# Database의 객체만 만들면 서버생성,커서생성 자동으로해주고
# 커서에명령어입력하는것만 따로 떼어낸 클래스임

# M단에서는 C단에서 필요로되는 기능에 맞춰서 DB데이터를 정리해서 보내줌
# 주의할점이 DB데이터 자체를 쌩으로보내는것이 아니라 
# 목적에맞게 db데이터를 '정리'까지 다해서 ready-to-go로 리턴한다는것
