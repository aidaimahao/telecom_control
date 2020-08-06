# from flask_restplus import Resource, Api
from process_control.models import *
from flask import request, jsonify
from . import admin_interface
from sqlalchemy import and_, or_
from process_control.admin.views import adimn_check_login

@admin_interface.route('/msg/<int:page>/', methods=['get', ])
@adimn_check_login
def msg_list(page=None):
    nickname = request.args.get('nickname', '')
    first_time = request.args.get('first_time', '')
    info1 = request.args.get('info1', '')
    phone = request.args.get('phone', '')
    phone_type = request.args.get('phone_type', '')
    # 若有条件，条件查询
    if nickname or first_time or info1 or phone:
        page_data = SignHistory.query.join(
            Userinfo, SignHistory.openid == Userinfo.openid).join(
            AudioRecord, SignHistory.openid == AudioRecord.openid).filter(
            SignHistory.sign_id == AudioRecord.sign_id).add_entity(
            Userinfo).add_entity(AudioRecord)
        if nickname:
            page_data = page_data.filter(Userinfo.nickname.like(nickname))
        if first_time:
            page_data = page_data.filter()
        if info1:
            page_data = page_data.filter(SignHistory.info1 == info1)
        if phone:
            if phone_type == '0':
                page_data = page_data.filter(Userinfo.phone_number == phone)
            elif phone_type == '1':
                page_data = page_data.filter(Userinfo.job_number == phone)
        page_data = page_data.order_by(SignHistory.time.desc()).paginate(page=page, per_page=10)
    else:
        if page == None:
            page = 1
        page_data = SignHistory.query.join(
            Userinfo, SignHistory.openid == Userinfo.openid).join(
            AudioRecord, SignHistory.openid == AudioRecord.openid).filter(
            SignHistory.sign_id == AudioRecord.sign_id).add_entity(
            Userinfo).add_entity(AudioRecord).order_by(
            SignHistory.time.desc()).paginate(page=page, per_page=10)
    page_data = [
        {'nickname': x[1].nickname, 'first_time': str(x[1].first_time), 'phone_number': x[1].phone_number,
         'job_number': x[1].job_number, 'info1': x[0].info1, 'info2': x[0].info2, 'audio_path': x[2].audio_path,
         'face_image': x[1].face_image}
        for x in page_data.items]
    return jsonify(page_data)


@admin_interface.route('/check/<int:page>/', methods=['get', ])
@adimn_check_login
def check_list(page=None):
    nickname = request.args.get('nickname', '')
    state = [int(x) if x.isdigit() else None for x in request.args.getlist('state')]
    # 若有条件，条件查询
    if nickname or state:
        page_data = Userinfo.query
        if nickname:
            page_data = page_data.filter(Userinfo.nickname.like(nickname))
        if state:
            if None in state:
                page_data = Userinfo.query.filter(or_(Userinfo.face_pass.in_(state), Userinfo.face_pass == None))
            else:
                page_data = Userinfo.query.filter(Userinfo.face_pass.in_(state))
        page_data = page_data.order_by(Userinfo.first_time.desc()).paginate(page=page, per_page=10)
    else:
        if page == None:
            page = 1
        page_data = Userinfo.query.order_by(
            Userinfo.first_time.desc()).paginate(page=page, per_page=10)
    for i in page_data.items:
        print(i)
    page_data = [{'nickname': x.nickname, 'face_pass': x.face_pass, 'is_admin': x.is_admin,
                  'phone_number': x.phone_number, 'job_number': x.job_number, 'first_time': x.first_time,
                  'face_image': x.face_image} for x in page_data.items]

    return jsonify(page_data)


@admin_interface.route('/pass_or_fail/', methods=['post', 'get'], strict_slashes=False)
@adimn_check_login
def pass_or_fail():
    if request.method == 'GET':
        openid = request.args.get('openid', '')
        mark = request.args.get('mark', '')
    else:
        openid = request.form['openid']
        mark = request.form['mark']
    res = {'state': '', 'msg': ''}
    if openid:
        user_obj_list = Userinfo.query.filter(Userinfo.openid==openid)
        if user_obj_list:
                user_obj = user_obj_list.first()
                if int(mark) == 1:
                    # 审核通过
                    user_obj.face_pass = int(mark)
                    db.session.add(user_obj)
                    db.session.commit()
                    res['state'] = 'success'
                    res['msg'] = '审核通过'
                else:
                    # 审核不通过
                    reason_list = request.args.getlist('reason')
                    reason_text = ''
                    reason_text = '；'.join(reason_list)
                    user_obj.face_pass = int(mark)
                    user_obj.face_encoding = reason_text
                    db.session.add(user_obj)
                    db.session.commit()
                    res['state'] = 'success'
                    res['msg'] = '审核不通过'
        else:
            res['state'] = 'error'
            res['msg'] = '账户不存在'
            print('账户不存在')
    else:
        res['state'] = 'error'
        res['msg'] = '未获取到openid'
    return jsonify(res)