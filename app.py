#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''   Material System build   '''

######## importing ########
from util import*


######## initializaton ########

app = Flask(__name__)
app.secret_key = 's\x1f}\xc8\xe29c\x84\xd1\x87P\x8e\xa5h5s\xf1\xfff\xcf\xfcK\xe8i'

######## views  ########
# ''' entry & exit '''
@app.route('/')
def index():
    return redirect(url_for('personal'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        #检查危险字符
        if check_slashes(request.form['id']) \
                and check_slashes(request.form['passwd']):
            session['passwd'] = request.form['passwd']
            if request.form['admin_type'] == 'admin1':
                session['id'] = request.form['id']
                if verify(session['id'], session['passwd'], "ADMIN"):
                    try:
                        # don't carry your passwd with you
                        assert session.pop('passwd', None) != None
                    except:
                        session.pop('id', None)
                        return redirect(url_for('login'))
                    flash("着陆成功！", category='success')
                    return redirect(url_for('personal'))
                else:
                    session.pop('id', None)
                    session.pop('passwd', None)
                    return redirect(url_for('login'))
            elif request.form['admin_type'] == 'user':
                session['id2'] = request.form['id']
                if verify(session['id2'], session['passwd'], "USER"):
                    try:
                        # don't carry your passwd with you
                        assert session.pop('passwd', None) != None
                    except:
                        session.pop('id2', None)
                        return redirect(url_for('login'))
                    flash("着陆成功！", category='success')
                    return redirect(url_for('personal'))
                else:
                    session.pop('id2', None)
                    session.pop('passwd', None)
                    return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))

@app.route('/register/', methods=['POST'])
def register():
    id = request.form['id']
    name=request.form['user_name']
    # LOG(114514)
    dept_name=request.form['dept_id']
    # print(dept_name)
    passwd = request.form['passwd_first']
    if passwd != request.form['passwd_second']:
        flash("两次密码不相同！<br>换个好记一点的吧？", category='error')
        return redirect(url_for('login'))
    # elif len(passwd) < 8:
    #     flash("密码太短了！", category='warning')
    #     return redirect(url_for('login'))
    elif request.form['invitation'] != INVITATION:
        flash("邀请码错误！", category='error')
        return redirect(url_for('login'))
    else:
        if userRegist(id, name,passwd, request.form['admin_type'],dept_name):
            return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))

@app.route('/home/')
def personal():
    if 'id' in session:
        getname(True,session["id"])
    elif "id2" in  session:
        getname(False,session["id2"])
    return render_template("home.html")

@app.route('/logout/')
def logout():
    # 已登陆的管理员才能看到logout按钮，否则报错
    assert 'id' in session or 'id2' in session
    if 'id' in session:
        # clear session
        session.pop('id', None) # about the usage of session.pop see: https://stackoverflow.com/questions/20115662/what-does-the-second-argument-of-the-session-pop-method-do-in-python-flask
    elif 'id2' in session:
        session.pop('id2', None)
    print(session.pop('passwd', None))  # should get `None`
    flash("已登出", category='message')
    return redirect(url_for('index'))

    ''' entry to modules '''

@app.route('/devices/', methods=['GET', 'POST'])
def devices_apply():
    if request.method == 'GET':
        return render_template('devices_apply.html')
    elif request.method == 'POST':
        #格式控制
        if form_legitimate(request.form, 'material'):
            if applying_device(request.form):
                # NOTE: should not exceed 79 chars (per line)
                printLog("user {} apply for material: {}\n".format(
                    request.form['name'], request.form['material']))
                flash("表格提交成功, 请检查相应邮箱（含垃圾箱）。", category='success')
            return redirect(url_for('personal'))
        else:
            return render_template('devices_apply.html')

@app.route('/device/', methods=['GET', 'POST'])
def device_apply():
    if request.method == 'GET':
        return render_template('devices_apply.html')
    elif request.method == 'POST':
        #格式控制
        if form_legitimate(request.form, 'material'):
            if applying_device(request.form):
                # NOTE: should not exceed 79 chars (per line)
                printLog("user {} apply for material: {}\n".format(
                    request.form['name'], request.form['material']))
                flash("表格提交成功, 请检查相应邮箱（含垃圾箱）。", category='success')
            return redirect(url_for('personal'))
        else:
            return render_template('devices_apply.html')

@app.route('/classroom/', methods=['GET', 'POST'])
def classroom_apply():
    if request.method == 'GET':
        return render_template('classroom_apply.html')
    elif request.method == 'POST':
        if form_legitimate(request.form, 'classroom'):
            if applying_classroom(request.form):
                printLog("user {} apply for classroom: {}\n".format(
                    request.form['name'], request.form['classroom']))
                flash("表格提交成功, 请检查相应邮箱（含垃圾箱）。", category='success')
            return redirect(url_for('personal'))
        else:
            return render_template('classroom_apply.html')


