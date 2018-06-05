import pygame


class VideoBuffer:
    def __init__(self):
        self.video_buffer = [0] * 64 * 32

    def paint_byte_line(self, x_coord, y_coord, byte_line):
        x = x_coord % 64
        y = y_coord % 32
        buffer_index = (64 * y) + x
        collision = False
        for i in range(8):
            if buffer_index + i > 0x7FF:
                continue
            bit_pixel = (byte_line >> (7 - i)) & 1
            if self.video_buffer[buffer_index + i] == 0 and bit_pixel == 1:
                collision = True
            self.video_buffer[buffer_index + i] = bit_pixel

        return collision

    def clear_buffer(self):
        for i in range(len(self.video_buffer)):
            self.video_buffer[i] = 0


class PyGameDisplay(VideoBuffer):
    def __init__(self):
        super().__init__()
        pygame.init()
        self.screen = pygame.display.set_mode((640, 320))

    def paint_screen(self):
        for x_coord in range(64):
            for y_coord in range(32):
                r = pygame.Rect(x_coord * 10, y_coord * 10, 10, 10)
                if self.video_buffer[64 * y_coord + x_coord] == 1:
                    self.screen.fill(0xFFFFFF, r)
                else:
                    self.screen.fill(0, r)

        pygame.display.flip()
