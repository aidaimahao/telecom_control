a = ['a', 'b', 'c']
b = [1, 3, 4]
ret = zip(a, b)
print(list(ret))
print()
import datetime
print(str(datetime.datetime.now()))

print(type(datetime.datetime.now()))
print(datetime.datetime.now())
from datetime import date

print(isinstance(1, int))
''.isdigit()

x = [1, 3, 4, 5]
if 3 in x:
    x.remove(3)
print(x)


l = ['sdfsd','sfd']
print(';'.join(l))


import os
print(os.path.realpath)

a = [
    ('a', 21),
    ('b', 21),
    ('a', 22),
    ('a', 21),
]
print(set(a))
from process_control.models import AudioDirty, AudioStandard,AudioRecord,Userinfo
from process_control.admin.Recording_recognition import audio_text_check, fileTrans,update_column,write_to_db
from process_control import db
from collections import defaultdict
if __name__ == '__main__':
    # s = ['然后他用完了你就点速结束了。', '对，然后打电话念佛结束是支持在录音嘛。对，那就是落现场的音。', '滚蛋', '效果']
    # ret = audio_text_check(s)
    # d = defaultdict(list)
    # print(len(d), 'aaaaaaaaaa')
    # if ret is None:
    #     print('ooo')
    # if d is None:
    #     print('ok')
    # s = str(d)
    # print(s, type(s))

    # write_to_db()
    # update_column()
    """
    {{url_for('admin.standard_simi_list')}}?refer={{data.0.0}}
    """
    # src="https://cnzhile.com/tfc/audio/fcd7a7a93db741f0b9f8f29045cf37e5.wav"
    # import time
    # start = time.time()
    # fileTrans(src)
    # end = time.time()
    # print(end-start)
    # write_to_db()
    update_column()

