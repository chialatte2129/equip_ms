from flask_admin.form.upload import ImageUploadField
from flask_admin.form import thumbgen_filename
from flask_admin.form.fields import Select2Field
from flask_admin.contrib.sqla import ModelView
from flask_login import login_required
from flask import url_for
from main.models import Equip
from uuid import uuid4
from jinja2 import Markup
import os.path as op

File_path = op.join (op.dirname(__file__),'static')

class EquipView(ModelView):
    can_create = True
    form_columns = ( 'PNAME','BUY_DATE', 'STATUS', 'PICTURE', 'CATES')
    column_list = ( 'PNAME','BUY_DATE', 'STATUS', 'PICTURE')
    column_labels = dict(
        PNAME="器材名稱",
        BUY_DATE="採購日期",
        STATUS='領用狀態',
        PICTURE="器材照片",
        CATES="器材類別"
    )

    def __init__(self, session, **kwargs):
        super(EquipView, self).__init__(Equip, session, **kwargs)

class EquipAdmin(EquipView):
    def _list_thumbnail(view, context, model, name):
        if not model.PICTURE:
            return ''
        return Markup('<img src="%s">' % url_for('static',filename=thumbgen_filename(model.PICTURE)))

    column_formatters = {
        'PICTURE': _list_thumbnail
    }

    temp_uuid = str(uuid4())
    form_extra_fields = {
        'PICTURE': ImageUploadField('器材照片',
            base_path=File_path,
            relative_path=f'uploadFile/{temp_uuid}/',
            thumbnail_size=(60, 60, True)
        )
    }