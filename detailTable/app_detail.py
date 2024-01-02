#coding=utf-8
import json

# import requests
from flask import Flask, Response, render_template, request

from sqlalchemy import and_, text
#引用数据库启动文件
from detailTable.exts_detail import db
#引用数据库配置文件
import detailTable.config_detail as config_detail
#引用数据库
from detailTable.model_detail import Information, Basic1, Basic2, Dictionary1
import pandas as pd
import copy

app = Flask(__name__)
app.config.from_object(config_detail)
db.init_app(app)
# 修改输出信息的编码
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"


@app.route("/index")
def index():
    return render_template('index.html')


# 返回健康状态
@app.route("/health")
def health():
    result = {'status': 'UP'}
    return Response(json.dumps(result), mimetype='application/json')


def getFundModel(SQLAlchemyModel):
    retList = []
    for ret in SQLAlchemyModel:
        retList.append(ret.__dict__)
        pass
    return retList


def id2name(pid):
    infor1 = Dictionary1.query.filter(Dictionary1.purposeid.like(pid))
    pname = getFundModel(infor1)
    if (len(pname) == 0):
        return 0
    return pname[0]['purposename']


@app.route('/queryDetail', methods=['GET', 'POST'])
def queryDetail():
    merge_list = []
    if request.method == 'POST':
        campus = request.form.get('campus')
        buildname = request.form.get('buildname')
        roomid = request.form.get('roomid')
        roomname = request.form.get('roomname')
        areaBuild = request.form.get('areaBuild')
        areaUse = request.form.get('areaUse')
        purpose = request.form.get('purpose') # 这里的purpose是id
        classify = request.form.get('classify')
        userid = request.form.get('userid')
        username = request.form.get('username')
        roomstate = request.form.get('roomstate')
        notes = request.form.get('notes')
        department = request.form.get('department')
        infor = Information.query.filter(
                    and_(Information.buildname.like("%" + buildname + "%") if buildname is not None else text(""),
                         Information.roomid.like("%" + roomid + "%") if roomid is not None else text(""),
                         Information.roomname.like("%" + roomname + "%") if roomname is not None else text(""),
                         Information.areaBuild.like("%" + areaBuild + "%") if areaBuild is not None else text(""),
                         Information.areaUse.like("%" + areaUse + "%") if areaUse is not None else text(""),
                         Information.purpose.like("%" + purpose + "%") if purpose is not None else text(""),
                         Information.classify.like("%" + classify + "%") if classify is not None else text(""),
                         Information.username.like("%" + username + "%") if username is not None else text(""),
                         Information.roomstate.like("%" + roomstate + "%") if roomstate is not None else text(""),
                         Information.notes.like("%" + notes + "%") if notes is not None else text(""),
                         Information.department.like("%" + department + "%") if department is not None else text(""),
                         Information.campus.like("%" + campus + "%") if campus is not None else text(""),
                         Information.userid.like("%" + userid + "%") if userid is not None else text(""))).all()  # 默认and，and_不写也行
        # list里的元素为字典类型
        merge_list = getFundModel(infor)

        for result in merge_list:
            result['purpose'] = id2name(result['purpose'])
    return render_template('queryDetail.html', merge_list=merge_list)  # 结合html返回list



@app.route('/insertDetail')
def insertDetail():
    return render_template("insertDetail.html")


@app.route('/insert', methods=['GET', 'POST'])
def insert():
    ifSuccess = True
    if request.method == "POST":
        results = dict(request.form)
        # 没对所有字段验证是否为空
        if results['buildname'] is None or results['roomid'] is None:
            ifSuccess = False # 插入数据，主键不能为空
        else:
            infor = Information.query.filter(
                and_(Information.buildname.like(results['buildname']),
                     Information.roomid.like(results['roomid']))).first()
            if infor is not None:
                ifSuccess = False # 避免主键重复
            else:
                information = Information(
                    campus=results['campus'],
                    buildname=results['buildname'],
                    roomid=results['roomid'],
                    roomname=results['roomname'],
                    areaBuild=0 if results['areaBuild'] == '' else float(results['areaBuild']),
                    areaUse=0 if results['areaUse'] == '' else float(results['areaUse']),
                    purpose=results['purpose'], # 传过来的直接是id
                    classify=results['classify'],
                    userid=results['userid'],
                    username=results['username'],
                    roomstate=results['roomstate'],
                    notes=results['notes'],
                    department=results['department'])
                db.session.add(information)
                db.session.commit()
    if ifSuccess == True:
        results['purpose'] = id2name(results['purpose'])
        return render_template("insert_successful.html", results=results)
    else:
        return render_template("insert_fail.html")


