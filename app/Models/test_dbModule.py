import pymysql 

conn = pymysql.connect(host='localhost', user='root', password='test1234', charset='utf8', db='testdb') 
cursor = conn.cursor(pymysql.cursors.DictCursor) 

sql_db = '''
    CREATE DATABASE testdb DEFAULT CHARACTER SET UTF8;
'''

sql_table = '''
    CREATE TABLE testtable(
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(256) NOT NULL,
        address VARCHAR(256) NOT NULL
    );
'''

insert_sql = '''
    INSERT INTO testtable(name, address)
    VALUES('kim', 'korea');
'''

select_sql = '''
    SELECT *
    FROM testtable;    
'''

update_sql = '''
    UPDATE testtable
    SET address='spain'
    WHERE name='lee';
'''

cursor.execute(select_sql)


result = cursor.fetchall()
print(result)
# print(type(result))
conn.commit() 
conn.close() 

# 우선 mysql workbench에서 mysql서버를 만들고나서 시작(아이피,포트,비번 등등)
# 그리고 pymysql을 사용해 그 서버와 사용할db를(db를처음작성시엔 db인수필요없음)를 conn변수에 넣는다.
# 서버,db를담고있는 conn에대한 커서를 하나만들어주고 인제 그 커서를 사용해 쿼리를 입력한다.
# sql변수에 쿼리문을 "안에" 직접 써준다. 만약 줄이 여러개면 독스트링 '''안에''' 써준다.
# 그리고 해당커서위치에 execute명령문+위에서쓴쿼리문을 넣어줘서 실행시킨다.
# 서버,db에 커밋해서 변경사항저장후 close로 해당서버를 닫는다.
# (db가 처음부터 여러개있는게아니라, 서버안에 db가 여러개 있는형식이다)
# (그리고 db안에 테이블이 여러개있는 형식이다.)
# (pymysql을 쓰면 conn이라는 변수에 서버,db가 넣어져있게되므로 workbench없이도 python안에서 서버를 조작할수있기때문에 편리)

# fetchone()은 한 record에대한 field명(키)와 해당값(밸류)가 ,로이어져있는 딕셔너리형 1개출력
# fetchall()은 모든 record에대한 딕셔너리로 이루어진 리스트를 반환