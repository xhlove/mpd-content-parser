'''
作者: weimo
创建日期: 2021-01-01 15:11:10
上次编辑时间: 2021-01-01 15:11:27
一个人的命运啊,当然要靠自我奋斗,但是...
'''

from ..mpditem import MPDItem


class SegmentTimeline(MPDItem):
    # 5.3.9.6 Segment timeline
    def __init__(self, name: str):
        super(SegmentTimeline, self).__init__(name)