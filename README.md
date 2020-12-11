# mpd content parser

Parse mpd content as much as possible.

# requirements

> pip install argparse

# usage

```bash
usage: mpd content parser v1.2@xhlove [-h] [-p PATH] [-m {once,split}]

Mpd Content Parser, extract pssh and generate all tracks download links
easily. Report bug to vvtoolbox.dev@gmail.com

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  mpd file path.
  -m {once,split}, --mode {once,split}
                        generate links once time or split to write. Default is
                        once
```

# output

![example](/urls_output.png)