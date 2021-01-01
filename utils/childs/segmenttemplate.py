'''
作者: weimo
创建日期: 2021-01-01 15:11:10
上次编辑时间: 2021-01-01 17:10:04
一个人的命运啊,当然要靠自我奋斗,但是...
'''

from ..mpditem import MPDItem


class SegmentTemplate(MPDItem):
    def __init__(self, name: str):
        super(SegmentTemplate, self).__init__(name)
        # SegmentTemplate没有duration的话 timescale好像没什么用
        self.timescale = None
        self.duration = None
        self.presentationTimeOffset = None
        self.initialization = None # type: str
        self.media = None # type: str
        self.startNumber = 1

    def get_initialization(self) -> str:
        return self.initialization.replace('..', '')

    def get_media(self) -> str:
        return self.media.replace('..', '')

# '''
# The SegmentTimeline element shall contain a list of S elements each of which describes a sequence
# of contiguous segments of identical MPD duration. The S element contains a mandatory @d attribute
# specifying the MPD duration, an optional @r repeat count attribute specifying the number of contiguous
# Segments with identical MPD duration minus one and an optional @t time attribute. The value of the @t
# attribute minus the value of the @presentationTimeOffset specifies the MPD start time of the first
# Segment in the series.
# The @r attribute has a default value of zero (i.e., a single Segment in the series) when not present. For
# example, a repeat count of three means there are four contiguous Segments, each with the same MPD
# duration. The value of the @r attribute of the S element may be set to a negative value indicating that the
# duration indicated in @d repeats until the S@t of the next S element or if it is the last S element in the
# SegmentTimeline element until the end of the Period or the next update of the MPD, i.e. it is treated
# in the same way as the @duration attribute for a full period.
# '''