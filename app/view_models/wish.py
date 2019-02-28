from app.spider.yushu_book import YuShuBook
from app.view_models.book import BookViewModel


class MyWishes:
    def __init__(self, trades_of_mine, trade_count_list):
        self.trades = []

        self.__trades_of_mine = trades_of_mine
        self.__trade_count_list = trade_count_list

        self.trades = self.__parse()

    def __parse(self):
        temp_trades = []
        for trade in self.__trades_of_mine:
            my_trade = self.__matching(trade)
            temp_trades.append(my_trade)
        return temp_trades

    def __matching(self, trade):
        count = 0
        for trade_count in self.__trade_count_list:
            if trade.isbn == trade_count['isbn']:
                count = trade_count['count']
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(trade.isbn)
        r = {
            'wishes_count': count,
            'book': BookViewModel(yushu_book.first),
            'id': trade.id
        }
        return r
