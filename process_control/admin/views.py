from flask import render_template, redirect, flash, url_for, session, request
from . import admin
from process_control.models import *
from sqlalchemy import and_, or_
from process_control.admin.forms import *
from functools import wraps
from process_control.admin.Recording_recognition import write_to_db
# 登录验证
def adimn_check_login(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if not session.get('account'):
            return redirect(url_for('admin.login', next=request.url))
        return func(*args, **kwargs)

    return decorated_func


# 登录
@admin.route('/login/', methods=['get', 'post'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        account = data['account']
        pwd = data['pwd']
        user = Userinfo.query.filter(Userinfo.account==account).filter(Userinfo.pwd==pwd).first()
        if user:
            # 账户存在
            is_admin = user.is_admin
            if is_admin == 1:
                # 该账户是管理员
                session['account'] = account
                session['openid'] = user.openid
                session['location'] = user.location
                return redirect(url_for('admin.msg_list', page=1))
            else:
                flash('该账户不是管理员！', 'err')
        else:
            flash('账户或密码不正确！', 'err')

    return render_template('admin/login.html', form=form)


# 服务记录查询
@admin.route('/', methods=['get'], endpoint='first')
@admin.route('/msg/list/<int:page>/', methods=['get', ])
@adimn_check_login
def msg_list(page=None):
    nickname = request.args.get('nickname', '')
    first_time = request.args.get('first_time', '')
    info1 = request.args.getlist('info1')
    check_to_audio = request.args.getlist('check_to_audio')
    phone = request.args.get('phone', '')
    location = session['location']
    # 若有条件，条件查询
    if nickname or first_time or info1 or phone:
        page_data = SignHistory.query.join(
            Userinfo, SignHistory.openid == Userinfo.openid).add_entity(
            Userinfo).filter(Userinfo.location==location)
        if nickname:
            print(page_data)
            print('------------------')
            page_data = page_data.filter(Userinfo.nickname.like(nickname))
        if first_time:
            mintime = first_time + ' ' + '0:0:0'
            maxtime = first_time + ' ' + '23:59:59'
            page_data = page_data.filter(SignHistory.time <= maxtime).filter(SignHistory.time >= mintime)
        if info1:
            if info1[0] == '0':
                page_data = page_data.filter(SignHistory.info1 == '装机')
            elif info1[0] == '1':
                page_data = page_data.filter(SignHistory.info1 == '修障')
            else:
                page_data = page_data
        if check_to_audio:
            if check_to_audio[0] == '0':
                page_data = page_data.filter(SignHistory.match_audio == None)
            elif check_to_audio[0] == '1':
                page_data = page_data.filter(SignHistory.match_audio != None)
            else:
                page_data = page_data
        if phone:
            page_data = page_data.filter(SignHistory.info3 == phone)
        page_data = page_data.order_by(SignHistory.time.desc()).paginate(page=page, per_page=10)
    else:
        if page == None:
            page = 1
        page_data = SignHistory.query.join(
            Userinfo, SignHistory.openid == Userinfo.openid).add_entity(Userinfo).filter(Userinfo.location==location).filter(SignHistory.match_audio==None).order_by(
            SignHistory.time.desc()).paginate(page=page, per_page=10)
        print('ooooooooooooooooo', page_data)
    print(page_data)
    # 搜索条件
    return render_template('admin/msglist.html', page_data=page_data)


# 注册信息审核
@admin.route('/check/<int:page>', methods=['get', ])
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
        page_data = Userinfo.query.filter(Userinfo.face_pass == None).order_by(
            Userinfo.first_time.desc()).paginate(page=page, per_page=10)
    return render_template('admin/checklist.html', page_data=page_data)


# 审核通过？
@admin.route('/pass_or_fail/', methods=['get', 'post'])
@adimn_check_login
def pass_or_fail():
    openid = request.args.get('openid', '')
    mark = request.args.get('mark', '')
    if openid:
        user_obj_list = Userinfo.query.filter(Userinfo.openid == openid)
        if user_obj_list:
            user_obj = user_obj_list.first()
            if int(mark) == 1:
                user_obj.face_pass = int(mark)
                db.session.add(user_obj)
                db.session.commit()
            else:
                reason_list = request.args.getlist('reason')
                reason_text = ''
                reason_text = '；'.join(reason_list)
                user_obj.face_pass = int(mark)
                user_obj.nopass_reason = reason_text
                db.session.add(user_obj)
                db.session.commit()
        else:
            print('账户不存在')

    return redirect(url_for('admin.check_list', page=1))


# 录音质检页
@admin.route('/audio/', methods=['get', 'post'])
@adimn_check_login
def audio_page():
    openid = request.args.get('openid', '')
    signid = request.args.get('signid', '')
    print(openid, signid)
    audio_obj = AudioRecord.query.filter(and_(AudioRecord.sign_id == signid, AudioRecord.openid == openid)).first()
    user_obj = Userinfo.query.filter(Userinfo.openid == openid).first()
    sign_obj = SignHistory.query.filter(and_(SignHistory.openid==openid, SignHistory.sign_id==signid)).first()
    # 照片地址
    '/opt/web/telecom_field_control/face_image/61-368b6f55505641e6bae524fb7cfe573e.jpg'
    if user_obj.face_image:
        photo_path = user_obj.face_image.replace('/opt/web/telecom_field_control', 'https://cnzhile.com/tfc')
    else:
        photo_path = ''
    audio_note = sign_obj.audio_note  # 录音备注
    if audio_obj is None:
        # 没有录音
        audio_path = ''
        audio_text = {}
        machine_judge = 0
        machine_judge_reason = '没有录音'
    else:
        # 录音地址
        audio_path = audio_obj.audio_path.replace('/opt/web/telecom_field_control', 'https://cnzhile.com/tfc')
        # 录音文本
        try:
            audio_text = eval(audio_obj.audio_text)
        except:
            audio_text = audio_obj.audio_text
        # 录音文本质检结果
        machine_judge = audio_obj.machine_judge
        machine_judge_reason = audio_obj.machine_judge_reason
    match_audio = sign_obj.match_audio
    match_location = sign_obj.match_location
    match_image = sign_obj.match_image
    print(match_audio,match_location,match_image)
    data = {
         'user_obj': user_obj,
        'openid': openid,
        'signid': signid,
        'audio_note': audio_note,
         'sign_obj': sign_obj,
        'audio_path': audio_path,
        'audio_text': audio_text,
        'photo_path': photo_path,
        'machine_judge': machine_judge,
        'machine_judge_reason': machine_judge_reason,
        'match_audio': match_audio,
        'match_location': match_location,
        'match_image': match_image,

    }
    return render_template('admin/audio.html', data=data)

# 录音质检提交
@admin.route('/submit_note/', methods=['post'])
@adimn_check_login
def submit_note():
    print('--------------')
    note = request.form.get('note', '')
    openid = request.form.get('openid', '')
    signid = request.form.get('signid', '')
    match_image = request.form.get('match_image', '')
    match_location = request.form.get('match_location', '')
    match_audio = request.form.get('match_audio', '')
    sign_history_obj = SignHistory.query.filter(and_(SignHistory.openid==openid, SignHistory.sign_id==signid)).first()
    print(match_image, match_location, match_audio, type(match_audio))  # 字符串
    # 如果match_image/location/audio 没有值，默认为1
    if not match_audio:
        match_audio = 1
    if not match_location:
        match_location = 1
    if not match_image:
        match_image = 1
    if openid and signid:
        sign_history_obj.audio_note = note
        sign_history_obj.match_audio = int(match_audio)
        sign_history_obj.match_location = int(match_location)
        sign_history_obj.match_image = int(match_image)
        db.session.add(sign_history_obj)
        db.session.commit()
        res = {
            'state': 'success',
            'msg': '备注添加成功'
        }
    else:
        res = {
            'state': 'fail',
            'msg': '录音未找到'
        }
    print(res)
    return res


# 操作语音质检标准
# 标准句子显示
@admin.route('/sentence_list/', methods=['get'])
@adimn_check_login
def standard_sentence_list():
    location = session['location']
    sentence_list = set(AudioStandard.query.with_entities(AudioStandard.sentence, AudioStandard.nessasery).filter(AudioStandard.area.startswith(location)).all())
    return render_template('admin/standard_home.html', data=sentence_list)

# 标准句删除
@admin.route('/sentence_del/', methods=['get', 'post'])
@adimn_check_login
def sentence_del():
    sentence = request.args.get('sentence', '')
    res = {'state': '', 'msg': ''}
    if sentence:
        aus = AudioStandard.query.filter(AudioStandard.sentence==sentence).all()
        for item in aus:
            db.session.delete(item)
            db.session.commit()
        res['state'] = 'success'
        res['msg'] = '删除成功'
        flash('删除成功！', 'ok')
        return redirect(url_for('admin.standard_sentence_list'))
    else:
        res['state'] = 'fail'
        res['msg'] = '删除失败'
    return res



# 标准句添加
@admin.route('/sentence_add/', methods=['get', 'post'])
@adimn_check_login
def sentence_add():
    if request.method == 'POST':
        nes = request.form.get('nes', '')
        sentence = request.form.get('sentence', '')
        print('nes...', nes)
        area = session['location']
        res = {'state': '', 'msg': ''}
        if nes=='' or sentence=='':
            print('come')
            res['state'] = 'fail'
            res['msg'] = '未填写内容或未选是否可说！'
            return res
        audio_standard = AudioStandard(
            area=area,
            sentence=sentence,
            nessasery=nes
        )
        db.session.add(audio_standard)
        db.session.commit()
        res['state'] = 'success'
        res['msg'] = '添加成功'
        print(res)
        return res
    return render_template('admin/standard_sentence_add.html')

# 标准句修改
@admin.route('/sentence_edit/', methods=['get', 'post'])
@adimn_check_login
def sentence_edit():
    old_sentence = request.args.get('sentence', '')
    if request.method == 'POST':
        new_sentence = request.form.get('sentence', '').strip()
        old_sentence = request.form.get('old_sentence', '').strip()
        res = {'state': '', 'msg': ''}
        if not new_sentence:
            res['state'] = 'fail'
            res['msg'] = '未输入内容！'
            print('未输入内容')
            return res
        audio_standards = AudioStandard.query.filter(AudioStandard.sentence==old_sentence).all()
        print(audio_standards)
        for audio_standard in audio_standards:
            audio_standard.sentence = new_sentence
            db.session.add(audio_standard)
            db.session.commit()
        res['state'] = 'success'
        res['msg'] = '修改成功'
        return res
    return render_template('admin/standard_sentence_edit.html', data=old_sentence)

# 相似句展示
@admin.route('/standard_simi_list/', methods=['get'])
@adimn_check_login
def standard_simi_list():
    refer = request.args.get('refer')
    word = request.args.get('word')
    if refer:
        simi = AudioStandard.query.filter(AudioStandard.keywords ==refer).with_entities(AudioStandard.sentence).first()
        word = simi[0]
    simi_list = set(AudioStandard.query.filter(AudioStandard.sentence==word).with_entities(AudioStandard.simi_sentence).all())
    return render_template('admin/standard_simi.html', data={'sentence': word, 'simi_list': simi_list})


# 相似句添加
@admin.route('/simi_add/', methods=['get', 'post'])
@adimn_check_login
def simi_add():
    sentence = request.args.get('sentence', '')
    if request.method == 'POST':
        simi = request.form.get('simi', '')
        sentence = request.form.get('sentence', '')
        res = {'state': '', 'msg': ''}
        if not simi:
            res['state'] = 'fail'
            res['msg'] = '未填写内容或填写不选！'
            return res
        nes = AudioStandard.query.filter(AudioStandard.sentence==sentence).with_entities(AudioStandard.nessasery).first()[0]
        area = session['location']
        # 判断已有的sentence中的simi_sentence是否为空，如果为空更新字段
        audio_standards = AudioStandard.query.filter(AudioStandard.sentence==sentence).all()
        print(audio_standards)
        mark = 0  # 字段是否更新标志
        for audio_standard in audio_standards:
            print('ssss', audio_standard.simi_sentence, type(audio_standard.simi_sentence))
            if audio_standard.simi_sentence == None:
                print('gaile')
                mark = 1
                audio_standard.simi_sentence = simi
                db.session.add(audio_standard)
                db.session.commit()
                break
            else:
                continue
        if not mark:
            # 未更新字段， 新增一条记录
            audio_s = AudioStandard(
                area=area,
                sentence=sentence,
                simi_sentence=simi,
                nessasery=nes
            )
            db.session.add(audio_s)
            db.session.commit()
        res['state'] = 'success'
        res['msg'] = '添加成功'
        print(res)
        return res
    return render_template('admin/standard_simi_sentence_add.html', data={'sentence': sentence})

# 相似句修改
import chardet
@admin.route('/simi_edit/', methods=['get', 'post'])
@adimn_check_login
def simi_edit():
    oldsimi = request.args.get('simi', '')
    sentence = request.args.get('sentence', '')
    if request.method == 'POST':
        new_simi = request.form.get('simi', '').strip()
        old_simi = request.form.get('old_simi', '').strip()
        sentence = request.form.get('sentence', '')
        res = {'state': '', 'msg': ''}
        if not new_simi:
            res['state'] = 'fail'
            res['msg'] = '未输入内容！'
            print('未输入内容')
            return res
        print(sentence)
        print('sentence,oldsimi', old_simi, sentence, type(sentence),)
        if old_simi == 'None':
            old_simi = None
        audio_standards = AudioStandard.query.filter(AudioStandard.sentence==sentence).filter(AudioStandard.simi_sentence==old_simi).all()
        print(audio_standards)
        for audio_standard in audio_standards:
            audio_standard.simi_sentence = new_simi
            db.session.add(audio_standard)
            db.session.commit()
        res['state'] = 'success'
        res['msg'] = '修改成功'
        print(res)
        return res
    return render_template('admin/standard_simi_sentence_edit.html', data={'oldsimi': oldsimi, 'sentence': sentence})


# 将录音转成文本并进行质检，存入数据库
@admin.route('/insert_db/')
def insert_db():
    area = session['location']
    try:
        write_to_db(area)
        return {'msg': '录音文本，质检插入成功'}
    except:
        return {'msg': '录音文本，质检插入失败'}


# 暂时不用
# @admin.route('/standard_key_word/', methods=['get'])
# def standard_key_word():
#     word = request.args.get('word')
#     print(word)
#     simi_list = AudioStandard.query.filter(AudioStandard.simi_sentence==word).with_entities(AudioStandard.keywords).all()
#     return render_template('admin/standard_keyword.html', data=simi_list)

# 测试
@admin.route('/test/', methods=['get'])
def test():
    return render_template('admin/base_standard.html')


