# 为了测试时创建数据库及相应表格参数
import sqlite3

conn = sqlite3.connect('/mnt/e/device.db')
print ("Opened database successfully")
c = conn.cursor()


c.execute('''CREATE TABLE DEPARTMENT
       (deptid  TEXT(10)    PRIMARY KEY     NOT NULL,
       deptname           TEXT(30)    ); ''')
print ("Table department created successfully")

c.execute('''CREATE TABLE ADMIN
       (ID  TEXT(10)    PRIMARY KEY     NOT NULL,
       username           TEXT(30)    ,
       PASSWORD           TEXT(30)    NOT NULL,
       deptid    TEXT(10) ,
       FOREIGN KEY(deptid) REFERENCES  DEPARTMENT(deptid)); ''')
print ("Table admin created successfully")

c.execute('''CREATE TABLE USER
       (usertid  TEXT(10)    PRIMARY KEY     NOT NULL,
       username           TEXT(30)    ,
       PASSWORD           TEXT(30)    NOT NULL,
       deptid    TEXT(10) ,
       FOREIGN KEY(deptid) REFERENCES  DEPARTMENT(deptid)); ''')
print ("Table department created successfully")