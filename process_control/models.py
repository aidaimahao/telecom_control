# coding: utf-8
from sqlalchemy.ext.declarative import declarative_base
from process_control import db
Base = declarative_base()
metadata = Base.metadata


class AudioRecord(db.Model):
    __tablename__ = 'audio_record'

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    openid = db.Column(db.String(32))
    time = db.Column(db.DateTime)
    audio_path = db.Column(db.Text)
    sign_id = db.Column(db.String(32))
    machine_judge = db.Column(db.SmallInteger)
    user_judge = db.Column(db.SmallInteger)
    user_judge_reason = db.Column(db.Text)
    machine_judge_reason = db.Column(db.Text)
    audio_text = db.Column(db.Text)
    def test_schema(self):
        return {
            'id': self.id,
            'openid': self.openid,
            'time': self.time,
            'audio_path': self.audio_path,
            'sign_id': self.sign_id,
        }



class SignHistory(db.Model):
    __tablename__ = 'sign_history'

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    openid = db.Column(db.String(32))
    face_encoding = db.Column(db.Text)
    state = db.Column(db.SmallInteger)
    time = db.Column(db.DateTime)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    sign_id = db.Column(db.String(32))
    info1 = db.Column(db.String(50))
    info2 = db.Column(db.String(50))
    info3 = db.Column(db.String(50))
    audio_note = db.Column(db.Text)
    match_image = db.Column(db.SmallInteger)
    match_location = db.Column(db.SmallInteger)
    match_audio = db.Column(db.SmallInteger)
    def test_schema(self):
        return {
            'id': self.id,
            'openid': self.openid,
            'face_encoding': self.face_encoding,
            'state': self.state,
            'time': self.time,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'sign_id': self.sign_id,
            'info1': self.info1,
            'info2': self.info2,
            'info3': self.info3,
        }

class Userinfo(db.Model):
    __tablename__ = 'userinfo'

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    openid = db.Column(db.String(32), index=True)
    nickname = db.Column(db.String(20))
    face_image = db.Column(db.Text)
    is_admin = db.Column(db.SmallInteger)
    first_time = db.Column(db.DateTime)
    face_pass = db.Column(db.SmallInteger)
    job_number = db.Column(db.String(45))
    phone_number = db.Column(db.String(45))
    location = db.Column(db.String(45))
    nopass_reason = db.Column(db.Text)
    account = db.Column(db.String(20))
    pwd = db.Column(db.String(12))
    def test_schema(self):
        return {
            'id': self.id,
            'openid': self.openid,
            'nickname': self.nickname,
            'face_image': self.face_image,
            'first_time': self.first_time,
            'face_pass': self.face_pass,
            'job_number': self.job_number,
            'phone_number': self.phone_number,
        }


class AudioDirty(db.Model):
    __tablename__ = 'audio_dirty'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dirty = db.Column(db.Text)


class AudioStandard(db.Model):
    __tablename__ = 'audio_standard'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    area = db.Column(db.String(11), nullable=False)
    sentence = db.Column(db.String(64), nullable=False)
    simi_sentence = db.Column(db.String(64))
    keywords = db.Column(db.String(11))
    nessasery = db.Column(db.Integer, nullable=False)