@app.route('/classroom-usage/')
def classroom_usage():
    if request.method == 'GET':
        def get_endtime(record):
            return struct_timing(record[9], record[10], record[11], record[12])
        # results = get_records('classroom', date.today().year, date.today().month)
        # search for unfinished records that are approved
        # msgs = [i for i in results if i[13] == 1 and get_endtime(i) >= localtime()]
        # msgs = sorted(msgs, key=get_endtime) # sort messages accoriding to their endtime
        # num = len(msgs)
        msgs=[1,1,1]
        return render_template('classroom_usage.html', msgs=msgs,
                               num=3)
@app.route('/device_man/')
def device_man():
    if request.method == 'GET':
        def get_endtime(record):
            return struct_timing(record[9], record[10], record[11], record[12])
        # results = get_records('classroom', date.today().year, date.today().month)
        # search for unfinished records that are approved
        # msgs = [i for i in results if i[13] == 1 and get_endtime(i) >= localtime()]
        # msgs = sorted(msgs, key=get_endtime) # sort messages accoriding to their endtime
        # num = len(msgs)
        l=getALLDevice(getdept(True,session["id"]))
        return render_template('device_man.html', msgs=l,
                               num=len(l))
@app.route('/personal_search/', methods=['GET', 'POST'])
def personal_search():
    if request.method == 'GET':
        return render_template('personal_search.html', hint = True)
    elif request.method == 'POST':
        with mysql.connector.connect(host=IP,user='root', password=PW, database='device') as database:
            c = database.cursor()
            cursor = c.execute('select * from material where dep = ? and name = ?' ,(request.form['dep'], request.form['name']))
            mat_result = cursor.fetchall()
            cursor = c.execute('select * from classroom where dep = ? and name = ?' ,(request.form['dep'], request.form['name']))
            class_result = cursor.fetchall()
        num_mat = len(mat_result)
        num_class = len(class_result)
        return render_template('personal_search.html', hint = False, mat_result = mat_result, class_result=class_result, num_mat = num_mat, num_class = num_class)

#### views for administers ####

@app.route('/scrutiny-application/', methods=['GET', 'POST'])
@login_verify # to make sure non-administer can not access this page
def scrutiny()-> str:
    if request.method == 'GET':
        if 'id' in session:
            msgs = get_new_apply('MATERIAL', 0)
        elif 'id2' in session:
            msgs = get_new_apply('CLASSROOM', 0)
        id_list = [ i[0] for i in msgs ]
        num = len(id_list)
        return render_template('scrutiny.html', msgs=msgs,
                               num=num, id_list=id_list)
        # 此处id_list与 num都是为了解决提取出来的信息的定位问题。
        # id_list用于反馈时确定更新的申请id，而 msgs中的储存有数据内容
        # 的元组在该list中的位置则应由序数确定， 因而在scrutiny.html中
        # 将请求id号与序数做到了一一对应
        # 有更好方案可以改进


@app.route('/approve_mat/<int:id>', methods=['POST'])
@login_verify
def approve_mat(id):
    record_scrutiny_results('material', id, 1, session['id'])
    printLog("administer {} approved the application for borrowing material.\n application NO: {}\n".format(session['id'],id))
    flash("审批借出设备成功", category='success')
    return redirect(url_for('scrutiny'))

@app.route('/refuse_mat/<int:id>', methods=['POST'])
@login_verify
def refuse_mat(id):
    record_scrutiny_results('material', id, 2, session['id'])
    printLog("administer {} refused the application for borrowing material.\n application NO: {}\n".format(session['id'], id))
    flash("设备借出申请已拒绝", category='info')
    return redirect(url_for('scrutiny'))

@app.route('/approve_class/<int:id>', methods=['POST'])
@login_verify
def approve_class(id):
    record_scrutiny_results('classroom', id, 1, session['id2'])
    printLog("administer {} approved the application for borrowing classroom.\n application NO: {}\n".format(session['id2'],id))
    flash("审批借出教室成功", category='success')
    return redirect(url_for('scrutiny'))

@app.route('/refuse_class/<int:id>', methods=['POST'])
@login_verify
def refuse_class(id):
    record_scrutiny_results('classroom', id, 2, session['id2'])
    printLog("administer {} refused the application for borrowing classroom.\n application NO: {}\n".format(session['id2'], id))
    flash("教室借出申请已拒绝", category='info')
    return redirect(url_for('scrutiny'))

@app.route('/records/')
@login_verify
def records()->str:
    if 'id' in session:
        tablename = 'material'
    elif 'id2' in session:
        tablename = 'classroom'
    results = get_records(tablename, expire_date().year, expire_date().month)
    num = len(results)
    return render_template('records.html', msgs = results, num = num)

######## Miscellaneous entries ########

@app.route('/opensource/')
def opensource_info()->str:
    return render_template("opensource-info.html")

@app.route('/help/')
def help()->str:
    return render_template("help.html")

######## run ########

if __name__ == '__main__':
    app.run(host = "0.0.0.0", debug = True)
