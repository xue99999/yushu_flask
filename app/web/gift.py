from flask import flash, current_app, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from app.libs.enum import PendingStatus
from app.models.base import db
from app.models.gift import Gift
from app.view_models.gift import MyGifts
from . import web


@web.route('/my/gifts')
@login_required
def my_gifts():
    uid = current_user.id
    gifts_of_mine = Gift.get_user_gifts(uid)
    isbn_list = [gift.isbn for gift in gifts_of_mine]
    wish_count_list = Gift.get_wish_count(isbn_list)
    view_model = MyGifts(gifts_of_mine, wish_count_list)
    return render_template('my_gifts.html', gifts=view_model.gifts)


@web.route('/personal/center')
@login_required
def personal_center():
    return 'personal_center'


@web.route('/gift/<gid>/redraw')
@login_required
def redraw_from_gifts(gid):
    # 撤销礼物，必须得看处于交易的哪一步，只有等待交易需要操作
    gift = Gift.query.filter_by(id=gid, launched=False).first_or_404()
    from app.models.drift import Drift
    drift = Drift.query.filter_by(gift_id=gid, pending=PendingStatus.Wating).first_or_404()
    if drift:
        flash('这个礼物处于交易状态，请先前往鱼漂完成该交易')
    else:
        with db.auto_commit():
            current_user.beans -= current_app.config['BEANS_UPLOAD_ONE_BOOK']
            gift.delete()
    return redirect(url_for('web.my_gifts'))


@web.route('/gifts/book/<isbn>')
@login_required
def save_to_gifts(isbn):
    if current_user.can_save_to_list(isbn):
        with db.auto_commit():
            gift = Gift()
            gift.isbn = isbn
            gift.uid = current_user.id
            current_user.beans += current_app.config['BEANS_UPLOAD_ONE_BOOK']
            db.session.add(gift)
    else:
        flash('这本书已经在你的赠送清单或者已经存在你的心愿清单了，请不要重复添加')
    return redirect(url_for('web.book_detail', isbn=isbn))


