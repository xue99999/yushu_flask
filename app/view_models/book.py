class BookViewModel:
    def __init__(self, book):
        self.isbn = book['isbn']
        self.image = book['image']
        self.title = book['title']
        self.author = "、".join(book['author'])
        self.price = book['price']
        self.pages = book['pages']
        self.publisher = book['publisher']
        self.summary = book['summary']
        self.binding = book['binding']
        self.pubdate = book['pubdate']


class BookCollection:
    def __init__(self):
        self.total = 0
        self.books = []
        self.keyword = ''

    def fill(self, yushu_book, keyword):
        self.total = yushu_book.total
        self.keyword = keyword
        self.books = [BookViewModel(book) for book in yushu_book.books]


class _BookViewModel:
    # 描述特征 (类变量，实例变量)
    # 行为 (方法)
    # 面向过程
    @classmethod
    def package_single(cls, data, keyword):
        returned = {
            'books': [],
            'total': 0,
            'keyword': keyword,
        }

        if data:
            returned['total'] = 1
            returned['books'] = [cls._cut_data(data)]

        return returned

    @classmethod
    def package_collection(cls, data, keyword):
        returned = {
            'books': [],
            'total': 0,
            'keyword': keyword,
        }

        if data:
            returned['total'] = data['total']
            returned['books'] = [cls._cut_data(book) for book in data['books']]

        return returned

    @classmethod
    def _cut_data(cls, data):
        return {
            'title': data['title'],
            'author': "、".join(data['author']),
            'price': data['price'],
            'pages': data['pages'] or '',
            'publisher': data['publisher'],
            'summary': data['summary'] or '',
        }

