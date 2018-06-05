from pychip8 import display
from pychip8.memory import Memory


class UnkownOpcodeError(Exception):
    pass


class Opcode:
    def __init__(self, opcode_string, opcodes_list):
        self.opcode_string = opcode_string
        self.opcodes_list = opcodes_list

    def __call__(self, *args, **kwargs):
        func = args[0]
        self.opcodes_list[self.opcode_string] = func

        def decorated_function(values):
            return func(values)

        return decorated_function


class Cpu:

    def __init__(self):
        self.opcodes = {}

        self.memory = Memory()
        self.display = display.PyGameDisplay()

        self.v_registers = [0] * 16
        self.stack = [0] * 16
        self.pc_register = 0x200
        self.sp_register = 0
        self.i_register = 0

        self.delay_timer = 0
        self.sound_timer = 0
        self.init_opcodes()

    def load_rom(self, rom_filename):
        self.memory.load_rom(rom_filename)

    def loop_step(self):
        self.run_opcode()
        if self.sound_timer != 0:
            self.sound_timer -= 1
        if self.delay_timer != 0:
            self.delay_timer -= 1

        self.display.paint_screen()

    def run_opcode(self):
        opcode = self.memory.read_word(self.pc_register)
        self.pc_register += 2
        decoded = self.decode_opcode(opcode)
        # print('{} - {}'.format(hex(opcode), decoded['opcode_string']))
        self.opcodes[decoded['opcode_string']](decoded)
        # print('i -> {}'.format(self.i_register))
        # print('v0 -> {}'.format(self.v_registers[0]))

    def decode_opcode(self, opcode):
        nibbles = [
            (opcode >> 12) & 0xF,
            (opcode >> 8) & 0xF,
            (opcode >> 4) & 0xF,
            opcode & 0xF
        ]
        if opcode == 0x00E0:
            return {'opcode_string': '00e0'}
        elif opcode == 0x00EE:
            return {'opcode_string': '00ee'}
        elif nibbles[0] == 1:
            return {
                'opcode_string': '1nnn',
                'n': opcode & 0xFFF
            }
        elif nibbles[0] == 2:
            return {
                'opcode_string': '2nnn',
                'n': opcode & 0xFFF
            }
        elif nibbles[0] == 3:
            return {
                'opcode_string': '3xyy',
                'x': nibbles[1],
                'y': (nibbles[2] << 4) | nibbles[3]
            }
        elif nibbles[0] == 4:
            return {
                'opcode_string': '4xyy',
                'x': nibbles[1],
                'y': (nibbles[2] << 4) | nibbles[3]
            }
        elif nibbles[0] == 5:
            return {
                'opcode_string': '5xy0',
                'x': nibbles[1],
                'y': nibbles[2]
            }
        elif nibbles[0] == 6:
            return {
                'opcode_string': '6xyy',
                'x': nibbles[1],
                'y': (nibbles[2] << 4) | nibbles[3]
            }
        elif nibbles[0] == 7:
            return {
                'opcode_string': '7xyy',
                'x': nibbles[1],
                'y': (nibbles[2] << 4) | nibbles[3]
            }
        elif nibbles[0] == 8:
            return {
                'opcode_string': '8xy{}'.format(format(nibbles[3], '1x')),
                'x': nibbles[1],
                'y': nibbles[2]
            }
        elif nibbles[0] == 9:
            return {
                'opcode_string': '9xy0',
                'x': nibbles[1],
                'y': nibbles[2]
            }
        elif nibbles[0] == 0xA:
            return {
                'opcode_string': 'annn',
                'n': opcode & 0xFFF
            }
        elif nibbles[0] == 0xB:
            return {
                'opcode_string': 'bnnn',
                'x': opcode & 0xFFF
            }
        elif nibbles[0] == 0xC:
            return {
                'opcode_string': 'cxyy',
                'x': nibbles[1],
                'y': opcode & 0xFF
            }
        elif nibbles[0] == 0xD:
            return {
                'opcode_string': 'dxyn',
                'x': nibbles[1],
                'y': nibbles[2],
                'n': nibbles[3]
            }
        elif nibbles[0] == 0xE:
            return {
                'opcode_string': 'exa1',
                'x': nibbles[1]
            }
        elif nibbles[0] == 0xF:
            return {
                'opcode_string': 'fx{}'.format(format(opcode & 0xFF, '02x')),
                'x': nibbles[1]
            }
        else:
            raise UnkownOpcodeError('Unknown opcode {}'.format(hex(opcode)))

    def register_opcode(self, opcode_string):
        return Opcode(opcode_string, self.opcodes)

    def init_opcodes(self):
        @self.register_opcode('00e0')
        def _(values):
            """Clear display"""
            self.display.clear_buffer()

        @self.register_opcode('00ee')
        def _(values):
            """Return from a subroutine"""
            self.pc_register = self.stack[self.sp_register]
            self.sp_register -= 1

        @self.register_opcode('1nnn')
        def _(values):
            """Jump to location nnn"""
            self.pc_register = values['n']

        @self.register_opcode('2nnn')
        def _(values):
            """Call subroutine at nnn"""
            self.sp_register += 1
            self.stack[self.sp_register] = self.pc_register
            self.pc_register = values['n']

        @self.register_opcode('3xyy')
        def _(values):
            """Skip next instruction if Vx == yy"""
            if self.v_registers[values['x']] == values['y']:
                self.pc_register += 2

        @self.register_opcode('4xyy')
        def _(values):
            """Skip next instruction if Vx != yy"""
            if self.v_registers[values['x']] != values['y']:
                self.pc_register += 2

        @self.register_opcode('5xy0')
        def _(values):
            """Skip next instruction if Vx == Vy"""
            vx = self.v_registers[values['x']]
            vy = self.v_registers[values['y']]
            if vx == vy:
                self.pc_register += 2

        @self.register_opcode('6xyy')
        def _(values):
            """Set Vx = yy"""
            self.v_registers[values['x']] = values['y']

        @self.register_opcode('7xyy')
        def _(values):
            """Set Vx = Vx + yy"""
            vx = self.v_registers[values['x']]
            self.v_registers[values['x']] = (vx + values['y']) & 0xFF

        @self.register_opcode('8xy0')
        def _(values):
            """Set Vx = Vy"""
            vy = self.v_registers[values['y']]
            self.v_registers[values['x']] = vy

        @self.register_opcode('8xy1')
        def _(values):
            """Set Vx = Vx or Vy"""
            vy = self.v_registers[values['y']]
            self.v_registers[values['x']] |= vy

        @self.register_opcode('8xy2')
        def _(values):
            """Set Vx = Vx and Vy"""
            vy = self.v_registers[values['y']]
            self.v_registers[values['x']] &= vy

        @self.register_opcode('8xy3')
        def _(values):
            """Set Vx = Vx xor Vy"""
            vy = self.v_registers[values['y']]
            self.v_registers[values['x']] ^= vy

        @self.register_opcode('8xy4')
        def _(values):
            """Set Vx = Vx + Vy, VF = carry"""
            vx = self.v_registers[values['x']]
            vy = self.v_registers[values['y']]
            if vx + vy > 0xFF:
                self.v_registers[0xf] = 1
            else:
                self.v_registers[0xf] = 0
            self.v_registers[values['x']] = (vx + vy) & 0xFF

        @self.register_opcode('8xy5')
        def _(values):
            """Set Vx = Vx - Vy, VF = not borrow"""
            vx = self.v_registers[values['x']]
            vy = self.v_registers[values['y']]
            if vx > vy:
                self.v_registers[0xf] = 1
            else:
                self.v_registers[0xf] = 0
            self.v_registers[values['x']] = (vx - vy) & 0xFF

        @self.register_opcode('8xy6')
        def _(values):
            """Set Vx = Vx >> 1, VF = LSB"""
            vy = self.v_registers[values['y']]

            self.v_registers[0xf] = vy & 1

            self.v_registers[values['x']] = vy >> 1

        @self.register_opcode('8xy7')
        def _(values):
            """Set Vx = Vy - Vx, VF = not borrow"""
            vx = self.v_registers[values['x']]
            vy = self.v_registers[values['y']]
            if vy > vx:
                self.v_registers[0xf] = 1
            else:
                self.v_registers[0xf] = 0
            self.v_registers[values['x']] = (vy - vx) & 0xFF

        @self.register_opcode('8xye')
        def _(values):
            """Set Vx = Vx << 1"""
            vy = self.v_registers[values['y']]
            self.v_registers[0xf] = (vy >> 7) & 1
            self.v_registers[values['x']] = vy >> 1

        @self.register_opcode('9xy0')
        def _(values):
            """Skip the next instruction if Vx != Vy"""
            vx = self.v_registers[values['x']]
            vy = self.v_registers[values['y']]
            if vx != vy:
                self.pc_register += 2

        @self.register_opcode('annn')
        def _(values):
            """Set I = nnn"""
            self.i_register = values['n']

        @self.register_opcode('bnnn')
        def _(values):
            """Jump to location nnn + v0"""
            self.pc_register = self.v_registers[0] + values['n']

        @self.register_opcode('cxyy')
        def _(values):
            """Set Vx = random byte and yy"""

            self.v_registers[values['x']] = ((self.pc_register ^ self.sp_register) & values['y']) & 0xFF

        @self.register_opcode('dxyn')
        def _(values):
            """Paint sprite from I into (Vx, Vy)"""
            self.v_registers[0xF] = 0
            vx = self.v_registers[values['x']]
            vy = self.v_registers[values['y']]
            height = 16 if values['n'] == 0 else values['n']
            for i in range(height):
                byte_line = self.memory.read_byte(self.i_register + i)
                if self.display.paint_byte_line(vx, vy + i, byte_line):
                    self.v_registers[0xF] = 1

        @self.register_opcode('ex9e')
        def _(values):
            """Skip next instruction if key with the value Vx is pressed"""
            # TODO
            pass

        @self.register_opcode('exa1')
        def _(values):
            """Skip next instruction if key with value Vx is not pressed"""
            # TODO
            self.pc_register += 2
            pass

        @self.register_opcode('fx07')
        def _(values):
            """Set Vx = delay timer value"""
            self.v_registers[values['x']] = self.delay_timer

        @self.register_opcode('fx0a')
        def _(values):
            """Wait for a key press and store it on Vx"""
            # TODO
            pass

        @self.register_opcode('fx15')
        def _(values):
            """Set delay timer = Vx"""
            self.delay_timer = self.v_registers[values['x']]

        @self.register_opcode('fx18')
        def _(values):
            """Set sound timer = Vx"""
            self.sound_timer = self.v_registers[values['x']]

        @self.register_opcode('fx1e')
        def _(values):
            """Set I = I + Vx"""
            vx = self.v_registers[values['x']]
            self.i_register = (self.i_register + vx) & 0xFFFF

        @self.register_opcode('fx29')
        def _(values):
            """Set I = location of sprite for digit Vx"""
            # TODO
            self.i_register = 0
            pass

        @self.register_opcode('fx33')
        def _(values):
            """Store BCD representation of Vx in memory locations I"""
            vx = self.v_registers[values['x']]
            self.memory.write_byte(self.i_register, vx // 100)
            self.memory.write_byte(self.i_register + 1, (vx // 10) % 10)
            self.memory.write_byte(self.i_register + 2, (vx // 10) % 10)

        @self.register_opcode('fx55')
        def _(values):
            """Store registers V0 through Vx in memory address I"""
            for i in range(values['x']):
                self.memory.write_byte(self.i_register + i, self.v_registers[i])

        @self.register_opcode('fx65')
        def _(values):
            """Read registers V0 through x from memory address I"""
            for i in range(values['x']):
                self.v_registers[i] = self.memory.read_byte(self.i_register + i)

        pass
