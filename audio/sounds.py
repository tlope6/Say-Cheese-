import pygame

class Sounds :
    def __init__(self, music_path : str) :
        pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.0)
        self.playing = False


    def fade_in(self) :
        if not self.playing :
            pygame.mixer.music.play(-1)
            pygame.mixer.music.fadeout(0)
            pygame.mixer.music.set_volume(0.6)
            self.playing  = True

    def fade_out(self) :
        if self.playing:
            pygame.mixer.music.fadeout(1500)
            self.playing = False
