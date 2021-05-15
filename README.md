# mpd content parser

Parse mpd content as much as possible.

# requirements

> pip install argparse
> pip install requests

# usage

```bash
usage: mpd content parser v1.7@xhlove [-h] [-p PATH] [-s] [-tree]
                                      [-baseurl BASEURL] [-url URL] [-o OUT]

Mpd Content Parser, generate all tracks download links easily. Report bug to
vvtoolbox.dev@gmail.com

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  mpd file path.
  -s, --split           generate links for each Period.
  -tree, --tree         print mpd tree.
  -baseurl BASEURL, --baseurl BASEURL
                        set mpd base url.
  -url URL, --url URL   url to fetch link from
  -o OUT, --out OUT     output directory to store all text files
```

# output

![example](output/urls_output.png)