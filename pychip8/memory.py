import array


class Memory:
    def __init__(self):
        self.memory = array.array('B', [0] * 0x200)
        self.memory[0:5] = array.array('B', [0xF0, 0x90, 0x90, 0x90, 0xF0])  # 0
        self.memory[5:10] = array.array('B', [0x20, 0x60, 0x20, 0x20, 0x70])  # 1
        self.memory[10:15] = array.array('B', [0xF0, 0x10, 0xF0, 0x80, 0xF0])  # 2
        self.memory[15:20] = array.array('B', [0xF0, 0x10, 0xF0, 0x10, 0xF0])  # 3
        self.memory[20:25] = array.array('B', [0x90, 0x90, 0xF0, 0x10, 0x10])  # 4
        self.memory[25:30] = array.array('B', [0xF0, 0x80, 0xF0, 0x10, 0xF0])  # 5
        self.memory[30:35] = array.array('B', [0xF0, 0x80, 0xF0, 0x90, 0xF0])  # 6
        self.memory[35:40] = array.array('B', [0xF0, 0x10, 0x20, 0x40, 0x40])  # 7
        self.memory[40:45] = array.array('B', [0xF0, 0x90, 0xF0, 0x90, 0xF0])  # 8
        self.memory[45:50] = array.array('B', [0xF0, 0x90, 0xF0, 0x10, 0xF0])  # 9
        self.memory[50:55] = array.array('B', [0xF0, 0x90, 0xF0, 0x90, 0x90])  # A
        self.memory[55:60] = array.array('B', [0xE0, 0x90, 0xE0, 0x90, 0xE0])  # B
        self.memory[60:65] = array.array('B', [0xF0, 0x80, 0x80, 0x80, 0xF0])  # C
        self.memory[65:70] = array.array('B', [0xE0, 0x90, 0x90, 0x90, 0xE0])  # D
        self.memory[70:75] = array.array('B', [0xF0, 0x80, 0xF0, 0x80, 0xF0])  # E
        self.memory[75:80] = array.array('B', [0xF0, 0x80, 0xF0, 0x80, 0x80])  # F

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
