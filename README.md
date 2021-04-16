# mpd content parser

Parse mpd content as much as possible.

# requirements

> pip install argparse
> pip install requests

# usage

```bash
usage: mpd content parser v1.6@xhlove [-h] [-p PATH] [-s] [-baseurl BASEURL]

Mpd Content Parser, generate all tracks download links easily. Report bug to
vvtoolbox.dev@gmail.com

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  mpd file path.
  -s, --split           generate links for each Period.
  -baseurl BASEURL, --baseurl BASEURL
                        set mpd base url.
  -url url, --url url 
                      set url to get chunk from
  -o path --out path
                      set output directory for all txt files
```

# output

![example](output/urls_output.png)