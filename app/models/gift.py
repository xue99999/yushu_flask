from flask import current_app
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, desc, func
from sqlalchemy.orm import relationship
from app.models.base import Base, db
from app.spider.yushu_book import YuShuBook


class Gift(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    launched = Column(Boolean, default=False)
    user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))
    isbn = Column(String(15), nullable=False)
    # 因为自己数据库没有内容，所以注释掉关系模型
    # book = relationship('Book')
    # bid = Column(Integer, ForeignKey('book.id'))

    def in_yourself_gift(self, uid):
        return True if self.uid == uid else False

    # 赠书清单
    @classmethod
    def get_user_gifts(cls, uid):
        gifts = Gift.query.filter_by(
            uid=uid, launched=False).order_by(
            desc(Gift.create_time)).all()
        return gifts

    @classmethod
    def get_wish_count(cls, isbn_list):
        from app.models.wish import Wish
        # 传入的一组isbn， 到wish表中计算出某个礼物
        # 的wish心愿数量
        # 一个数量嘛？
        # 一组数量
        # mysql in
        # isbn wish的数量
        # db.session 可查询任意模型
        count_list = db.session.query(func.count(Wish.isbn), Wish.isbn).filter(Wish.launched == False,
                                                   Wish.isbn.in_(isbn_list),
                                                   Wish.status == 1).group_by(
            desc(Wish.isbn)).all()
        count_list = [{'count': w[0], 'isbn': w[1]}for w in count_list]
        return count_list

    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    @classmethod
    def recent(cls):
        # .distinct().group_by(Gift.isbn) mysql去重写法
        recent_gifts = Gift.query.filter_by(launched=False).group_by(
            Gift.isbn).order_by(
            desc(Gift.create_time)).limit(
            current_app.config['RECENT_LIMIT_NUMBER']).distinct().all()
        return recent_gifts
