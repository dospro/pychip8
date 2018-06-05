import array


class Memory:
    def __init__(self):
        self.memory = array.array('B', [0] * 0x200)

    def load_rom(self, rom_filename):
        with open(rom_filename, 'rb') as rom_file:
            rom_file.seek(0, 2)
            size = rom_file.tell()
            rom_file.seek(0, 0)
            self.memory.fromfile(rom_file, size)
            missing_size = 0xFFF - 0x200 - size
            self.memory = self.memory + array.array('B', [0] * missing_size)

    def read_byte(self, address):
        return self.memory[address]

    def write_byte(self, address, value):
        self.memory[address] = value

    def read_word(self, address):
        """Returns a 16 bit big-endian word from memory"""
        return (self.memory[address] << 8) | self.memory[address + 1]

    def write_word(self, address, value):
        """Write 16 bit big endian word into memory"""
        self.memory[address] = (value >> 8) & 0xFF
        self.memory[address + 1] = value & 0xFF
