from main import app
from main import db
from main import login_manager
from flask_admin import Admin, BaseView, expose
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask import flash, url_for, redirect, render_template, request
from main.models import User, query_user
from main.user import UserAdmin

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

# class MyRecord(BaseView):
#     @expose('/my')
#     @login_required
#     def index(self):
#         return self.render('index.html')

admin = Admin(app, name=u'EQMS',index_view=MainProfile(name='首頁'), template_mode='bootstrap3')
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