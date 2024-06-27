#!/usr/bin/python3
# 为了测试时创建数据库及相应表格参数
# import sqlite3
import mysql.connector
# conn = sqlite3.connect('/mnt/e/device.db')
# print ("Opened database successfully")
# c = conn.cursor()
conn = mysql.connector.connect(host=IP,user='root', password=PW, database='device')
c = conn.cursor()

c.execute('''CREATE TABLE DEPARTMENT
       (deptid  CHAR(10)    PRIMARY KEY     NOT NULL,
       deptname CHAR(30)    ); ''')
print ("Table department created successfully")

c.execute('''CREATE TABLE ADMIN
       (ID  CHAR(10)    PRIMARY KEY     NOT NULL,
       username           CHAR(30)    ,
       PASSWORD           CHAR(100)    NOT NULL,
       deptid    CHAR(10) ,
       FOREIGN KEY(deptid) REFERENCES  DEPARTMENT(deptid)); ''')
print ("Table admin created successfully")

c.execute('''CREATE TABLE USER
       (id  CHAR(10)    PRIMARY KEY     NOT NULL,
       username           CHAR(30)    ,
       PASSWORD           CHAR(100)    NOT NULL,
       deptid    CHAR(10) ,
       FOREIGN KEY(deptid) REFERENCES  DEPARTMENT(deptid)); ''')
print ("Table department created successfully")


c.execute('''CREATE TABLE DEVICE_TYPE
       (devid  CHAR(10)    PRIMARY KEY     NOT NULL,
       name           CHAR(30) ); ''')
print ("Table device created successfully")


c.execute('''CREATE TABLE DEVICE
       (devid  CHAR(10)     NOT NULL,
       deptid    CHAR(10) ,
       allnum int,
       curnum int,
       PRIMARY KEY(devid,deptid),
       FOREIGN KEY(devid) REFERENCES  DEVICE_TYPE(devid),
       FOREIGN KEY(deptid) REFERENCES  DEPARTMENT(deptid)); ''')
print ("Table device created successfully")


create_borrow_dev:str='''CREATE TABLE BORROW_DEVICE(
       id  CHAR(10)         NOT NULL,
       devid  CHAR(10)     NOT NULL,
       deptid    CHAR(10) ,
       borrowtime date,
       return date,
       PRIMARY KEY     (id,devid,deptid,borrowtime),
       FOREIGN KEY(deptid) REFERENCES  DEPARTMENT(deptid),
       FOREIGN KEY(devid) REFERENCES  DEVICE_TYPE(devid)  ,         
       FOREIGN KEY(id) REFERENCES  USER(id));'''

c.execute(create_borrow_dev)
print ("Table borrow_device created successfully")