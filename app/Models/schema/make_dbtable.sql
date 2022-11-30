CREATE DATABASE travel_planner_db DEFAULT CHARACTER SET UTF8;

USE travel_planner_db;

CREATE TABLE locationtable(
    id          INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    latitude    FLOAT(24) NOT NULL,
    longitude   FLOAT(24) NOT NULL
) CHARSET=utf8;

/* 
sql문을 작성할때는 절대 -를 명명할때 쓰면안된다. travel-planner이라고 했다가 개고생함
또, 이 sql파일을 cmd에서 실행할때 source C:/Users/dive2bass01/github/travel-planner/app/schema/make_dbtable.sql;
라고 적어줘야한다. 주의할점은 \이아니라 /라고 적어줘야한다는점, 맨마지막에 ; 이들어간다는점이다
*/
