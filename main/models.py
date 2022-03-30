from main import db
from datetime import datetime as dt



class User(db.Model):
    __tablename__ = 'USERS'
    __table_args__ = {'extend_existing': True}
    can_create = True
    ACCOUNT = db.Column(db.String(30), primary_key=True)
    PASSWORD = db.Column(db.String(30), nullable=False)
    NAME = db.Column(db.String(30), nullable=False)
    POSITION = db.Column(db.String(30))
    PICTURE = db.Column(db.String(200), unique=False, nullable=True)
    AUTH = db.Column(db.String(30), unique=False, nullable=True)
    # job_managet_account = db.relationship(Job, back_populates="user")

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        # return self.authenticated
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __repr__(self):
        return f'{self.NAME} <{self.ACCOUNT}>'

def query_user(user_id):
    for user in User.query.all():
        if user_id == user.ACCOUNT:
            return user

class Job(db.Model):
    __tablename__ = 'JOB'
    __table_args__ = {'extend_existing': True}
    can_create = True
    JID = db.Column(db.Integer(), primary_key=True , autoincrement=True)
    NAME = db.Column(db.String(45), nullable=False)
    MANAGER = db.Column(db.String(30), db.ForeignKey('USERS.ACCOUNT'), nullable=False)
    MANAGER_ACCOUNT = db.relationship(User, foreign_keys=[MANAGER])
    LOCATION = db.Column(db.String(45), nullable=False)
    OWNER_PHONE = db.Column(db.String(45))
    OWNER_NAME = db.Column(db.String(45), unique=False, nullable=True)
    DESCRIPTION = db.Column(db.String(128), unique=False, nullable=True)

    def __repr__(self):
        return f'{self.NAME}'

equip_cates = db.Table('EQUIPCATE', 
    db.Column("EID",db.Integer, db.ForeignKey('EQUIP.EID')),
    db.Column("CID",db.Integer, db.ForeignKey('CATEGORY.CID'))
)

class Category(db.Model):
    __tablename__ = 'CATEGORY'
    __table_args__ = {'extend_existing': True}
    can_create = True
    CID = db.Column(db.Integer(), primary_key=True , autoincrement=True)
    CNAME = db.Column(db.String(45), nullable=False)

    def __repr__(self):
        return f'{self.CNAME}'

class Equip(db.Model):
    __tablename__ = 'EQUIP'
    __table_args__ = {'extend_existing': True}
    can_create = True
    EID = db.Column(db.Integer(), primary_key=True , autoincrement=True)
    PNAME = db.Column(db.String(100), nullable=False)
    BUY_DATE = db.Column(db.Date, nullable=False, default=dt.utcnow)
    STATUS = db.Column(db.Integer(), default=0)
    PICTURE = db.Column(db.String(200))
    CATES = db.relationship('Category', secondary=equip_cates, backref=db.backref("EQUIP"), lazy="dynamic")

    def __repr__(self):
        return f'{self.PNAME}'

lending_equip = db.Table('ORDEREQUIP', 
    db.Column("EID",db.Integer, db.ForeignKey('EQUIP.EID')),
    db.Column("OID",db.Integer, db.ForeignKey('LENDINGORDER.OID'))
)

class LendingOrder(db.Model):
    __tablename__ = 'LENDINGORDER'
    __table_args__ = {'extend_existing': True}
    # can_create = True
    OID = db.Column(db.Integer(), primary_key=True , autoincrement=True)
    RECEIVE_DATE = db.Column(db.Date, nullable=True)
    RETURN_DATE = db.Column(db.Date, nullable=True)
    REASON = db.Column(db.String(500))
    JID = db.Column(db.Integer(), db.ForeignKey('JOB.JID'), nullable=False)
    ORDER_JOB = db.relationship(Job, foreign_keys=[JID])
    ACCOUNT = db.Column(db.String(30), db.ForeignKey('USERS.ACCOUNT'), nullable=False)
    LENDING_ACCOUNT = db.relationship(User, foreign_keys=[ACCOUNT])
    EQUIP = db.relationship('Equip', secondary=lending_equip, backref=db.backref("LENDINGORDER"))

    def __repr__(self):
        return '<Lending Order %r>' % self.REASON