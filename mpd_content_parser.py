'''
作者: weimo
创建日期: 2020-09-14 13:13:18
上次编辑时间: 2021-01-01 16:08:23
一个人的命运啊,当然要靠自我奋斗,但是...
'''

import re
import math
from typing import Dict
from pathlib import Path
from argparse import ArgumentParser
from xml.parsers.expat import ParserCreate

# aria2c下载生成的txt命令示例 以及使用代理的示例
# aria2c -i urls.txt -d DownloadPath --https-proxy="http://127.0.0.1:10809" --http-proxy="http://127.0.0.1:10809"

from utils.mpd import MPD
from utils.maps.audiomap import AUDIOMAP

from utils.childs.adaptationset import AdaptationSet
from utils.childs.baseurl import BaseURL
from utils.childs.cencpssh import CencPssh
from utils.childs.contentprotection import ContentProtection
from utils.childs.period import Period
from utils.childs.representation import Representation
# from utils.childs.role import Role
from utils.childs.s import S
from utils.childs.segmenttemplate import SegmentTemplate
from utils.childs.segmenttimeline import SegmentTimeline


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


class MPDPaser(object):
    def __init__(self, basename: str, xmlraw: str, split: bool):
        self.step = 0
        self.basename = basename
        self.xmlraw = xmlraw
        self.split = split
        self.obj = None
        self.parser = None
        self.stack = list()
        self.ar_idid = {}  # type: Dict[str, Links]
        self.objs = {
            "MPD": MPD,
            "BaseURL": BaseURL,
            "Period": Period,
            "AdaptationSet": AdaptationSet,
            "Representation": Representation,
            "SegmentTemplate": SegmentTemplate,
            "SegmentTimeline": SegmentTimeline,
            "S": S,
            "ContentProtection": ContentProtection,
            "cenc:pssh": CencPssh,
        }

    def work(self):
        self.parser = ParserCreate()
        self.parser.StartElementHandler = self.handle_start_element
        self.parser.EndElementHandler = self.handle_end_element
        self.parser.CharacterDataHandler = self.handle_character_data
        self.parser.Parse(self.xmlraw)

    def handle_start_element(self, tag, attrs):
        if self.obj is None:
            if tag != "MPD":
                raise Exception("the first tag is not MPD!")
            self.obj: MPD = MPD(tag)
            self.obj.addattrs(attrs)
            self.stack.append(self.obj)
        else:
            if self.objs.get(tag) is None:
                return
            child = self.objs[tag](tag)
            child.addattrs(attrs)
            self.obj.childs.append(child)
            self.obj = child
            self.stack.append(child)

    def handle_end_element(self, tag):
        if self.objs.get(tag) is None:
            return
        if len(self.stack) > 1:
            _ = self.stack.pop(-1)
            self.obj = self.stack[-1]

    def handle_character_data(self, texts):
        if texts.strip() != "":
            self.obj.innertext = texts

    @staticmethod
    def find_child(name: str, parent):
        return [child for child in parent.childs if child.name == name]

    def tree(self, obj):
        print(f"{self.step * '--'}>{obj.name}")
        self.step += 1
        for child in obj.childs:
            self.tree(child)
        self.step -= 1
        print(f"{self.step * '--'}>{obj.name}")

    def match_duration(self, _duration):
        if isinstance(_duration, str) is False:
            return

        duration = re.match(r"PT(\d+)(\.?\d+)S", _duration)
        if duration is not None:
            return float(duration.group(1)) if duration else 0.0
        # P0Y0M0DT0H3M30.000S
        duration = re.match(r"PT(\d+)H(\d+)M(\d+)(\.?\d+)S",
                            _duration.replace('0Y0M0D', ''))
        if duration is not None:
            _h, _m, _s, _ss = duration.groups()
            return int(_h) * 60 * 60 + int(_m) * 60 + int(_s) + float("0" + _ss)

    def parse(self, _baseurl: str):
        mediaPresentationDuration = self.obj.__dict__.get(
            "mediaPresentationDuration")
        self.mediaPresentationDuration = self.match_duration(
            mediaPresentationDuration)
        if _baseurl == '':
            BaseURLs = self.find_child("BaseURL", self.obj)
            baseurl = None if len(BaseURLs) == 0 else BaseURLs[0].innertext
        else:
            baseurl = _baseurl
        Periods = self.find_child("Period", self.obj)
        for _Period in Periods:
            _Period: Period
            if isinstance(_Period.start, str):
                _Period.start = self.match_duration(_Period.duration)
            if isinstance(_Period.duration, str):
                _Period.duration = self.match_duration(_Period.duration)
            AdaptationSets = self.find_child("AdaptationSet", _Period)
            for _AdaptationSet in AdaptationSets:
                _AdaptationSet: AdaptationSet
                if baseurl is None:
                    BaseURLs = self.find_child("BaseURL", _AdaptationSet)
                    baseurl = None if len(
                        BaseURLs) == 0 else BaseURLs[0].innertext
                Representations = self.find_child("Representation",
                                                  _AdaptationSet)
                SegmentTemplates = self.find_child("SegmentTemplate",
                                                   _AdaptationSet)
                for _Representation in Representations:
                    _Representation: Representation
                    if len(SegmentTemplates) == 0:
                        self.generate(baseurl, _Period, _AdaptationSet, _Representation)
                    else:
                        # SegmentTemplate和Representation同一级的话，解析不一样
                        self.generate(baseurl,
                                      _Period,
                                      _AdaptationSet,
                                      _Representation,
                                      isInnerSeg=False)
        for track_key, links in self.ar_idid.items():
            links: Links
            links.dump_urls()

    def generate(self,
                 baseurl: str,
                 _Period: Period,
                 _AdaptationSet: AdaptationSet,
                 _Representation: Representation,
                 isInnerSeg: bool = True):
        if _AdaptationSet.contentType is not None:
            _contentType = _AdaptationSet.contentType
        elif _AdaptationSet.mimeType is not None:
            _contentType = _AdaptationSet.mimeType.split('/')[0].title()
        elif _Representation.mimeType is not None:
            _contentType = _Representation.mimeType.split('/')[0].title()
        else:
            _contentType = 'UNKONWN'
        if _AdaptationSet.codecs is not None:
            _codecs = _AdaptationSet.codecs
        else:
            _codecs = _Representation.codecs
        if isInnerSeg is True:
            track_key = f"{_AdaptationSet.id}-{_Representation.id}-{_contentType}"
        else:
            track_key = f"{_Representation.id}-{_contentType}"
        if self.split and _Period.id is not None:
            track_key = f"{_Period.id}-" + track_key
        if _Period.duration == 0.0 and self.mediaPresentationDuration is not None:
            _Period.duration = self.mediaPresentationDuration
        track_key = track_key.replace("/", "_")
        links = Links(self.basename, _Period.duration, track_key,
                      _Representation.bandwidth, _codecs)
        if _AdaptationSet.lang is not None:
            links.lang = _AdaptationSet.lang
        if _AdaptationSet.mimeType is not None:
            links.suffix = "." + _AdaptationSet.mimeType.split("/")[0].split(
                "-")[-1]
        else:
            links.suffix = "." + _Representation.mimeType.split("/")[0].split(
                "-")[-1]
            if _Representation.mimeType == "video/mp4":
                if _Representation.width is not None:
                    links.resolution = f"{_Representation.width}x{_Representation.height}p"
        if isInnerSeg is True:
            SegmentTemplates = MPDPaser.find_child("SegmentTemplate",
                                                   _Representation)
        else:
            SegmentTemplates = MPDPaser.find_child("SegmentTemplate",
                                                   _AdaptationSet)
        for _SegmentTemplate in SegmentTemplates:
            _SegmentTemplate: SegmentTemplate
            start_number = int(_SegmentTemplate.startNumber)  # type: int
            if self.ar_idid.get(links.track_key) is None:
                _initialization = _SegmentTemplate.initialization.replace(
                    '..', '')
                if "$RepresentationID$" in _initialization:
                    _initialization = _initialization.replace(
                        "$RepresentationID$", _Representation.id)
                if baseurl is not None:
                    _initialization = baseurl + _initialization
                links.urls.append(_initialization)
                self.ar_idid[links.track_key] = links
            else:
                if self.split is True:
                    self.ar_idid[links.track_key] = links
                else:
                    self.ar_idid[links.track_key].update(
                        _Period.duration, _Representation.bandwidth)
            SegmentTimelines = MPDPaser.find_child("SegmentTimeline",
                                                   _SegmentTemplate)
            urls = []
            if len(SegmentTimelines) == 0:
                interval_duration = float(int(_SegmentTemplate.duration) / int(_SegmentTemplate.timescale))
                if _SegmentTemplate.presentationTimeOffset is None:
                    _Segment_duration = _Period.duration
                else:
                    _Segment_duration = _Period.duration
                repeat = int(math.ceil(_Segment_duration / interval_duration))
                for number in range(start_number, repeat + start_number):
                    _media = _SegmentTemplate.media.replace('..',
                                                            '')  # type: str
                    if "$Number$" in _media:
                        _media = _media.replace("$Number$", str(number))
                    if "$RepresentationID$" in _media:
                        _media = _media.replace("$RepresentationID$",
                                                _Representation.id)
                    _url = _media
                    if baseurl is not None:
                        _url = baseurl + _url
                    urls.append(_url)
            else:
                for _SegmentTimeline in SegmentTimelines:
                    _SegmentTimeline: SegmentTimeline
                    # repeat = 0
                    _last_time_offset = 0  # _Period.start
                    SS = MPDPaser.find_child("S", _SegmentTimeline)
                    for _S in SS:
                        _S: S
                        repeat = 1 if _S.r is None else int(_S.r) + 1
                        for offset in range(repeat):
                            _media = _SegmentTemplate.replace('..',
                                                              '')  # type: str
                            if "$Number$" in _media:
                                _media = _media.replace(
                                    "$Number$", str(start_number))
                                start_number += 1
                            if "$RepresentationID$" in _media:
                                _media = _media.replace(
                                    "$RepresentationID$", _Representation.id)
                            if "$Time$" in _media:
                                _media = _media.replace(
                                    "$Time$", str(_last_time_offset))
                                _last_time_offset += int(_S.d)
                            _url = _media
                            if baseurl is not None:
                                _url = baseurl + _url
                            urls.append(_url)
            self.ar_idid[links.track_key].urls.extend(urls)
            if self.split is True:
                self.ar_idid[links.track_key].dump_urls()

    @staticmethod
    def show_AdaptationSet(obj: AdaptationSet):
        attrs = []
        for attr_name, attr_value in obj.__dict__.items():
            if attr_name == "childs":
                continue
            if attr_value is None:
                continue
            attrs += [f"{attr_value}"]
        # print(" ".join(attrs))


def main():
    command = ArgumentParser(
        prog="mpd content parser v1.5@xhlove",
        description=("Mpd Content Parser, "
                     "generate all tracks download links easily. "
                     "Report bug to vvtoolbox.dev@gmail.com"))
    command.add_argument("-p", "--path", help="mpd file path.")
    command.add_argument("-s",
                         "--split",
                         action="store_true",
                         help="generate links for each Period.")
    command.add_argument("-baseurl",
                         "--baseurl",
                         default="",
                         help="set mpd base url.")
    args = command.parse_args()
    if args.path is None:
        args.path = input("paste mpd file path plz:\n")
    xmlpath = Path(args.path).resolve()
    if xmlpath.exists():
        xmlraw = xmlpath.read_text(encoding="utf-8")
        parser = MPDPaser(xmlpath.stem, xmlraw, args.split)
        parser.work()
        # parser.tree(parser.obj)
        parser.parse(args.baseurl)
    else:
        print(f"{str(xmlpath)} is not exists!")


if __name__ == "__main__":
    main()