from datetime import datetime

from . import Object


class Date(Object, datetime):

    @classmethod
    def wrap(cls, raw_object):
        date_time = datetime.fromtimestamp(raw_object)
        return super().__new__(cls, *date_time.timetuple()[:6])

    def __new__(
            cls,
            *args,
            **kwargs
    ):
        return super().__new__(cls, *args, *kwargs)

    def __init__(
            self,
            *args,
            **kwargs
    ):
        super().__init__(**kwargs)

    def __repr__(self):
        return str(self)

    def unwrap(self):
        return int(super().timestamp())
