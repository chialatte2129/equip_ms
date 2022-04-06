from main import app
from main import db, cursor, connection
from main import login_manager
from flask_admin import Admin, BaseView, expose
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import login_user, current_user, login_required, logout_user
from flask import flash, url_for, redirect, render_template, request
from main.models import User, query_user, Job, Category, Equip, LendingOrder
from main.user import UserAdmin
from main.equip import EquipAdmin
from datetime import datetime
from flask_babelex import Babel

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
    for i in data:
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

def get_order(order_id)->list:
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
        WHERE LO.JID = JB.JID AND LO.OID=:oid
        GROUP BY LO.OID, RECEIVE_DATE, RETURN_DATE, REASON, JB.NAME
        ORDER BY RECEIVE_DATE desc
    """
    cursor.prepare(sql)
    cursor.execute(None, {'oid':order_id})
    data = cursor.fetchall()  
    result = {
        '領用單編號': data[0][0],
        '領用日期': data[0][1],
        '歸還日期': data[0][2],
        '領用原因': data[0][3],
        '所屬工作': data[0][4],
        '領用數量':data[0][5]
    }
    return result


def lending_order_detail(lending_id)->list:
    sql=f"""
        SELECT 
            E.EID EID, 
            E.PNAME E_NAME,
            LISTAGG(C.CNAME, ', ') WITHIN GROUP(ORDER BY C.CNAME) CATES,
            E.BUY_DATE BUY_DATE,
            E.status,
            E.PICTURE PICTURE

        FROM EQUIP E, EQUIPCATE EC, CATEGORY C, LENDINGORDER LO
        WHERE E.EID=EC.EID AND EC.CID=C.CID AND LO.OID = :id AND E.EID in (
            SELECT EID FROM ORDEREQUIP WHERE OID = :id
        )
        GROUP BY E.EID, E.PNAME, E.BUY_DATE, E.PICTURE, E.STATUS
    """
    cursor.prepare(sql)
    cursor.execute(None, {'id':lending_id})
    data = cursor.fetchall()
    res_data = []
    for i in data:
        item = {
            '物品編號': i[0],
            '物品類別': i[1],
            '物品名稱': i[2],
            '採購日期': i[3],
            '領用狀態': i[4],
            '圖片檔': i[5]
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

class OrderEquipView(BaseView):
    def is_visible(self):
        # This view won't appear in the menu structure
        return False
    @expose('/')
    @login_required
    def index(self,id):
        lendingorder=lending_order_detail(id)
        order=get_order(id)
        print(order["歸還日期"]=="--")
        return self.render(
            'order_equip.html', 
            oId = id,
            order = order,                 #領用單
            lendingorder = lendingorder,    #領用單明細
            show_return=order["歸還日期"]=="--"
        )

class UpdateLendingOrderView(BaseView):
    def is_visible(self):
        return False
 
    @expose('/', methods=['GET', 'POST'])
    @login_required
    def index(self,id):
        if request.method == 'GET':
            return self.render('return_equip.html', return_oid = id)
        else:
            oid = request.values['return_btn']
            cursor.prepare(f"UPDATE LENDINGORDER SET RETURN_DATE = SYSDATE WHERE OID = {int(oid)}")
            cursor.execute(None,{})
            connection.commit()
            cursor.prepare(f"UPDATE EQUIP SET STATUS = 0 WHERE EID IN(SELECT EID FROM ORDEREQUIP WHERE ORDEREQUIP.OID = {int(oid)})")
            cursor.execute(None,{})
            connection.commit()
            return redirect('/')
            

class NewLendingOrderView(BaseView):
    def is_visible(self):
        return False
 
    @expose('/', methods=['GET', 'POST'])
    @login_required
    def index(self):
        if request.method == 'GET':
            allow_jobs = Job.query.all()
            job_list = []
            for row in allow_jobs:
                job_list.append({"id":row.JID, "name":row.NAME})

            allow_equip = Equip.query.filter_by(STATUS=0)
            equip_list = []
            for row in allow_equip:
                equip_list.append({"id":row.EID, "name":row.PNAME})

            user_object = User.query.get(current_user.get_id())
            form_data = {
                "P_NAME":user_object.NAME,
                "RECIEVE_DATE":datetime.today().strftime('%Y-%m-%d')
            }
            return self.render('new_lending_order.html', data=form_data, job_list=job_list, equip_list=equip_list)
        else:
            form_dict = request.values.to_dict(flat=False)
            recieve_date = request.values.get('recieve_date')
            job = request.values.get('job')
            reason = request.values.get('reason')
            equips = form_dict["equips"] if "equips" in form_dict else []

            if not reason :
                flash('領用事由不可為空!')
                return redirect('/admin/new_order')
            if not equips:
                flash('領用器材不可為空!')
                return redirect('/admin/new_order')
            
            cursor.prepare(f"INSERT INTO LENDINGORDER VALUES (null, to_date('{recieve_date}','yyyy-mm-dd'), null, '{reason}', {int(job)}, '{current_user.get_id()}')")
            cursor.execute(None,{})
            connection.commit()
            new_id = LendingOrder.query.order_by(LendingOrder.OID.desc()).first().OID
            for item in equips:
                cursor.prepare(f"INSERT INTO ORDEREQUIP VALUES ({new_id},{item})")
                cursor.execute(None,{})
                connection.commit()
                equip_obj = Equip.query.get(item)
                equip_obj.STATUS = 1
                db.session.commit()
            return redirect('/')

class LogoutView(BaseView):
    @expose('/')
    def logout(self):
        return redirect('/logout')

class JobView(ModelView):
    can_create = True
    column_list = ('NAME', 'MANAGER_ACCOUNT',  'OWNER_NAME', 'OWNER_PHONE', 'LOCATION',"DESCRIPTION")
    form_columns = ('NAME', 'MANAGER_ACCOUNT','OWNER_NAME', 'OWNER_PHONE', 'LOCATION',  "DESCRIPTION")
    column_labels = dict(
        NAME="工作名稱",
        MANAGER_ACCOUNT="負責人",
        LOCATION='工作地點',
        OWNER_NAME="業主",
        OWNER_PHONE="業主電話",
        DESCRIPTION="工作內容"
    )

    form_widget_args = {
        'DESCRIPTION': {
            'rows': 100,
            'style': 'font-family: monospace;'
        }
    }

    def is_accessible(self):#登錄了才能顯示，沒有登錄就不顯示
        user_object = User.query.get(current_user.get_id())
        return user_object.AUTH=="system"
    
    def is_visible(self):
        user_object = User.query.get(current_user.get_id())
        return user_object.AUTH=="system"

    def __init__(self, session, **kwargs):
        super(JobView, self).__init__(Job, session, **kwargs)

class CateView(ModelView):
    can_create = True
    column_display_pk = False
    form_display_pk = False
    column_labels = dict(
        CID="類別編號",
        CNAME="類別名稱"
    )

    def is_accessible(self):#登錄了才能顯示，沒有登錄就不顯示
        user_object = User.query.get(current_user.get_id())
        return user_object.AUTH=="system"
    
    def is_visible(self):
        user_object = User.query.get(current_user.get_id())
        return user_object.AUTH=="system"

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

    def is_accessible(self):#登錄了才能顯示，沒有登錄就不顯示
        user_object = User.query.get(current_user.get_id())
        return user_object.AUTH=="system"
    
    def is_visible(self):
        user_object = User.query.get(current_user.get_id())
        return user_object.AUTH=="system"

    def __init__(self, session, **kwargs):
        super(LendingOrderView, self).__init__(LendingOrder, session, **kwargs)

admin = Admin(app, name=u'EQMS',index_view=MainProfile(name='首頁'), template_mode='bootstrap4')
babel = Babel()
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_TW'
babel.init_app(app)
admin.add_view(OrderEquipView(url="order/<id>"))
admin.add_view(UpdateLendingOrderView(url="return/<id>"))
admin.add_view(NewLendingOrderView(url="new_order"))
admin.add_view(UserAdmin(db.session, url="user", name = u'使用者管理'))
admin.add_view(JobView(db.session, url="job", name=u"工作管理"))
admin.add_view(CateView(db.session, url="cate", name = u'類別管理'))
admin.add_view(EquipAdmin(db.session, url="equip", name = u'器材管理'))
admin.add_view(LendingOrderView(db.session, url="lending_record", name = u'領用單紀錄'))
admin.add_view(LogoutView(name=u'登出'))

@login_manager.user_loader
def load_user(user_id):
    if query_user(user_id) is not None:
        curr_user = User()
        curr_user.id = user_id

        return curr_user

@app.route('/')
def index():
    if current_user.get_id():
        return redirect("/admin")
    else:
        return redirect(url_for('login'))

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
    return redirect(url_for('login'))
    # return 'Logged out successfully!'