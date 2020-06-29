# one_fmt
The goal of this tools is to build payload for format string vulnerability, as fmt_str module from pwntools on 64-bits machines is shitty.

+ Supports only python2 for now, as python3 for pwning is awful
+ Supports only 64-bits for now, as I personally rarely encounter 32-bits scenarios nowadays

Feel free to add supports and pull requests are welcomed.

Some code of this module is from [Inndy/formatstring-exploit](https://github.com/Inndy/formatstring-exploit). It's better than pwntools, but still it used a a lot of paddings to generalize payloads therefore sometimes not so pleasing.

The payload has 3 levels: `%n %hn %hhn`. In version 1.1.0(2974bc4), I added an optimize() function to further reduce payload size. This should be the final version of functions for a while. Enjoy!

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

Another test program `test2` is for me to test cases as well.

test3 folder is for me to test optimize function, and it worked on my machine XD

## Changelog

1.0.0: First version

1.0.1: Update Pypi project url

1.0.2: Fix typo in setup.py

1.0.3: Fix endianness; Fix %n index bug

1.1.0: Add optimization function; Fix bug

## TODO

+ ~~Add a level of automatically generate an shorter payload on low levels~~
  + ~~For example, if you use level 0 to generate`fmt[0x601050] = p64(0x4142)`, the payload will write to 8 addresses. However, this can be trimmed by write a `%n` to `0x601054` and a `%hn` to `0x601052`.~~
+ Supports Python3 and 32 bits? Will do when I have the need.
+ ~~ADD COMMENTS TO THE ULGY CODE~~

