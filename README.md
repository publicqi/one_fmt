# one_fmt
The goal of this tools is to build payload for format string vulnerability, as fmt_str module from pwntools on 64-bits machines is shitty.

+ Supports only python2 for now, as python3 for pwning is awful
+ Supports only 64-bits for now, as I personally rarely encounter 32-bits scenarios nowadays

Feel free to add supports and pull requests are welcomed.

Some code of this module is from [Inndy/formatstring-exploit](https://github.com/Inndy/formatstring-exploit). It's better than pwntools, but still it used a a lot of paddings to generalize payloads therefore sometimes not so pleasing.

The payload has 3 levels: `%n %hn %hhn`

## Installation

```sh
pip install one_fmt
```

Or

```sh
git clone https://github.com/publicqi/one_fmt.git
cd one_fmt
python2 setup.py install
```

## Usage

```python
from one_fmt import *
fmt = Fmt(offset=24, written=8)
fmt[0x601040] = "DEADBEEF"
fmt[0x601050] = 0x1337babe
payload_level_hhn = fmt.build(0)
payload_level_hn = fmt.build(1)
payload_level_n = fmt.build(2)
```

The payload has 3 levels: `%n %hn %hhn`. For some cases when dealing with a CTF challenge which limits your input length, you'd better to use a higher level with shorter payload but may takes longer time.

## Test case

You can find a test program in test folder and test1.py. The challenge is written by [@lockshaw](https://github.com/lockshaw). There're a few cases that the address contains `\x0a` therefore SIGSEV. And the challenge doesn't really need arbitrary write as lots addresses are there on the stack. It's just for demoing.
