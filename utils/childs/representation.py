'''
作者: weimo
创建日期: 2021-01-01 15:10:52
上次编辑时间: 2021-01-01 17:16:39
一个人的命运啊,当然要靠自我奋斗,但是...
'''

from ..mpditem import MPDItem


class Representation(MPDItem):
    def __init__(self, name: str):
        super(Representation, self).__init__(name)
        self.id = None
        self.bandwidth = None
        self.codecs = None
        self.mimeType = None
        self.sar = None
        self.width = None
        self.height = None
        self.audioSamplingRate = None

    def get_contenttype(self):
        if self.mimeType is not None:
            return self.mimeType.split('/')[0].title()

    def get_resolution(self):
        return f"{self.width}x{self.height}p"

    def get_suffix(self):
        return '.' + self.mimeType.split('/')[0].split('-')[-1]