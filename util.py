#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask, request, session, render_template, url_for, redirect
from flask import make_response, flash, jsonify, send_from_directory
from time import localtime, strftime, strptime
from datetime import date, timedelta
from functools import wraps
from email_module import mail

from glob_var import *
import sqlite3, os, re, hashlib

######## user utils ########
def verify(id, passwd, admin_str)->bool:
    with sqlite3.connect(DATABASE) as database:
        cursor = database.execute("SELECT PASSWORD FROM %s WHERE ID = ? "%admin_str, (id,))
        correct = cursor.fetchone()
        if correct == None:  # wrong id
            flash("用户名不存在！", category="error")
            return False
        else:  # correct id
            hashed_pass = hashlib.sha256((passwd+SALT+id).encode('utf-8')).hexdigest()
            if hashed_pass == correct[0]:
                return True    # correct id-pass pair
            else:  # wrong passwd
                flash("密码错误！", category="error")
                return False

def userRegist(id:str, name:str,passwd:str, admin_type:str,dept_name:str)->bool:
    '''Register a new administrater.

    admin_type should be either 'admin1' or 'admin2'.
    '''
    if admin_type == 'admin1':
        db = 'ADMIN'
    elif admin_type == 'user':
        db = 'USER'
    else:
        flash("注册信息错误", category='error')
    if id == '' or passwd == '':
        flash("用户名或密码不能为空！", category='error')
        return False
    with sqlite3.connect(DATABASE) as database:
        cursor = database.execute("select password from %s where id = ? "%db, (id,))
        empty = cursor.fetchone()
        if empty != None:
            flash("用户名已经存在!", category='warning')
            return False
          # id is new
        cursor = database.execute("select deptid from DEPARTMENT where deptname = ? ", (dept_name,))
        empty = cursor.fetchone()
        if empty == None:
            flash("不存在的部门!", category='warning')
            return False
        deptid=empty[0]

        treated = hashlib.sha256((passwd+SALT+id).encode('utf-8'))
        sql_sentence = "insert into %s (id, name,password,deptid) values (?, ? , ?,?)"%(db)
        cur = database.execute(sql_sentence,(id,name, treated.hexdigest(),deptid))
        database.commit()
        flash("注册成功！<br>请登录！", category='success')
        return True

def printLog(log):
    ''' Use to write log for user's behaviour '''
    with open(LOG, encoding="utf-8", mode='a') as f:
        f.write(log)
        f.write("operation time: {}\n\n".format(strftime("%Y-%m-%d %H:%M:%S", localtime())))
        print("ADD TO LOG")

def applying_material(form)->bool:
    ''' Use to dump the applying information into the database, using the request.form as argument.

    Return True, if the form is successfully added to database and the email is sent. Else, False is returned.'''
    mat_form = [
        (
            form['dep'], form['name'], form['material'], form['contact'],
            form['startyear'], form['startmonth'], form['startday'],
            form['starthour'], form['endingyear'], form['endingmonth'],
            form['endingday'], form['endinghour']
        )
    ]
    with sqlite3.connect(DATABASE) as database:
        c = database.cursor()
        try:
            c.executemany('INSERT INTO MATERIAL VALUES (NULL,?, ?, ?, ?, ?, ?, ?, ? ,?, ?, ?, ?, 0, NULL)', mat_form)
            database.commit()
            hint = "社联小伙伴{}，你好！\n你已成功提交设备借出申请，请勿重复提交!\n本邮件为自动发出，请勿回复。\n".format(form['name'])
        except:
            flash("申请提交失败，请重试或联系技术人员。", category="error")
            # 如果出现数据无法添加到数据库（可能由于检查合理性时未检查出的错误）
            return False
        else:
            if email_enable:
                result = mail(hint, [form['contact']])
                if not result: # 如果邮件发送出现问题
                    flash("邮件发送失败，请联系技术人员。", category="error")
                    return False
            return True


def applying_classroom(form)->bool:
    '''Very much the same as applying_material, except for it's used to dump data into table CLASSROOM'''
    mat_form = [
        (
            form['dep'], form['name'], form['classroom'], form['contact'],
            form['startyear'], form['startmonth'], form['startday'],
            form['starthour'], form['endingyear'], form['endingmonth'],
            form['endingday'], form['endinghour']
        )
    ]
    with sqlite3.connect(DATABASE) as database:
        c = database.cursor()
        try:
            c.executemany('INSERT INTO CLASSROOM VALUES (NULL,?, ?, ?, ?, ?, ?, ?, ? ,?, ?, ?, ?, 0, NULL)', mat_form)
            database.commit()
            hint = "社联小伙伴{}，你好！\n你已成功提交教室借出申请，请勿重复提交!\n本邮件为自动发出，请勿回复。\n".format(form['name'])
        except:
            flash("申请提交失败，请重试或联系技术人员。", category="error")
            # 如果出现数据无法添加到数据库（可能由于检查合理性时未检查出的错误）
            return False
        else:
            if email_enable:
                result = mail(hint, [form['contact']])
                if not result: # 如果邮件发送出现问题
                    flash("邮件发送失败，请联系技术人员。", category="error")
                    return False
            return True


