'''
作者: weimo
创建日期: 2020-09-14 13:13:18
上次编辑时间: 2021-01-01 18:08:57
一个人的命运啊,当然要靠自我奋斗,但是...
'''

from typing import Dict
from pathlib import Path
from argparse import ArgumentParser
from xml.parsers.expat import ParserCreate

# aria2c下载生成的txt命令示例 以及使用代理的示例
# aria2c -i urls.txt -d DownloadPath --https-proxy="http://127.0.0.1:10809" --http-proxy="http://127.0.0.1:10809"

from utils.mpd import MPD
from utils.links import Links
from utils.funcs import tree, find_child, dump, match_duration

from utils.childs.adaptationset import AdaptationSet
from utils.childs.baseurl import BaseURL
from utils.childs.cencpssh import CencPssh
from utils.childs.contentprotection import ContentProtection
from utils.childs.period import Period
from utils.childs.representation import Representation
from utils.childs.role import Role
from utils.childs.s import S
from utils.childs.segmenttemplate import SegmentTemplate
from utils.childs.segmenttimeline import SegmentTimeline


class MPDPaser(object):
    def __init__(self, basename: str, xmlraw: str, split: bool):
        self.step = 0
        self.basename = basename
        self.xmlraw = xmlraw
        self.split = split
        self.obj = None
        self.parser = None
        self.stack = list()
        self.tracks = {}  # type: Dict[str, Links]
        self.objs = {
            "MPD": MPD,
            "BaseURL": BaseURL,
            "Period": Period,
            "AdaptationSet": AdaptationSet,
            "Representation": Representation,
            "SegmentTemplate": SegmentTemplate,
            "SegmentTimeline": SegmentTimeline,
            "Role": Role,
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

    def parse(self, _baseurl: str):
        mediaPresentationDuration = self.obj.__dict__.get("mediaPresentationDuration")
        self.mediaPresentationDuration = match_duration(mediaPresentationDuration)
        if _baseurl == '':
            BaseURLs = find_child("BaseURL", self.obj)
            baseurl = None if len(BaseURLs) == 0 else BaseURLs[0].innertext
        else:
            baseurl = _baseurl
        Periods = find_child("Period", self.obj)
        for _Period in Periods:
            _Period: Period
            if isinstance(_Period.start, str):
                _Period.start = match_duration(_Period.duration)
            if isinstance(_Period.duration, str):
                _Period.duration = match_duration(_Period.duration)
            AdaptationSets = find_child("AdaptationSet", _Period)
            for _AdaptationSet in AdaptationSets:
                _AdaptationSet: AdaptationSet
                if baseurl is None:
                    BaseURLs = find_child("BaseURL", _AdaptationSet)
                    baseurl = None if len(BaseURLs) == 0 else BaseURLs[0].innertext
                Representations = find_child("Representation", _AdaptationSet)
                SegmentTemplates = find_child("SegmentTemplate", _AdaptationSet)
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
        return self.tracks

    def generate(self,
                 baseurl: str,
                 _Period: Period,
                 _AdaptationSet: AdaptationSet,
                 _Representation: Representation,
                 isInnerSeg: bool = True):
        _contentType = _AdaptationSet.get_contenttype()
        if _contentType is None:
            _contentType = _Representation.get_contenttype()
        if _contentType is None:
            _contentType = 'UNKONWN'
        if _AdaptationSet.codecs is not None:
            _codecs = _AdaptationSet.codecs
        elif _Representation.codecs is not None:
            _codecs = _Representation.codecs
        else:
            _Roles = find_child("Role", _AdaptationSet)
            _codecs = _Roles[0].value
        if isInnerSeg is True:
            key = f"{_AdaptationSet.id}-{_Representation.id}-{_contentType}"
        else:
            key = f"{_Representation.id}-{_contentType}"
        if self.split and _Period.id is not None:
            key = f"{_Period.id}-" + key
        if _Period.duration == 0.0 and self.mediaPresentationDuration is not None:
            _Period.duration = self.mediaPresentationDuration
        key = key.replace("/", "_")
        links = Links(self.basename, _Period.duration, key, _Representation.bandwidth, _codecs)
        if _AdaptationSet.lang is not None:
            links.lang = _AdaptationSet.lang
        if _AdaptationSet.mimeType is not None:
            links.suffix = _AdaptationSet.get_suffix()
        else:
            links.suffix = _Representation.get_suffix()
        if _Representation.width is not None:
            links.resolution = _Representation.get_resolution()
        elif _AdaptationSet.width is not None:
            links.resolution = _AdaptationSet.get_resolution()
        if isInnerSeg is True:
            SegmentTemplates = find_child("SegmentTemplate", _Representation)
        else:
            SegmentTemplates = find_child("SegmentTemplate", _AdaptationSet)
        for _SegmentTemplate in SegmentTemplates:
            _SegmentTemplate: SegmentTemplate
            start_number = int(_SegmentTemplate.startNumber)  # type: int
            if self.tracks.get(links.key) is None:
                _initialization = _SegmentTemplate.get_initialization()
                if "$RepresentationID$" in _initialization:
                    _initialization = _initialization.replace("$RepresentationID$", _Representation.id)
                if baseurl is not None:
                    _initialization = baseurl + _initialization
                links.urls.append(_initialization)
                self.tracks[links.key] = links
            else:
                if self.split is True:
                    self.tracks[links.key] = links
                else:
                    self.tracks[links.key].update(
                        _Period.duration, _Representation.bandwidth)
            SegmentTimelines = find_child("SegmentTimeline", _SegmentTemplate)
            urls = []
            if len(SegmentTimelines) == 0:
                interval_duration = float(int(_SegmentTemplate.duration) / int(_SegmentTemplate.timescale))
                if _SegmentTemplate.presentationTimeOffset is None:
                    _Segment_duration = _Period.duration
                else:
                    _Segment_duration = _Period.duration
                repeat = int(round(_Segment_duration / interval_duration))
                for number in range(start_number, repeat + start_number):
                    _media = _SegmentTemplate.get_media()
                    if "$Number$" in _media:
                        _media = _media.replace("$Number$", str(number))
                    if "$RepresentationID$" in _media:
                        _media = _media.replace("$RepresentationID$", _Representation.id)
                    _url = _media
                    if baseurl is not None:
                        _url = baseurl + _url
                    urls.append(_url)
            else:
                for _SegmentTimeline in SegmentTimelines:
                    _SegmentTimeline: SegmentTimeline
                    # repeat = 0
                    _last_time_offset = 0  # _Period.start
                    SS = find_child("S", _SegmentTimeline)
                    for _S in SS:
                        _S: S
                        repeat = 1 if _S.r is None else int(_S.r) + 1
                        for offset in range(repeat):
                            _media = _SegmentTemplate.get_media()
                            if "$Number$" in _media:
                                _media = _media.replace("$Number$", str(start_number))
                                start_number += 1
                            if "$RepresentationID$" in _media:
                                _media = _media.replace("$RepresentationID$", _Representation.id)
                            if "$Time$" in _media:
                                _media = _media.replace("$Time$", str(_last_time_offset))
                                _last_time_offset += int(_S.d)
                            _url = _media
                            if baseurl is not None:
                                _url = baseurl + _url
                            urls.append(_url)
            self.tracks[links.key].urls.extend(urls)
            if self.split is True:
                self.tracks[links.key].dump_urls()


def main():
    command = ArgumentParser(
        prog="mpd content parser v1.6@xhlove",
        description=("Mpd Content Parser, "
                     "generate all tracks download links easily. "
                     "Report bug to vvtoolbox.dev@gmail.com"))
    command.add_argument("-p", "--path", help="mpd file path.")
    command.add_argument("-s", "--split", action="store_true", help="generate links for each Period.")
    command.add_argument("-tree", "--tree", action="store_true", help="print mpd tree.")
    command.add_argument("-baseurl", "--baseurl", default="", help="set mpd base url.")
    args = command.parse_args()
    if args.path is None:
        args.path = input("paste mpd file path plz:\n")
    xmlpath = Path(args.path).resolve()
    if xmlpath.exists():
        xmlraw = xmlpath.read_text(encoding="utf-8")
        parser = MPDPaser(xmlpath.stem, xmlraw, args.split)
        parser.work()
        if args.tree:
            tree(parser.obj)
        tracks = parser.parse(args.baseurl)
        dump(tracks)
    else:
        print(f"{str(xmlpath)} is not exists!")


if __name__ == "__main__":
    main()