@app.route("/deleteConfirmation")
def deleteConfirmation():
    buildname = request.args.get("buildname")
    roomid = request.args.get("roomid")
    return render_template("deleteConfirmation.html", buildname=buildname, roomid=roomid)


@app.route("/deleteDetail")
def deleteDetail():
    buildname = request.args.get("buildname")
    roomid = request.args.get("roomid")
    try:
        db.session.query(Information).filter(Information.buildname == buildname, Information.roomid == roomid).delete()
        db.session.commit()
    except:
        db.rollback()
    return render_template("deleteDetail.html", buildname=buildname, roomid=roomid)


update_dict = {} # 用来存放一条 detail表 更改之前的旧数据


@app.route('/updateDetail')
def updateDetail():
    buildname = request.args.get("buildname")
    roomid = request.args.get("roomid")
    infor = db.session.query(Information).filter(Information.buildname == buildname, Information.roomid == roomid).first()
    global update_dict
    update_dict = infor.__dict__
    del update_dict['_sa_instance_state']
    # output_update = update_dict
    output_update = copy.deepcopy(update_dict)
    output_update['purpose'] = id2name(output_update['purpose'])

    return render_template("updateDetail.html", update_dict=output_update)


@app.route('/update', methods=['GET', 'POST'])
def update():
    # update_dict是通过全局变量从另一个路由传入的旧数据
    # results是从html传入的新数据
    if request.method == "POST":
        global update_dict
        results = dict(request.form)
        for key in results:
            results[key] = update_dict[key] if results[key] == '' else results[key]
        try:
            db.session.query(Information).filter(Information.buildname == update_dict['buildname'], Information.roomid == update_dict['roomid']).update(results)
            db.session.commit()
        except:
            db.rollback()
            return render_template("update_fail.html")
        results['purpose'] = id2name(results['purpose'])
    return render_template("update.html", update_dict=results)


export_list = [[]]
count1_head = ['楼宇名称', '行政办公', '教师用房', '研究生用房', '人员行政用房（行政+教师+研究生）', '本科实验室', '学科实验室', '专用教室', '公共设施', '合计']
count2_head = ['部门名称', '行政办公', '教师用房', '研究生用房', '人员行政用房（行政+教师+研究生）', '本科实验室', '学科实验室', '专用教室', '公共设施', '合计']
count4_head = ['楼宇名称', '教学及辅助用房', '教室', '实验实习用房', '专职科研机构办公及研究用房', '图书馆'\
            , '室内体育用房', '师生活动用房', '会堂', '继续教育用房', '行政办公用房', '校行政办公用房'\
            , '院系及教师教研办公用房', '生活用房', '学生宿舍（公寓）', '食堂', '单身教师宿舍（公寓）'\
            , '后勤及辅助用房', '教工住宅', '其他用房']
count3_head = ['楼宇名称', '行政办公_建筑面积', '行政办公_使用面积', '教师用房_建筑面积', '教师用房_使用面积', '研究生用房_建筑面积'\
            , '研究生用房_使用面积', '人员行政用房（行政+教师+研究生）_建筑面积', '人员行政用房（行政+教师+研究生）_使用面积'\
            , '本科实验室_建筑面积', '本科实验室_使用面积', '学科实验室_建筑面积', '学科实验室_使用面积', '专用教室_建筑面积'\
            , '专用教室_使用面积', '公共设施_建筑面积', '公共设施_使用面积', '合计_建筑面积', '合计_使用面积']


