from flask_admin.form.upload import ImageUploadField
from flask_admin.form import thumbgen_filename
from flask_admin.contrib.sqla import ModelView
from flask_login import login_required
from flask import url_for
from main.models import User
from uuid import uuid4
from jinja2 import Markup
import os.path as op

File_path = op.join (op.dirname(__file__),'static')

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

    temp_uuid = str(uuid4())
    form_extra_fields = {
        'PICTURE': ImageUploadField('大頭照',
            base_path=File_path,
            relative_path=f'uploadFile/{temp_uuid}/',
            thumbnail_size=(60, 60, True)
        )
    }