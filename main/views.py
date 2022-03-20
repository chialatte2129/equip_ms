from main import app
from main import db
from main import login_manager
from flask_admin import Admin, BaseView, expose
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from flask_admin.form import thumbgen_filename
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask import flash, url_for, redirect, render_template, request
from main.models import User, query_user
import os.path as op
from uuid import uuid4
from jinja2 import Markup

File_path = op.join (op.dirname(__file__),'static')

class Profile(AdminIndexView):
    @expose('/')
    def default(self):
        plan = [
            {
                'date': '20171212',
                'train': 'T198',
                'track': '8'
            },
            {
                'date': '20171212',
                'train': 'T199',
                'track': '9'
            },
            {
                'date': '20171212',
                'train': 'T197',
                'track': '7'
            },
            {
                'date': '20171212',
                'train': 'T196',
                'track': '6'
            }
        ]
        return self.render('profile.html', plans = plan)

class MyRecord(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')

class UserView(ModelView):
    # Disable model creation
    can_create = True
    column_display_pk = True
    form_display_pk = True
    column_list = ('ACCOUNT','NAME', 'POSITION', 'PICTURE')
    form_columns = ( 'NAME','ACCOUNT', 'PASSWORD', 'POSITION', 'PICTURE')
    column_labels = dict(ACCOUNT="帳號",NAME="姓名",PICTURE='大頭照',PASSWORD="密碼",POSITION="職稱")
    def getinfo(self):
        return "this is another model"
    def __init__(self, session, **kwargs):
        super(UserView, self).__init__(User, session, **kwargs)

class UserAdmin(UserView):
    # Setting thumbnails
    def _list_thumbnail(view, context, model, name):
        if not model.PICTURE:
            return ''
        return Markup('<img src="%s">' % url_for('static',filename=thumbgen_filename(model.PICTURE)))
    # Image display of formatted list
    column_formatters = {
        'PICTURE': _list_thumbnail
    }
    # The extended list displays a 60*60 pixel Avatar
    temp_uuid = str(uuid4())
    form_extra_fields = {
        'PICTURE': ImageUploadField('大頭照',
            base_path=File_path,
            relative_path=f'uploadFile/{temp_uuid}/', # static中的路径
            thumbnail_size=(60, 60, True)
        ) # 大小限制
    }

admin = Admin(
    app, 
    name=u'EQMS',
    index_view=Profile(name='首頁'), 
    template_mode='bootstrap3'
)
# admin.add_view(MyRecord(name='我的領用單'))
admin.add_view(UserAdmin(db.session, name = u'員工帳號'))


@login_manager.user_loader
def load_user(user_id):
    if query_user(user_id) is not None:
        curr_user = User()
        curr_user.id = user_id

        return curr_user

@app.route('/')
@login_required
def index():
    return 'Logged in as: %s' % current_user.get_id()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('userid')
        user = query_user(user_id)
        if user is not None and request.form['password'] == user.PASSWORD:
            curr_user = user
            login_user(curr_user)
            return redirect('/admin')
        flash('帳號密碼錯誤!')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully!'