@app.route('/count1/<depart>')
def count1(depart):
    infor = Basic1.query
    merge_list = getFundModel(infor)
    result_list = [] # 二维列表
    map_buildname = {} # 映射楼宇名称和result_list行之间的关系
    map_classify = {} # 映射房间分类和result_list列之间的关系

    map_classify['行政办公'] = 1
    map_classify['教师用房'] = 2
    map_classify['研究生用房'] = 3
    map_classify['本科实验室'] = 4
    map_classify['学科实验室'] = 6
    map_classify['科研实验室'] = 6 # 字典中没有这个类别，应该把它归到“学科”，加上以防万一
    map_classify['专用教室'] = 7
    map_classify['公共设施'] = 8
    kk = 0
    for result in merge_list:
        result_list.append([])
        for j in range(1, 11): # 数字从下标1开始，下标0是楼宇名称
            result_list[kk].append(0)
        map_buildname[result['buildname']] = kk
        kk += 1
    # 给最后一行“总计”留出空间
    result_list.append([])
    for j in range(1, 11):  # 数字从下标1开始，下标0是楼宇名称
        result_list[kk].append(0)

    # print(result_list[map_buildname['船电楼']][2]) # 访问每个元素的方式
    for result in merge_list:
        # 先按 每个建筑名称 搜所 目标学院 的所有行
        buildname = result['buildname']
        infor = Information.query.filter(
            and_(Information.buildname.like("%" + buildname + "%"),
                 Information.department.like("%" + depart + "%") # 在这里更改学院 ############################
                 )).all()
        # 这是轮机学院中某个建筑的所有行
        merge_list_tem = getFundModel(infor)
        # 把每行所对应的“公有房分类”填到二维列表中
        for tem in merge_list_tem:
            str = tem['classify']
            classifylist = str.split('/')  # 用/分割classify字符串，并保存到列表
            for classify in classifylist:  # 循环输出列表值
                result_list[map_buildname[buildname]][map_classify[classify]] += tem['areaUse']
    # 处理两个“合计”属性
    buildnum = len(merge_list)  # 全学校的所有房屋数量
    for i in range(buildnum):
        result_list[i][0] = merge_list[i]['buildname']
        result_list[i][4] = result_list[i][1] + result_list[i][2] + result_list[i][3] # 第一个合计
        result_list[i][9] = result_list[i][4] + result_list[i][5] + result_list[i][6] + result_list[i][7] + result_list[i][8] # 第二个合计
    # 转化为保留两位小数，防止精度导致的无限小数
    for i in range(buildnum):
        for j in range(1, 10):
            result_list[i][j] = round(result_list[i][j], 2)
    # 最后一行总计
    result_list[kk][0] = '总计'
    for j in range(1, 10):  # 数字从下标1开始，下标0是楼宇名称
        for i in range(buildnum):
            result_list[kk][j] += result_list[i][j]
            result_list[kk][j] = round(result_list[kk][j], 2)
    global export_list
    export_list = result_list
    return render_template('count1.html', result_list=result_list, buildnum=buildnum)


@app.route('/count3')
def count3():
    infor = Basic1.query
    merge_list = getFundModel(infor)
    result_list = [] # 二维列表
    map_buildname = {} # 映射楼宇名称和result_list行之间的关系
    map_classify = {} # 映射房间分类和result_list列之间的关系

    map_classify['行政办公'] = 1 # ！！！应该是行政办公
    map_classify['教师用房'] = 2
    map_classify['研究生用房'] = 3
    map_classify['本科实验室'] = 4
    map_classify['学科实验室'] = 6
    map_classify['科研实验室'] = 6 # 字典中没有这个类别，应该把它归到“学科”，加上以防万一
    map_classify['专用教室'] = 7
    map_classify['公共设施'] = 8 # ！！！应该是公共设施
    kk = 0
    for result in merge_list:
        result_list.append([])
        for j in range(1, 24): # 数字从下标1开始，下标0是楼宇名称
            result_list[kk].append(0)
        map_buildname[result['buildname']] = kk
        kk += 1
    # 给最后一行“总计”留出空间
    result_list.append([])
    for j in range(1, 24):  # 数字从下标1开始，下标0是楼宇名称
        result_list[kk].append(0)

    # print(result_list[map_buildname['船电楼']][2]) # 访问每个元素的方式
    for result in merge_list:
        # 先按 每个建筑名称 搜索所有行
        buildname = result['buildname']
        infor = Information.query.filter(
            and_(Information.buildname.like("%" + buildname + "%")
                 )).all()
        # 这是某个建筑的所有行
        merge_list_tem = getFundModel(infor)
        # 把每行所对应的“公有房分类”填到二维列表中
        for tem in merge_list_tem:
            str = tem['classify']
            classifylist = str.split('/')  # 用/分割classify字符串，并保存到列表
            for classify in classifylist:  # 循环输出列表值
                result_list[map_buildname[buildname]][map_classify[classify]] += tem['areaUse'] # 二维下标不加10是对应的使用面积
                result_list[map_buildname[buildname]][map_classify[classify]+10] += tem['areaBuild'] # 二维下标+10是对应的建筑面积
    # 处理两个“合计”属性
    buildnum = len(merge_list)  # 全学校的所有房屋数量
    for i in range(buildnum):
        result_list[i][0] = merge_list[i]['buildname']
        result_list[i][4] = result_list[i][1] + result_list[i][2] + result_list[i][3] # 第一个使用面积合计
        result_list[i][14] = result_list[i][11] + result_list[i][12] + result_list[i][13]  # 第一个建筑面积合计
        result_list[i][9] = result_list[i][4] + result_list[i][5] + result_list[i][6] + result_list[i][7] + result_list[i][8] # 第二个使用合计
        result_list[i][19] = result_list[i][14] + result_list[i][15] + result_list[i][16] + result_list[i][17] + result_list[i][18]  # 第二个建筑合计
    # 转化为保留两位小数，防止精度导致的无限小数
    for i in range(buildnum):
        for j in range(1, 22):
            result_list[i][j] = round(result_list[i][j], 2)
    # 最后一行总计
    result_list[kk][0] = '总计'
    for j in range(1, 22):  # 数字从下标1开始，下标0是楼宇名称
        for i in range(buildnum):
            result_list[kk][j] += result_list[i][j]
            result_list[kk][j] = round(result_list[kk][j], 2)
    global export_list
    export_list = result_list
    return render_template('count3.html', result_list=result_list, buildnum=buildnum)


