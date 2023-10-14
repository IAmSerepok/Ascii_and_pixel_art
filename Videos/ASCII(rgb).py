import pygame as pg
from numba import njit
import numpy as np
from ffpyplayer.player import MediaPlayer
import cv2
import os


main_folder = os.path.dirname(__file__)
video_folder = os.path.join(main_folder, "input")
save_folder = os.path.join(main_folder, "output")


@njit(fastmath=True)
def accelerated_conversion(image, gray_image, width, height, ascii_step, color_step, char_step):
    array_of_values = []
    for x in range(0, width, char_step):
        for y in range(0, height, char_step):
            char_index = gray_image[x, y] // ascii_step
            if char_index:
                r, g, b = image[x, y] // color_step
                array_of_values.append((char_index, (r, g, b), (x, y)))

    return array_of_values


class ArtConverter:

    def __init__(self, file_name, font_size, color_lvl, is_sound):

        pg.init()
        self.path = os.path.join(video_folder, file_name)
        if is_sound and (file_name != "VebCamera"):
            self.player = MediaPlayer(self.path)
        elif file_name == "VebCamera":
            self.path = 0
        self.capture = cv2.VideoCapture(self.path)
        self.image, self.gray_image = self.get_image()
        self.screen_size = self.screen_width, self.screen_height = self.image.shape[0], self.image.shape[1]
        self.surface = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()

        self.color_lvl = color_lvl
        self.ASCII_chars = ' ixzao*#MW&8%B@$'
        self.ASCII_step = 255 // (len(self.ASCII_chars) - 1)
        self.font = pg.font.SysFont('Сourier', font_size, bold=True)
        self.char_step = int(font_size * 0.6)
        self.palette, self.color_step = self.create_palette()

        self.rec_fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.record = False
        self.recorder = cv2.VideoWriter(os.path.join(save_folder, 'video_ascii_rgb.mp4'),
                                        cv2.VideoWriter_fourcc(*'mp4v'), self.rec_fps, self.screen_size)

    def get_frame(self):
        frame = pg.surfarray.array3d(self.surface)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return cv2.transpose(frame)

    def record_frame(self):
        if self.record:
            frame = self.get_frame()
            self.recorder.write(frame)
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                self.record = not self.record
                cv2.destroyAllWindows()

    def draw_converted_image(self):
        self.image, self.gray_image = self.get_image()
        values = accelerated_conversion(self.image, self.gray_image, self.screen_width, self.screen_height,
                                        self.ASCII_step, self.color_step, self.char_step)
        for char_index, color, (x, y) in values:
            char = self.ASCII_chars[char_index]
            self.surface.blit(self.palette[char][color], (x, y))

    def create_palette(self):
        colors, color_step = np.linspace(0, 255, num=self.color_lvl, dtype=int, retstep=True)
        color_palette = [np.array([r, g, b]) for r in colors for g in colors for b in colors]
        palette = dict.fromkeys(self.ASCII_chars, None)
        color_step = int(color_step)
        for char in palette:
            char_palette = {}
            for color in color_palette:
                color_key = tuple(color // color_step)
                char_palette[color_key] = self.font.render(char, False, tuple(color))
            palette[char] = char_palette
        return palette, color_step

    def save_image(self):
        pygame_image = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(save_folder, 'ascii_image_rgb.jpg'), cv2_img)

    def get_image(self):
        ret, self.cv2_image = self.capture.read()
        if not ret:
            exit()
        transposed_image = cv2.transpose(self.cv2_image)
        image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2RGB)
        gray_image = cv2.cvtColor(transposed_image, cv2.COLOR_RGB2GRAY)

        return image, gray_image

    def draw_cv2_image(self):
        resized_cv2_image = cv2.resize(self.cv2_image, (self.screen_width//4, self.screen_height//4),
                                       interpolation=cv2.INTER_AREA)
        cv2.imshow('img', resized_cv2_image)

    def draw(self):
        self.surface.fill('black')
        self.draw_converted_image()
        self.draw_cv2_image()

    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        self.save_image()
                    if event.key == pg.K_r:
                        self.record = not self.record

            self.record_frame()
            self.draw()
            pg.display.set_caption(str(round(self.clock.get_fps())))
            pg.display.flip()
            self.clock.tick()


app = ArtConverter(file_name="girl.mp4", font_size=12, color_lvl=8, is_sound=True)
app.run()
