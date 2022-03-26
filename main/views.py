from main import app
from main import db
from main import login_manager
from flask_admin import Admin, BaseView, expose
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask import flash, url_for, redirect, render_template, request
from main.models import User, query_user, Job, Category, Equip
from main.user import UserAdmin
from main.equip import EquipAdmin

class MainProfile(AdminIndexView):
    @expose('/')
    @login_required
    def default(self):
        user_object = User.query.get(current_user.get_id())
        image_file = url_for('static', filename=user_object.PICTURE)

        orders=[
            {"order_id":"XD123", "job_name":"王曉明的婚紗照", "equip_count":20},
            {"order_id":"XD124", "job_name":"王曉明的婚紗照", "equip_count":30},
            {"order_id":"XD125", "job_name":"王曉明的婚紗照", "equip_count":40}
        ]
        return self.render(
            'profile.html', 
            account = user_object.ACCOUNT,
            position = user_object.POSITION,
            image_file = image_file,
            name = user_object.NAME,
            orders = orders
        )

###給蕙瑄弄 隨意一個領用單ID show出裡面所有器材 跟歸還器材按鈕
###可以先去oracle建假資料
class OrderEquipView(BaseView):
    @expose('/')
    def order_equip(self):
        return self.render('order_equip.html', lendingorder={})

class JobView(ModelView):
    can_create = True
    column_list = ('NAME', 'MANAGER_ACCOUNT',  'OWNER_NAME', 'OWNER_PHONE', 'LOCATION',"DESCRIPTION")
    form_columns = ('NAME', 'MANAGER_ACCOUNT','OWNER_NAME', 'OWNER_PHONE', 'LOCATION',  "DESCRIPTION")
    column_labels = dict(
        NAME="工作名稱",
        MANAGER_ACCOUNT="負責員工",
        LOCATION='工作地點',
        OWNER_NAME="業主姓名",
        OWNER_PHONE="業主連絡電話",
        DESCRIPTION="工作內容"
    )

    form_widget_args = {
        'DESCRIPTION': {
            'rows': 100,
            'style': 'font-family: monospace;'
        }
    }
    def __init__(self, session, **kwargs):
        super(JobView, self).__init__(Job, session, **kwargs)

class CateView(ModelView):
    can_create = True
    column_display_pk = False
    form_display_pk = False
    # column_list = ("CID","CNAME")
    # form_columns =  ("CID", "CNAME")
    column_labels = dict(
        CID="類別編號",
        CNAME="類別名稱"
    )
    def __init__(self, session, **kwargs):
        super(CateView, self).__init__(Category, session, **kwargs)

admin = Admin(app, name=u'EQMS',index_view=MainProfile(name='首頁'), template_mode='bootstrap3')
admin.add_view(OrderEquipView(name='領用單細項(蕙萱)'))
admin.add_view(UserAdmin(db.session, name = u'使用者管理'))
admin.add_view(JobView(db.session, name=u"工作管理"))
admin.add_view(CateView(db.session, name = u'類別管理'))
admin.add_view(EquipAdmin(db.session, name = u'器材管理'))

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
            curr_user.id = user_id
            print(curr_user)
            login_user(curr_user)
            return redirect('/admin')
        flash('帳號密碼錯誤!')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully!'