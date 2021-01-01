'''
作者: weimo
创建日期: 2021-01-01 16:44:36
上次编辑时间: 2021-01-01 16:45:16
一个人的命运啊,当然要靠自我奋斗,但是...
'''

import re
from pathlib import Path
from .maps.audiomap import AUDIOMAP


class Links(object):
    def __init__(self, *args):
        basename, duration, track_key, bandwidth, codecs = args
        self.basename: str = basename
        self.duration: float = duration
        self.track_key: str = track_key
        self.bandwidth: float = float(bandwidth)
        self.codecs: str = self.get_codecs(codecs)
        self.suffix: str = ".unkonwn"  # aria2c下载的文件名后缀
        self.lang: str = ""
        self.resolution: str = ""
        self.urls: list = []

    def get_codecs(self, codecs: str):
        # https://chromium.googlesource.com/chromium/src/media/+/master/base/mime_util_internal.cc
        if re.match("avc(1|3)*", codecs):
            return "H264"
        if re.match("(hev|hvc)1*", codecs):
            return "H265"
        if re.match("vp(09|9)*", codecs):
            return "VP9"
        if codecs in ["wvtt"]:
            return codecs.upper()
        if AUDIOMAP.get(codecs) is None:
            codecs = ""
        else:
            codecs = "AAC" if "AAC" in AUDIOMAP[codecs] else AUDIOMAP[codecs]
        return codecs

    def update(self, duration: float, bandwidth: str):
        _bandwidth = float(bandwidth)
        self.bandwidth = (duration * _bandwidth + self.duration * self.bandwidth) / (self.duration + duration)
        self.duration += duration

    def get_path(self) -> Path:
        filename = f"{self.basename}-{self.track_key}-{self.codecs}-{self.bandwidth/1000:.3f}kbps"
        if self.lang != "":
            filename += f".{self.lang}"
        if self.resolution != "":
            filename += f".{self.resolution}"
        print(filename)
        return Path(filename + ".txt").resolve()

    def dump_urls(self):
        filepath = self.get_path()
        filepath.write_text("\n".join(self.urls), encoding="utf-8")