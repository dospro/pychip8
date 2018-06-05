from pychip8.cpu import Cpu
import sys

if __name__ == '__main__':
    print('Chip 8 emulator')
    cpu = Cpu()
    if len(sys.argv) < 2:
        print('USe a rom')
        sys.exit(0)

    cpu.load_rom(sys.argv[1])
    while True:
        cpu.loop_step()
