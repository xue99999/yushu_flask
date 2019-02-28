from flask import flash, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from app.models.base import db
from app.models.wish import Wish
from app.view_models.wish import MyWishes
from . import web


@web.route('/my/wish')
@login_required
def my_wish():
    trades_of_mine = Wish.get_user_wishes(current_user.id)
    isbn_list = [trade.isbn for trade in trades_of_mine]
    trades_count_list = Wish.get_gifts_count(isbn_list)
    view_model = MyWishes(trades_of_mine, trades_count_list)
    return render_template('my_wish.html', wishes=view_model.trades)


@web.route('/wishes/book/<isbn>')
@login_required
def save_to_wish(isbn):
    if current_user.can_save_to_list(isbn):
        with db.auto_commit():
            wish = Wish()
            wish.isbn = isbn
            wish.uid = current_user.id
            db.session.add(wish)
    else:
        flash('这本书已经在你的赠送清单或者已经存在你的心愿清单了，请不要重复添加')
    return redirect(url_for('web.book_detail', isbn=isbn))


@web.route('/wish/book/<isbn>/redraw')
@login_required
def redraw_from_wish(isbn):
    wish = Wish.query.filter_by(isbn=isbn, launched=False).first_or_404()
    with db.auto_commit():
        wish.delete()
    return redirect(url_for('web.my_wish'))


@web.route('/satisfy/wish/<int:wid>')
@login_required
def satisfy_wish(wid):
    wish = Wish.query.get_or_404(wid)
    from app.models.gift import Gift
    gift = Gift.query.filter_by(uid=current_user.id, isbn=wish.isbn).first_or_404()
    if not gift:
        flash('你还没有上传此书, '
              '请点击“加入到赠送清单”添加此书。添加前，请确保自己可以赠送此书')
    else:
        # 发送邮件或者短信
        flash('已向他/她发送了一封邮件，如果他/她愿意接受你的赠送，你将收到一个鱼漂')
    return redirect(url_for('web.book_detail', isbn=wish.isbn))



