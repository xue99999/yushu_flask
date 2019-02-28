from app.libs.enum import PendingStatus


class DriftCollection:
    def __init__(self, drifts, current_user_id):
        self.data = []

        self.__parse(drifts, current_user_id)

    def __parse(self, drifts, current_user_id):
        for drift in drifts:
            temp = DriftViewModel(drift, current_user_id)
            self.data.append(temp.data)


class DriftViewModel:
    def __init__(self, drift, current_user_id):
        self.data = {}

        self.data = self.__parse(drift, current_user_id)

    @staticmethod
    def requester_or_gifter(drift, current_user_id):
        if drift.requester_id == current_user_id:
            you_are = 'requester'
        else:
            you_are = 'gifter'
        return you_are

    def __parse(self, drift, current_user_id):
        you_are = self.requester_or_gifter(drift, current_user_id)
        pending_status = PendingStatus.pending_str(drift.pending, you_are)

        r = {
            'you_are': you_are,
            'operator': drift.requester_name if you_are != 'requester'
                else drift.gifter_nickname,
            'drift_id': drift.id,
            'book_title': drift.book_title,
            'book_author': drift.book_author,
            'book_img': drift.book_img,
            # 注意这里的create_datetime在Base里面做成了一个属性
            'date': drift.create_datetime.strftime('%Y-%m-%d'),
            'message': drift.message,
            'address': drift.address,
            'mobile': drift.mobile,
            'recipient_name': drift.recipient_name,
            'status': drift.pending,
            # 拼接的状态
            'status_str': pending_status
        }

        return r
