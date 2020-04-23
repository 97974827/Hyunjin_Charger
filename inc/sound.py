import pygame
import time


class Sound:
    sound = ""
    pygame.mixer.init(44100)
    file_sound = ""

    def playSound(self, file_sound):
        self.sound = pygame.mixer.Sound(file_sound)
        self.sound.play()

        # time.sleep(4)
        # self.stopSound()

        # pygame.mixer.music.load("../msgs/msg001.wav")
        # clock = pygame.time.Clock()
        # while pygame.mixer.music.get_busy():
        #     clock.tick(30)
        # pygame.mixer.music.load("../msgs/msg002.wav")
        # pygame.mixer.music.play()
        # clock = pygame.time.Clock()
        # while pygame.mixer.music.get_busy():
        #     clock.tick(30)
        # pygame.mixer.quit()

    def stopSound(self):
        self.sound.stop()

    def getBusySound(self):
        return pygame.mixer.get_busy()


# TODO : Sound Test Code
if __name__ == '__main__':
    pass
    # app = Sound()
    # app.playSound("../msgs/msg001.wav")
    # app.playSound("../msgs/msg002.wav")