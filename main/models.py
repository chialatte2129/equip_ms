from main import db
import os

def get_upload_path():
    # do something
    return os.path.join("./main", "uploads", "images")

class User(db.Model):
    __tablename__ = 'USERS'
    __table_args__ = {'extend_existing': True}
    can_create = True
    ACCOUNT = db.Column(db.String(30), primary_key=True)
    PASSWORD = db.Column(db.String(30), nullable=False)
    NAME = db.Column(db.String(30), nullable=False)
    POSITION = db.Column(db.String(30))
    PICTURE = db.Column(db.String(128), unique=False, nullable=True)

    def is_active(self):
        """True, as all users are active."""
        return True
    
    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.ACCOUNT

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        # return self.authenticated
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
        
    def __repr__(self):
        return '<User %r>' % self.ACCOUNT

def query_user(user_id):
    for user in User.query.all():
        if user_id == user.ACCOUNT:
            return user 