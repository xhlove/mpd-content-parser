'''
作者: weimo
创建日期: 2021-01-01 15:10:41
上次编辑时间: 2021-01-01 16:41:28
一个人的命运啊,当然要靠自我奋斗,但是...
'''

from ..mpditem import MPDItem


class Role(MPDItem):
    def __init__(self, name: str):
        super(Role, self).__init__(name)
        self.schemeIdUri = None
        self.value = None