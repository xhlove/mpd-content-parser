'''
作者: weimo
创建日期: 2021-01-01 15:09:55
上次编辑时间: 2021-01-01 15:37:36
一个人的命运啊,当然要靠自我奋斗,但是...
'''

from ..mpditem import MPDItem


class Period(MPDItem):
    def __init__(self, name: str):
        super(Period, self).__init__(name)
        self.id = None
        self.start = 0
        self.duration = 0.0