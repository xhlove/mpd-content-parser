'''
作者: weimo
创建日期: 2021-01-01 15:09:42
上次编辑时间: 2021-01-01 15:37:17
一个人的命运啊,当然要靠自我奋斗,但是...
'''

from ..mpditem import MPDItem


class BaseURL(MPDItem):
    def __init__(self, name: str):
        super(BaseURL, self).__init__(name)
        self.innertext = None