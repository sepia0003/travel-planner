import pymysql

class Database:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', user='root', password='test1234', db='travel_planner_db', charset='utf8')
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        # 위conn은 유저와 어떤 database를 쓸지를 이미 대응시킨상태
        # 따라서 cmd에서 명령어치는것처럼 db명.table명으로 안쓰고바로 table명을 써도됨

    def maketable(self, tablename):
        query = '''
            CREATE TABLE {}(
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                lon VARCHAR(256) NOT NULL,
                lat VARCHAR(256) NOT NULL,
                util VARCHAR(256) NOT NULL,
                stay VARCHAR(256) NOT NULL,
                open VARCHAR(256) NOT NULL,
                close VARCHAR(256) NOT NULL
            );
        '''.format(tablename)
        self.cursor.execute(query)
        self.conn.commit()

    def addlocation(self, location_info): #c
        query = '''
            INSERT INTO locationtable(lon, lat, util, stay, open, close)
            VALUES(%s, %s, %s, %s, %s, %s);
        '''
        self.cursor.execute(query, location_info)
        self.conn.commit()

    def getlocationlist(self): #r
        query = '''
            SELECT *
            FROM locationtable;
        '''
        self.cursor.execute(query)
        fetchalllist = self.cursor.fetchall()
        # result = []
        # for ele in fetchalllist:
        #     result.append(list(ele.values()))
        result = fetchalllist

        return result

    def resetlocationlist(self): #d
        query = '''
            DELETE FROM locationtable;
        '''
        self.cursor.execute(query)
        self.conn.commit()

    def closeconn(self):
        self.conn.close()
       



# 유저(아이디+아이피+비번) 따로만들고
# database들과 그안의 table들을 따로만들고
# 유저와 database.table 을 대응시키는것
# *schema는 database와 같은말

# Database의 객체만 만들면 서버생성,커서생성 자동으로해주고
# 커서에명령어입력하는것만 따로 떼어낸 클래스임

# M단에서는 C단에서 필요로되는 기능에 맞춰서 DB데이터를 정리해서 보내줌
# 주의할점이 DB데이터 자체를 쌩으로보내는것이 아니라 
# 목적에맞게 db데이터를 '정리'까지 다해서 ready-to-go로 리턴한다는것

# "문자열 {2}문자열 문자열{0}문자열{1}".format(10, "str", "30") 이라고 포맷팅을하면
# "문자열 30문자열 문자열10문자열str" 이라고 정리가된다. 즉,
# {안}에는 뒤.format부분에서 가져올 요소의 인덱스를 집어넣고 (집어넣지않으면 자동으로 맨앞의{}부터 맨뒤의{}까지 0~증순으로 인덱스부여됨)
# .format(안)에 인덱스0부터 원하는 인덱스까지 증순으로 요소들을 ,를 사용해 입력해주면된다.
# -----------------------------
# 예를들면 "VALUES({}, {});".format(10, "str") 일때
# 먼저 format에서 받아온 인자중에 문자열이 아닌것을 모두 문자열로 바꾼다. 10->"10"
# 바꾼것 그대로 {}부분에 브레이크인한다.
# "VALUES(" + "10" + ", " + "str" + ");"
# = "VALUES(10, str);"
# !!주의 format으로 쿼리문 쓸때 주의할점은 만든 텍스트가 그대로 쿼리명령문이 된다는것이다.
# 원하는텍스트는 VALUES(10, "str"); 여야하는데 위는 그렇지 못하다.
# "VALUES({}, \"{}\");".format(10, "str") 이라고 \"를 필요한부분 앞뒤에 써줘야한다.

# sql문에서는 플레이스홀더로서 %s를 사용하여 execute의 두번째인자로 튜플을 받아와 입력가능하다
# 이 %s를 붙일수 있는부분은 위와다르게 실제 데이터밸류부분에만 들어갈수있다
# 테이블명이라던지 필드명이라던지 기타 텍스트를 대신해서 쓸수없다.
# 대신 위처럼 \" \"로 감싸주지않아도 된다.
# ------------------------------
# 예를들면 "VALUES(%s, %s);" execute(query, (10, "str")) 일때
# 먼저 execute에서 받아온 인자중에 문자열인것 앞뒤에 이스케이프문자\"를 붙여서 새로운 문자열로 만들고 "str" -> "\"str\""
# 그다음 문자열이 아닌것을 모두 문자열로 바꾼다 10->"10"
# 바꾼것 그대로 %s 부분에 브레이크인한다.
# "VALUES(" + "10" + ", " + "\"str\"" + ");"
# = "VALUES(10, \"str\");"
