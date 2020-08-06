import json
import time
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from process_control.models import AudioDirty, AudioStandard, AudioRecord
# 语言文件转文字
def fileTrans(fileLink, akId='LTAI4G7ZodNrMVZinxBMjobk', akSecret='p7xnHWyRSduKHqilQBQVBVL6taJdC7', appKey='kDQGgs3WNravwLfu') :
    # 地域ID，常量内容，请勿改变
    REGION_ID = "cn-shanghai"
    PRODUCT = "nls-filetrans"
    DOMAIN = "filetrans.cn-shanghai.aliyuncs.com"
    API_VERSION = "2018-08-17"
    POST_REQUEST_ACTION = "SubmitTask"
    GET_REQUEST_ACTION = "GetTaskResult"
    # 请求参数key
    KEY_APP_KEY = "appkey"
    KEY_FILE_LINK = "file_link"
    KEY_VERSION = "version"
    KEY_ENABLE_WORDS = "enable_words"
    # 是否开启智能分轨
    KEY_AUTO_SPLIT = "auto_split"
    # 响应参数key
    KEY_TASK = "Task"
    KEY_TASK_ID = "TaskId"
    KEY_STATUS_TEXT = "StatusText"
    KEY_RESULT = "Result"
    # 状态值
    STATUS_SUCCESS = "SUCCESS"
    STATUS_RUNNING = "RUNNING"
    STATUS_QUEUEING = "QUEUEING"
    # 创建AcsClient实例
    client = AcsClient(akId, akSecret, REGION_ID)
    # 提交录音文件识别请求
    postRequest = CommonRequest()
    postRequest.set_domain(DOMAIN)
    postRequest.set_version(API_VERSION)
    postRequest.set_product(PRODUCT)
    postRequest.set_action_name(POST_REQUEST_ACTION)
    postRequest.set_method('POST')
    # 新接入请使用4.0版本，已接入(默认2.0)如需维持现状，请注释掉该参数设置
    # 设置是否输出词信息，默认为false，开启时需要设置version为4.0
    task = {KEY_APP_KEY: appKey, KEY_FILE_LINK: fileLink, KEY_VERSION: "4.0", KEY_ENABLE_WORDS: False}
    # 开启智能分轨，如果开启智能分轨 task中设置KEY_AUTO_SPLIT : True
    # task = {KEY_APP_KEY : appKey, KEY_FILE_LINK : fileLink, KEY_VERSION : "4.0", KEY_ENABLE_WORDS : False, KEY_AUTO_SPLIT : True}
    task = json.dumps(task)
    print(task)
    postRequest.add_body_params(KEY_TASK, task)
    taskId = ""
    try :
        postResponse = client.do_action_with_exception(postRequest)
        postResponse = json.loads(postResponse.decode())
        statusText = postResponse[KEY_STATUS_TEXT]
        if statusText == STATUS_SUCCESS :
            print ("录音文件识别请求成功响应！")
            taskId = postResponse[KEY_TASK_ID]
        else :
            print ("录音文件识别请求失败！")
            return
    except ServerException as e:
        print (e)
    except ClientException as e:
        print (e)
    # 创建CommonRequest，设置任务ID
    getRequest = CommonRequest()
    getRequest.set_domain(DOMAIN)
    getRequest.set_version(API_VERSION)
    getRequest.set_product(PRODUCT)
    getRequest.set_action_name(GET_REQUEST_ACTION)
    getRequest.set_method('GET')
    getRequest.add_query_param(KEY_TASK_ID, taskId)
    # 提交录音文件识别结果查询请求
    # 以轮询的方式进行识别结果的查询，直到服务端返回的状态描述符为"SUCCESS"、"SUCCESS_WITH_NO_VALID_FRAGMENT"，
    # 或者为错误描述，则结束轮询。
    statusText = ""
    while True :
        try :
            getResponse = client.do_action_with_exception(getRequest)
            getResponse = json.loads(getResponse.decode())
            print(getResponse)
            statusText = getResponse[KEY_STATUS_TEXT]
            if statusText == STATUS_RUNNING or statusText == STATUS_QUEUEING :
                # 继续轮询
                time.sleep(10)
            else :
                # 退出轮询
                break
        except ServerException as e:
            print (e)
        except ClientException as e:
            print (e)
    if statusText == STATUS_SUCCESS :
        print ("录音文件识别成功！")
        return getResponse
    else :
        print ("录音文件识别失败！")
        return None
    return


