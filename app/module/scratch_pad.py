import pymysql 

pwd = input()

conn = pymysql.connect(host='localhost', user='root', password=pwd, charset='utf8', db='testdb') 
cursor = conn.cursor(pymysql.cursors.DictCursor) 

sql = '''
    CREATE TABLE test_table(
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(256) NOT NULL,
        address VARCHAR(256) NOT NULL
    );
'''

insert_sql = '''
    INSERT INTO test_table(name, address)
    VALUES('lee', 'china');
'''

select_sql = '''
    SELECT *
    FROM test_table
    WHERE name = 'lee';    
'''

update_sql = '''
    UPDATE test_table
    SET address='spain'
    WHERE name='lee';
'''

cursor.execute(update_sql)


# result = cursor.fetchone()
# print(result)
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