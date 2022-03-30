from typing import List
from main import app
from main import db, cursor
from main import login_manager
from flask_admin import Admin, BaseView, expose
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask import flash, url_for, redirect, render_template, request
from main.models import User, query_user, Job, Category, Equip, LendingOrder
from main.user import UserAdmin
from main.equip import EquipAdmin

def my_lending_order(account)->list:
    sql="""
        SELECT 
            LO.OID, 
            TO_CHAR(RECEIVE_DATE, 'YYYY-MM-DD'), 
            COALESCE(TO_CHAR(RETURN_DATE, 'YYYY-MM-DD'),'--'),
            REASON, 
            JB.NAME, 
            COUNT(OE.EID)
        FROM LENDINGORDER LO
        LEFT OUTER JOIN JOB JB ON LO.JID = JB.JID
        LEFT OUTER JOIN ORDEREQUIP OE ON LO.OID = OE.OID
        WHERE LO.JID = JB.JID AND LO.ACCOUNT = :account
        GROUP BY LO.OID, RECEIVE_DATE, RETURN_DATE, REASON, JB.NAME
        ORDER BY RECEIVE_DATE desc
    """
    cursor.prepare(sql)
    cursor.execute(None, {'account':account})
    data = cursor.fetchall()
    res_data = []
    print(data)
    for i in data:
        print(i)
        item = {
            '領用單編號': i[0],
            '領用日期': i[1],
            '歸還日期': i[2],
            '領用原因': i[3],
            '所屬工作': i[4],
            '領用數量':i[5]
        }
        res_data.append(item)
    return res_data

class MainProfile(AdminIndexView):
    @expose('/')
    @login_required
    def default(self):
        user_object = User.query.get(current_user.get_id())
        image_file = url_for('static', filename=user_object.PICTURE)

        orders=my_lending_order(user_object.ACCOUNT)
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

class LendingOrderView(ModelView):
    # can_create = False
    # can_edit=False
    column_list = ('OID', 'REASON', 'LENDING_ACCOUNT', 'ORDER_JOB', 'RECEIVE_DATE', 'RETURN_DATE','EQUIP')
    form_columns = ('REASON','LENDING_ACCOUNT','ORDER_JOB',  'RECEIVE_DATE', 'RETURN_DATE','EQUIP')
    column_labels = dict(
        OID="領用單編號",
        REASON="領用事由",
        RECEIVE_DATE='領用日期',
        RETURN_DATE="歸還日期",
        ORDER_JOB="所屬工作",
        LENDING_ACCOUNT="領用人員",
        EQUIP="領用器材"
    )

    def __init__(self, session, **kwargs):
        super(LendingOrderView, self).__init__(LendingOrder, session, **kwargs)

admin = Admin(app, name=u'EQMS',index_view=MainProfile(name='首頁'), template_mode='bootstrap3')
admin.add_view(OrderEquipView(name='領用單細項(瑄瑄)'))
admin.add_view(UserAdmin(db.session, name = u'使用者管理'))
admin.add_view(JobView(db.session, name=u"工作管理"))
admin.add_view(CateView(db.session, name = u'類別管理'))
admin.add_view(EquipAdmin(db.session, name = u'器材管理'))
admin.add_view(LendingOrderView(db.session, name = u'領用單紀錄'))

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