# 录音文字内容检测
def audio_text_check(text_list, area='咸阳'):
    dirty = AudioDirty.query.with_entities(AudioDirty.dirty).all()
    keyword_way = AudioStandard.query.filter(AudioStandard.area.startswith(area)).with_entities(AudioStandard.sentence, AudioStandard.keywords, AudioStandard.nessasery).all()
    all_dirty = [x[0] for x in dirty]
    result = {'pass': 1, 'dirty_list': [], 'nopass_reason': []}
    key_dic = {x[0]: 0 for x in keyword_way}
    unnecessary_key_list = set([x[0] for x in keyword_way if x[2]==0])
    dirty_mark = 0
    print('keyway...', keyword_way)
    for text in text_list:
        # 污言秽语
        for item in all_dirty:
            if item in text:
                dirty_mark = 1
                result['dirty_list'].append(item)
        # 关键字判断
        for item in keyword_way:
            if item[1] is None:
                continue
            if item[1] in text:
                key_dic[item[0]] = 1
    if dirty_mark == 1:
        result['pass'] = 0
        result['nopass_reason'].append('存在谩骂言语！')
    for k, v in key_dic.items():
        if v == 0 and k not in unnecessary_key_list:
            # 一定要说的字段为0，不通过
            result['pass'] = 0
            result['nopass_reason'].append('无'+k)
        if k in unnecessary_key_list and v!=0:
            # 不能说的字段不为零，不通过
            # 存在不能说的文字
            result['pass'] = 0
            result['nopass_reason'].append('存在'+k)
        # 相似句

    return result



# 写进数据库
from collections import defaultdict
from process_control import db
# 语音文本写入数据库
def write_to_db(area):
    audios = AudioRecord.query.order_by(AudioRecord.time.desc()).all()
    for audio in audios:
        if audio.audio_text == None:
            audio_path = audio.audio_path.replace('/opt/web/telecom_field_control', 'https://cnzhile.com/tfc')
            change_index = 0
            text_dict = defaultdict(list)
            while True:
                if change_index == 3:
                    break
                ret = fileTrans(fileLink=audio_path)  # 转为文本
                print('-------', ret)
                if ret is None:
                    text_dict = text_dict
                else:
                    try:
                        audio_text_list = ret['Result']['Sentences']
                    except:
                        text_dict[0] = ['无内容']
                        break
                    for text in audio_text_list:
                        if text['ChannelId'] in text_dict.keys():
                            text_dict[text['ChannelId']].append(text['Text'])
                        else:
                            text_dict[text['ChannelId']] = [text['Text'], ]
                    text_dict = text_dict
                    break
                change_index += 1
            if len(text_dict) == 0:
                the_ret = '录音未识别'
                audio.audio_text = the_ret
                audio.machine_judge_reason = the_ret
                db.session.add(audio)
                db.session.commit()
            else:
                text_str = str(text_dict).replace("defaultdict(<class 'list'>, ", '').replace(')', '')
                audio.audio_text = text_str
                # 给machine_judge,machine_judge_reason赋值
                update_column(audio, area, text_str)
                db.session.add(audio)
                db.session.commit()

def update_column(audio, area, text_str):
        try:
            audio_text = eval(text_str)
        except:
            # 录音未识别，机器审核不通过
            print('录音未识别！审核不通过')
            audio.machine_judge = 0
            audio.machine_judge_reason = audio.audio_text
        print('录音文本已存在，进行机器质检。。。')
        print('录音文本：', audio_text)
        check_result = audio_text_check(audio_text[0], area)
        print('机器质检结果：', check_result)
        audio.machine_judge = check_result['pass']
        audio.machine_judge_reason = ';'.join(check_result['nopass_reason'])


#
# 测试用例
# accessKeyId = "LTAI4G7ZodNrMVZinxBMjobk"
# accessKeySecret = "p7xnHWyRSduKHqilQBQVBVL6taJdC7"
# appKey = "kDQGgs3WNravwLfu"
src="https://cnzhile.com/tfc/audio/d001add653e6464ba918949c5a11ff13.wav"
fileLink = "https://cnzhile.com/tfc/audio/opt_records_200707002449_200707002449_2020_07_08_103058"
# # fileLink = "https://aliyun-nls.oss-cn-hangzhou.aliyuncs.com/asr/fileASR/examples/nls-sample-16k.wav"
# # 执行录音文件识别
# ret = fileTrans(fileLink)
# print('ret----', ret['Result']['Sentences'][0]['Text'])