def get_new_apply(tablename, status_code):
    '''
    Take the name of the table and status_code that is checked as the
    arguments, return the list of complete content of matching records. Items
    in the list are tuples.

    Tablename should be a string and status_code is expected to be integers 0, 1, 2.
    '''
    with sqlite3.connect(DATABASE) as database:
        c = database.cursor()
        cursor = c.execute('select * from %s where status = %d;'% (tablename, status_code)) # 这里不是binding，好像不能用？占位
        new_apply_list = cursor.fetchall()
        # fetchall() returns a list of  tuples
        return new_apply_list


def record_scrutiny_results(tablename, indx, status_code, admin):
    ''' Take the name of the table, index of application and the renewed status_code, name of admin as arguments, the function updates the status of application on demand.

    Note that under normal condition, status_code should be 1 (representing approval of application) or 2 (representing denial)'''
    with sqlite3.connect(DATABASE) as database:
        c = database.cursor()
        c.execute("update %s set STATUS = ? where ID = ? "%tablename , (status_code, indx)  )
        c.execute("update %s set ADMIN = ? where ID = ? "%tablename , (admin, indx)  )
        # 提取审批后的记录储存于info中用于发送邮件
        cursor = c.execute('select * from %s where ID = %d;'% (tablename, indx))
        info = cursor.fetchall()[0]
        database.commit()
        if status_code == 1:
            feedback = "社联小伙伴{}，你好！\n你提交的借用{}的申请已批准。\n借出时间：{}年{}月{}日 {}时,请在{}年{}月{}日 {}时之前归还。 \n本邮件为自动发出，请勿回复。\n".format(info[2], info[3],info[5],info[6],info[7],info[8],info[9],info[10],info[11],info[12])
        elif status_code == 2:
            feedback = "社联小伙伴{}，你好！\n很遗憾，你借用{}的申请未能通过！\n本邮件为自动发出，请勿回复。\n".format(info[2], info[3])
        if email_enable:
            result = mail(feedback, [info[4]])
            if not result: # 如果邮件发送出现问题
                flash("邮件发送失败，请联系技术人员。", category="error")


def expire_date():
    a_month = timedelta(days=31)
    expire_date = date.today() - a_month
    return expire_date

def get_records(tablename, year, month):
    ''' Take the name of the table and year, month that is checked as the arguments, return the list of complete content of matching (i.e. the ending time is later than the given one) records. Items in the list are tuples.

    Tablename should be a string and year, month is expected to be integers.
    '''
    with sqlite3.connect(DATABASE) as database:
        c = database.cursor()
        cursor = c.execute('select * from %s where endingyear >= %d and endingmonth >= %d;'% (tablename, year, month))
        records = cursor.fetchall()
        return records

def login_verify(to_be_decorated):
    '''  check-in decorator  '''
    @wraps(to_be_decorated)
    def decorated(*args, **kwargs):
        if 'id' not in session and 'id2' not in session:
            flash("请登录！", category="error")     # NOTE: flash-msg show in the NEXT page
            return redirect(url_for('login'))
        return to_be_decorated(*args, **kwargs)
    return decorated

        ##### 检查合法性 #####

#检查字符串中危险的特殊字符

def check_slashes(plain)->bool:   # `str` is python reserved keyword, DON'T use it
    slashes=['{','}','\'','\"','%','?','\\',',']
    for i in plain:
            if i in slashes:
                flash("输入中包含非法字符", category="error")
                return False
    return True


#检查邮箱格式
def email_available(email)->bool: #email: str 格式
    pattern = re.compile(r"^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")
    match = pattern.match(email)
    if match:
        return True
    else:
        flash("邮箱格式不正确！", category="error")
        return False


#检查姓名格式
def name_available(name)->bool:   # name: str 格式
    pattern = re.compile(r"[\u4e00-\u9fa5]{2,8}")   # 匹配2到8个汉字
    match = pattern.match(name)
    if match:
        return True
    else:
        flash("不是合法的姓名！", category="error")
        return False


def struct_timing(year, month, day, hour):
    '''
    Take **strings** or **integers** as arguments, return a struct_time instance if it
    represents time with given format, else return `None`
    '''
    a = [year, month, day, hour]
    for i in range(0, 4):
        if isinstance(a[i],int):
            a[i] = repr(a[i])
    try:
        struct_time1 = strptime(a[0] + ' ' + a[1] + ' ' + a[2] + ' ' + a[3],
                                '%Y %m %d %H')
        return struct_time1
    except ValueError:
        flash("请输入正确的时间信息！", category="error")
        return None
    except:
        flash("访问错误！", category="error")


def form_legitimate(dic, column)->bool:
    """Check the legitimacy of the request form.

    Column is either 'material' or 'classroom' """
    items_1 = ('name', 'contact', 'dep', column)
    time_1 = ('startyear', 'startmonth', 'startday', 'starthour')
    time_2 = ('endingyear', 'endingmonth', 'endingday',  'endinghour')
    try:
        for item in items_1:
            if not check_slashes(dic[item]):
                return False
        if not name_available(dic['name']) and email_available(dic['contact']):
            return False
            # keep me wondering why it's "and" instead of "or"
        start = [dic[x] for x in time_1]
        end = [dic[x] for x in time_2]
        t1 = struct_timing(*start)
        t2 = struct_timing(*end)
        if t1 == None or t2 == None:
            return False
        elif t2 <= t1 or t1 <= localtime():
            flash("请输入正确的时间信息！", category="error")
            return False
        return True
    except :
        flash('INVALID REQUEST', category='error')
        return False
