'''
作者: weimo
创建日期: 2021-01-01 17:27:48
上次编辑时间: 2021-01-01 17:34:50
一个人的命运啊,当然要靠自我奋斗,但是...
'''

import re
from typing import Dict

from utils.links import Links


def tree(obj, step: int = 0):
    print(f"{step * '--'}>{obj.name}")
    step += 1
    for child in obj.childs:
        step = tree(child, step=step)
    step -= 1
    print(f"{step * '--'}>{obj.name}")
    return step


def find_child(name: str, parent):
    return [child for child in parent.childs if child.name == name]


def dump(tracks: Dict[str, Links]):
    for track_key, links in tracks.items():
        links.dump_urls()


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