@app.route('/count2')
def count2():
    infor = Basic2.query
    merge_list = getFundModel(infor)
    result_list = [] # 二维列表
    map_departmentname = {} # 映射部门名称和result_list行之间的关系
    map_classify = {} # 映射房间分类和result_list列之间的关系

    map_classify['行政办公'] = 1 # ！！！应该是行政办公
    map_classify['教师用房'] = 2
    map_classify['研究生用房'] = 3
    map_classify['本科实验室'] = 4
    map_classify['学科实验室'] = 6
    map_classify['科研实验室'] = 6 # 字典中没有这个类别，应该把它归到“学科”，加上以防万一
    map_classify['专用教室'] = 7
    map_classify['公共设施'] = 8 # ！！！应该是公共设施
    kk = 0
    for result in merge_list:
        result_list.append([])
        for j in range(1, 11): # 数字从下标1开始，下标0是部门名称
            result_list[kk].append(0)
        map_departmentname[result['departmentname']] = kk
        kk += 1
    # 给最后一行“总计”留出空间
    result_list.append([])
    for j in range(1, 11):  # 数字从下标1开始，下标0是学院名称（合计）
        result_list[kk].append(0)

    # print(result_list[map_buildname['航海学院']][2]) # 访问每个元素的方式
    for result in merge_list:
        # 先按 每个部门名称 搜索所有行
        departmentname = result['departmentname']
        infor = Information.query.filter(Information.department.like("%" + departmentname + "%")).all()
        # 这是某个部门中某个建筑的所有行
        merge_list_tem = getFundModel(infor)
        # 把每行所对应的“公有房分类”填到二维列表中
        for tem in merge_list_tem:
            strtem = tem['classify']
            classifylist = strtem.split('/')  # 用/分割classify字符串，并保存到列表
            for classify in classifylist:  # 循环输出列表值
                result_list[map_departmentname[departmentname]][map_classify[classify]] += tem['areaUse']
    # 处理两个“合计”属性
    departmentnum = len(merge_list)  # 全学校的所有部门数量
    for i in range(departmentnum):
        result_list[i][0] = merge_list[i]['departmentname']
        result_list[i][4] = result_list[i][1] + result_list[i][2] + result_list[i][3] # 第一个合计
        result_list[i][9] = result_list[i][4] + result_list[i][5] + result_list[i][6] + result_list[i][7] + result_list[i][8] # 第二个合计
    # 转化为保留两位小数，防止精度导致的无限小数
    for i in range(departmentnum):
        for j in range(1, 10):
            result_list[i][j] = round(result_list[i][j], 2)
    # 最后一行总计
    result_list[kk][0] = '总计'
    for j in range(1, 10):  # 数字从下标1开始，下标0是楼宇名称
        for i in range(departmentnum):
            result_list[kk][j] += result_list[i][j]
            result_list[kk][j] = round(result_list[kk][j], 2)
    global export_list
    export_list = result_list
    return render_template('count2.html', result_list=result_list, departmentnum=departmentnum)


