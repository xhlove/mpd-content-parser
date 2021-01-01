'''
作者: weimo
创建日期: 2021-01-01 15:11:56
上次编辑时间: 2021-01-01 15:12:48
一个人的命运啊,当然要靠自我奋斗,但是...
'''

from ..mpditem import MPDItem


class CencPssh(MPDItem):
    def __init__(self, name: str):
        super(CencPssh, self).__init__(name)