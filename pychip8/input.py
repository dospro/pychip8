import pygame


class Input:
    def __init__(self):
        self.exit_key_pressed = False
        self.pressed_keys = None
        self.key_mapping = {
            0: pygame.K_1,
            1: pygame.K_2,
            2: pygame.K_3,
            3: pygame.K_4,
            4: pygame.K_q,
            5: pygame.K_w,
            6: pygame.K_e,
            7: pygame.K_r,
            8: pygame.K_a,
            9: pygame.K_s,
            0xa: pygame.K_d,
            0xb: pygame.K_f,
            0xc: pygame.K_z,
            0xd: pygame.K_x,
            0xe: pygame.K_c,
            0xf: pygame.K_v,
        }

    def update(self):
        pygame.event.pump()
        self.pressed_keys = pygame.key.get_pressed()
        if self.pressed_keys[pygame.K_ESCAPE]:
            self.exit_key_pressed = True

    def is_key_pressed(self, key):
        return self.pressed_keys[self.key_mapping[key]]
