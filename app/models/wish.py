from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, desc, func
from sqlalchemy.orm import relationship
from app.models.base import Base, db


class Wish(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    launched = Column(Boolean, default=False)
    user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))
    isbn = Column(String(15), nullable=False)
    # 因为自己数据库没有内容，所以注释掉关系模型
    # book = relationship('Book')
    # bid = Column(Integer, ForeignKey('book.id'))

    # 赠书清单
    @classmethod
    def get_user_wishes(cls, uid):
        wishes = Wish.query.filter_by(
            uid=uid, launched=False).order_by(
            desc(Wish.create_time)).all()
        return wishes

    @classmethod
    def get_gifts_count(cls, isbn_list):
        # 传入的一组isbn， 到wish表中计算出某个礼物
        # 的wish心愿数量
        # 一个数量嘛？
        # 一组数量
        # mysql in
        # isbn wish的数量
        # db.session 可查询任意模型
        from app.models.gift import Gift
        count_list = db.session.query(func.count(Gift.isbn), Gift.isbn).filter(Gift.launched == False,
                                                                               Gift.isbn.in_(isbn_list),
                                                                               Gift.status == 1).group_by(
            desc(Gift.isbn)).all()
        count_list = [{'count': w[0], 'isbn': w[1]}for w in count_list]
        return count_list
