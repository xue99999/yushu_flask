from operator import or_

from flask import flash, url_for, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import desc
from werkzeug.utils import redirect

from app.forms.book import DriftForm
from app.libs.enum import PendingStatus
from app.models.base import db
from app.models.drift import Drift
from app.models.user import User
from app.view_models.book import BookViewModel
from app.view_models.drift import DriftCollection
from . import web


@web.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    # 1.自己不能索要自己的书
    # 2.鱼豆数量要满足
    # 3.每索要2本书，就要赠送一本书
    from app.models.gift import Gift
    current_gift = Gift.query.get_or_404(gid)
    if current_gift.in_yourself_gift(current_user.id):
        flash('这本书是你自己的，不能向自己索要书籍哦')
        return redirect(url_for('web.book_detail', isbn=current_gift.isbn))

    can = current_user.can_send_drift()
    if not can:
        return render_template('not_enoformugh_beans.html', beans=current_user.beans)

    form = DriftForm(request.form)
    if request.method == 'POST' and form.validate():
        save_drift(form, current_gift)
        # 发通知（短信/邮件）
        return redirect(url_for('web.pending'))

    gifter = current_gift.user.summary
    return render_template('drift.html', gifter=gifter, beans=current_user.beans, form=form)


@web.route('/pending')
@login_required
def pending():
    drifts = Drift.query.filter(
        or_(Drift.requester_id==current_user.id, Drift.gifter_id==current_user.id)).order_by(
            desc(Drift.create_time)
    ).all()

    views = DriftCollection(drifts, current_user.id)
    return render_template('pending.html', drifts=views.data)


@web.route('/drift/<int:did>/redraw')
@login_required
def redraw_drift(did):
    # 超权
    # uid:1  did:1
    # uid:2  did:2
    # 这里我们处理方式为：查询请求者id是否为自己
    with db.auto_commit():
        drift = Drift.query.filter_by(
            requester_id=current_user.id, id=did).first_or_404()
        drift.pending = PendingStatus.Redraw
        current_user.beans += 1
    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/reject')
@login_required
def reject_drift(did):
    # 超权
    # uid:1  did:1
    # uid:2  did:2
    # 这里我们处理方式为：查询请求者id是否为自己
    with db.auto_commit():
        from app.models.gift import Gift
        drift = Drift.query.filter(
            Gift.uid==current_user.id, Drift.id==did).first_or_404()
        drift.pending = PendingStatus.Reject
        requester = User.query.get_or_404(drift.requester_id)
        requester.beans += 1
    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/mailed')
@login_required
def mailed_drift(did):
    with db.auto_commit():
        # 修改dirft状态为 成功
        drift = Drift.query.filter_by(
            gifter_id=current_user.id, id=did).first_or_404()
        drift.pending = PendingStatus.Success

        # 邮寄成功修改礼物状态 为 已赠送
        from app.models.gift import Gift
        gift = Gift.query.filter_by(id=drift.gift_id).first_or_404()
        gift.launched = True

        # 邮寄成功修改心愿清单状态 为 已完成
        from app.models.wish import Wish
        wish = Wish.query.filter_by(
            isbn=drift.isbn, uid=drift.requester_id, launched=False).first_or_404()
        wish.launched = True
        # 更新某个字段的另一种写法
        # Wish.query.filter_by(
        #     isbn=drift.isbn, uid=drift.requester_id,
        #     launched=False).update({Wish.launched: True})

    return redirect(url_for('web.pending'))


def save_drift(drift_form, current_gift):
    with db.auto_commit():
        drift = Drift()
        drift_form.populate_obj(drift)

        drift.requester_id = current_user.id
        drift.requester_name = current_user.nickname
        drift.gifter_id = current_gift.user.id
        drift.gift_id = current_gift.id
        drift.gifter_nickname = current_gift.user.nickname

        book = BookViewModel(current_gift.book)

        drift.isbn = book.isbn
        drift.book_title = book.title
        drift.book_author = book.author
        drift.book_img = book.image

        # 减去一个鱼豆
        current_user.beans -= 1

        db.session.add(drift)