@app.route('/count4')
def count4():
    infor = Basic1.query
    merge_list = getFundModel(infor)
    result_list = [] # 二维列表
    map_buildname = {} # 映射楼宇名称和result_list行之间的关系
    # 不需要这个了，因为有了一个现成的数据表 map_purpose = {} # 映射房间用途和result_list列之间的关系
    kk = 0
    for result in merge_list:
        result_list.append([])
        for j in range(1, 21): # 数字从下标1开始，下标0是楼宇名称
            result_list[kk].append(0)
        map_buildname[result['buildname']] = kk
        kk += 1
    # 给最后一行“总计”留出空间
    result_list.append([])
    for j in range(1, 21):  # 数字从下标1开始，下标0是楼宇名称
        result_list[kk].append(0)

    # print(result_list[map_buildname['船电楼']][2]) # 访问每个元素的方式
    for result in merge_list:
        # 先按 每个建筑名称 搜索所有行
        buildname = result['buildname']
        infor = Information.query.filter(
            and_(Information.buildname.like("%" + buildname + "%")
                 )).all()
        # 这是某个建筑的所有行
        merge_list_tem = getFundModel(infor)
        # 把每行所对应的“公有房分类”填到二维列表中
        for tem in merge_list_tem:
            # str = tem['purpose']
            # purposelist = str.split('/')  # 用/分割classify字符串，并保存到列表
            # for purpose in purposelist:  # 循环输出列表值
            #     if(purpose[0:4] == '0101'):
            #         result_list[map_buildname[buildname]][2] += tem['areaUse']
            purpose = tem['purpose']
            if (purpose[0:4] == '0101'):
                result_list[map_buildname[buildname]][2] += tem['areaUse']
            elif(purpose[0:4] == '0102'):
                result_list[map_buildname[buildname]][3] += tem['areaUse']
            elif (purpose[0:4] == '0103'):
                result_list[map_buildname[buildname]][4] += tem['areaUse']
            elif (purpose[0:4] == '0104'):
                result_list[map_buildname[buildname]][5] += tem['areaUse']
            elif (purpose[0:4] == '0105'):
                result_list[map_buildname[buildname]][6] += tem['areaUse']
            elif (purpose[0:4] == '0106'):
                result_list[map_buildname[buildname]][7] += tem['areaUse']
            elif (purpose[0:4] == '0107'):
                result_list[map_buildname[buildname]][8] += tem['areaUse']
            elif (purpose[0:4] == '0108'):
                result_list[map_buildname[buildname]][9] += tem['areaUse']
            elif (purpose[0:4] == '0201'):
                result_list[map_buildname[buildname]][11] += tem['areaUse']
            elif (purpose[0:4] == '0202'):
                result_list[map_buildname[buildname]][12] += tem['areaUse']
            elif (purpose[0:4] == '0301'):
                result_list[map_buildname[buildname]][14] += tem['areaUse']
            elif (purpose[0:4] == '0302'):
                result_list[map_buildname[buildname]][15] += tem['areaUse']
            elif (purpose[0:4] == '0303'):
                result_list[map_buildname[buildname]][16] += tem['areaUse']
            elif (purpose[0:4] == '0304'):
                result_list[map_buildname[buildname]][17] += tem['areaUse']
            elif (purpose[0:2] == '04'):
                result_list[map_buildname[buildname]][18] += tem['areaUse']
            elif (purpose[0:2] == '05'):
                result_list[map_buildname[buildname]][19] += tem['areaUse']
    # 处理多个个“合计”属性
    buildnum = len(merge_list)  # 全学校的所有房屋数量
    for i in range(buildnum):
        result_list[i][0] = merge_list[i]['buildname']
        result_list[i][1] = result_list[i][2] + result_list[i][3] + result_list[i][4] + result_list[i][5] + result_list[i][6] + result_list[i][7] + result_list[i][8] + result_list[i][9]
        result_list[i][10] = result_list[i][11] + result_list[i][12]
        result_list[i][13] = result_list[i][14] + result_list[i][15] + result_list[i][16] + result_list[i][17]
        # 18、19已经是合计了
    # 转化为保留两位小数，防止精度导致的无限小数
    for i in range(buildnum):
        for j in range(1, 20):
            result_list[i][j] = round(result_list[i][j], 2)
    # 最后一行总计
    result_list[kk][0] = '总计'
    for j in range(1, 20):  # 数字从下标1开始，下标0是楼宇名称
        for i in range(buildnum):
            result_list[kk][j] += result_list[i][j]
            result_list[kk][j] = round(result_list[kk][j], 2)
    global export_list
    export_list = result_list
    return render_template('count4.html', result_list=result_list, buildnum=buildnum)


