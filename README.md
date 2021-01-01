# mpd content parser

Parse mpd content as much as possible.

# requirements

> pip install argparse

# usage

```bash
usage: mpd content parser v1.5@xhlove [-h] [-p PATH] [-s] [-baseurl BASEURL]

Mpd Content Parser, generate all tracks download links easily. Report bug to
vvtoolbox.dev@gmail.com

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  mpd file path.
  -s, --split           generate links for each Period.
  -baseurl BASEURL, --baseurl BASEURL
                        set mpd base url.
```

# output

![example](/urls_output.png)