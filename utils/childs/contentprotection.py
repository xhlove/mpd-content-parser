'''
作者: weimo
创建日期: 2021-01-01 15:11:56
上次编辑时间: 2021-01-01 15:11:56
一个人的命运啊,当然要靠自我奋斗,但是...
'''

from ..mpditem import MPDItem


class ContentProtection(MPDItem):
    def __init__(self, name: str):
        super(ContentProtection, self).__init__(name)
        self.value = None
        self.schemeIdUri = None
        self.cenc_default_KID = None