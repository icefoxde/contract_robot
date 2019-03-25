from aes import Prpcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin

# 定义数据模型
db = SQLAlchemy()

# 系统用户  User
class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.VARCHAR(100))
    user_pass = db.Column(db.VARCHAR(100))
    user_email = db.Column(db.VARCHAR(100))
    user_depat = db.Column(db.VARCHAR(100))
    user_auth = db.Column(db.VARCHAR(100))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return self.user_id


# 要素表的每一项的名字
namelist = [
    "docx_bh", "docx_syy", "docx_xyrq", "docx_xydd", "docx_zrf",
    "docx_srf", "docx_zwf", "docx_zrffzr", "docx_srffzr", "docx_zwffzr",
    "docx_zrfzs", "docx_srfzs", "docx_zwfzs", "docx_zmbjye", "docx_lx",
    "docx_qtzq", "docx_ztzq", "docx_zrjk", "docx_zqje",
    "docx_wyj", "docx_jzr", "docx_bxze", "docx_bjye",
    "docx_qx", "docx_khyh", "docx_hm", "docx_zh", "docx_jybzz"
]

class docx_table(db.Model):
    __tablename__ = 'docx_table'
    docx_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    docx_bh = db.Column(db.TEXT)
    docx_syy = db.Column(db.TEXT)
    docx_xyrq = db.Column(db.TEXT)
    docx_xydd = db.Column(db.TEXT)
    docx_zrf = db.Column(db.TEXT)
    docx_srf = db.Column(db.TEXT)
    docx_zwf = db.Column(db.TEXT)
    docx_zrffzr = db.Column(db.TEXT)
    docx_srffzr = db.Column(db.TEXT)
    docx_zwffzr = db.Column(db.TEXT)
    docx_zrfzs = db.Column(db.TEXT)
    docx_srfzs = db.Column(db.TEXT)
    docx_zwfzs = db.Column(db.TEXT)
    docx_zmbjye = db.Column(db.TEXT)
    docx_lx = db.Column(db.TEXT)
    docx_qtzq = db.Column(db.TEXT)
    docx_ztzq = db.Column(db.TEXT)
    docx_zrjk = db.Column(db.TEXT)
    docx_zqje = db.Column(db.TEXT)
    docx_wyj = db.Column(db.TEXT)
    docx_jzr = db.Column(db.TEXT)
    docx_bxze = db.Column(db.TEXT)
    docx_bjye = db.Column(db.TEXT)
    docx_qx = db.Column(db.TEXT)
    docx_khyh = db.Column(db.TEXT)
    docx_hm = db.Column(db.TEXT)
    docx_zh = db.Column(db.TEXT)
    docx_jybzz = db.Column(db.TEXT)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return 'User:%s' % self.name

    # aes加密的密钥
    __aes_key = "jcjjzgzzgsgss"

    @staticmethod
    def __encrypt(text):
        return Prpcrypt(docx_table.__aes_key).encrypt(text)

    @staticmethod
    def __decrypt(text):
        return Prpcrypt(docx_table.__aes_key).decrypt(text)

    @staticmethod
    def add_docx_table(dic):
        kwd = dict()
        for i in range(len(dic)):
            if isinstance(dic[i], list):
                kwd[namelist[i]] = docx_table.__encrypt(dic[i][0] + "#" + dic[i][1])
            else:
                kwd[namelist[i]] = docx_table.__encrypt(dic[i])

        d = docx_table(**kwd)
        db.session.add(d)
        db.session.commit()


# 登陆日志  Log
class Log(db.Model):
    __tablename__ = 'log'
    log_id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer)
    log_time = db.Column(db.DateTime)
    log_loc = db.Column(db.VARCHAR(100))
    log_ip = db.Column(db.VARCHAR(100))
    log_brow = db.Column(db.VARCHAR(100))

    def __init__(self,**kwargs):
        for key,value in kwargs.items():
            setattr(self,key,value)

# 意见反馈  Sugg
class Sugg(db.Model):
    __tablename__ = 'sugg'
    sugg_id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer)
    sugg_text = db.Column(db.VARCHAR(1000))

    def __init__(self,**kwargs):
        for key,value in kwargs.items():
            setattr(self,key,value)
# ------------------------------------------------------------------------
# -------------------------------------------------------------------------

