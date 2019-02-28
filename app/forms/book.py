from wtforms import Form, StringField, IntegerField
from wtforms.validators import Length, DataRequired, NumberRange, Regexp


# 验证层


class SearchForm(Form):
    q = StringField(validators=[DataRequired(), Length(min=1, max=30)])
    page = IntegerField(validators=[NumberRange(min=1, max=99)], default=1)


class DriftForm(Form):
    recipient_name = StringField('收件人姓名', validators=[
        DataRequired(),
        Length(min=2, max=10, message='收件人姓名必须在2个到10个字')
    ])
    mobile = StringField('手机号', validators=[
        DataRequired(), Regexp('^1[0-9]{10}$', 0, '请输入正确的手机号')])
    message = StringField('留言')
    address = StringField('邮寄地址', validators=[
        DataRequired(),
        Length(min=10, max=70, message='地址还不到10个字嘛？尽量写详细点')
    ])