@app.route('/export/<id>', methods=['GET', 'POST'])
def export(id):
    if request.method == 'POST':
        fileName = request.form.get('fileName')
        fileName += '.xlsx'
        global export_list

        if(id == '1'):
            export_list.insert(0, count1_head)
        if (id == '2'):
            export_list.insert(0, count2_head)
        if (id == '4'):
            export_list.insert(0, count4_head)
        if (id == '3'):
            export_list = list(map(list, zip(*export_list)))
            tem_list = []
            tem_list.append(export_list[0])
            for i in range(1, 9+1, 1):
                tem_list.append(export_list[i+10])
                tem_list.append(export_list[i])
            export_list = list(map(list, zip(*tem_list)))
            export_list.insert(0, count3_head)

        df = pd.DataFrame(export_list)
        df.to_excel(fileName, index=False, header=False)
    return render_template('export.html')


@app.route('/exitBI')
def exitBI():
    infor = Basic1.query
    # list里的元素为字典类型
    merge_list = getFundModel(infor)
    return render_template('exitBI.html', merge_list=merge_list)  # 结合html返回list


@app.route('/updateBI')
def updateBI():
    buildid = request.args.get("buildid")
    funccategory = request.args.get("funccategory")
    arealeased = request.args.get("arealeased")
    return render_template("updateBI.html", buildid=buildid, funccategory=funccategory, arealeased=arealeased)


@app.route('/upBI', methods=['GET', 'POST'])
def upBI():
    if request.method == 'POST':
        buildid = request.args.get("buildid")
        funccategory = request.form.get("funccategory")
        arealeased = request.form.get("arealeased")
        try:
            db.session.query(Basic1).filter(Basic1.buildid == buildid).update({Basic1.funccategory: funccategory, Basic1.arealeased: arealeased})
            db.session.commit()
        except:
            db.rollback()
        infor = Basic1.query
        merge_list = getFundModel(infor)
    return render_template("exitBI.html", merge_list=merge_list)


@app.route('/insertBI')
def insertBI():
    return render_template("insertBI.html")


@app.route('/inBI', methods=['GET', 'POST'])
def inBI():
    ifSuccess = True
    if request.method == "POST":
        results = dict(request.form)
        # 没对所有字段验证是否为空
        if results['buildid'] is None:
            ifSuccess = False  # 插入数据，主键不能为空
        else:
            infor = Basic1.query.filter(Basic1.buildid.like(results['buildid'])).first()
            if infor is not None:
                ifSuccess = False  # 避免主键重复
            else:
                basic1 = Basic1(
                    campus=results['campus'],
                    buildid=results['buildid'],
                    buildname=results['buildname'],
                    buildvalue=0 if results['buildvalue'] == '' else int(results['buildvalue']),
                    usecoefficient=0 if results['usecoefficient'] == '' else float(results['usecoefficient']),
                    acquisitionmethod=results['acquisitionmethod'],
                    propertyid=results['propertyid'],
                    ownershipnature=results['ownershipnature'],
                    buildstructure=results['buildstructure'],
                    ownershipcertificate=results['ownershipcertificate'],
                    propertyform=results['propertyform'],
                    purpose=results['purpose'],
                    height=0 if results['height'] == '' else float(results['height']),
                    floorunder=0 if results['floorunder'] == '' else float(results['floorunder']),
                    floorabove=0 if results['floorabove'] == '' else float(results['floorabove']),
                    areabuildunder=0 if results['areabuildunder'] == '' else float(results['areabuildunder']),
                    areabuildabove=0 if results['areabuildabove'] == '' else float(results['areabuildabove']),
                    areause=0 if results['areause'] == '' else float(results['areause']),
                    areabuild=0 if results['areabuild'] == '' else float(results['areabuild']),
                    areacover=0 if results['areacover'] == '' else float(results['areacover']),
                    yearbuilt=0 if results['yearbuilt'] == '' else int(results['yearbuilt']),
                    acquisitiondata=results['acquisitiondata'],
                    locate=results['locate'],
                    funccategory=results['funccategory'],
                    arealeased=0 if results['arealeased'] == '' else float(results['arealeased']))
                db.session.add(basic1)
                db.session.commit()
    if ifSuccess == True:
        infor = Basic1.query
        merge_list = getFundModel(infor)
        return render_template("exitBI.html", merge_list=merge_list)
    else:
        return render_template("insert_fail.html")


# if  __name__ == '__main__':
#     # 更改端口
#     app.run(host="0.0.0.0", port=8080)
