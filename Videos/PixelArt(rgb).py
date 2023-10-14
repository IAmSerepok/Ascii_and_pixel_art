import pygame as pg
import numpy as np
import pygame.gfxdraw
from numba import njit
from ffpyplayer.player import MediaPlayer
import cv2
import os


main_folder = os.path.dirname(__file__)
video_folder = os.path.join(main_folder, "input")
save_folder = os.path.join(main_folder, "output")


@njit(fastmath=True)
def accelerated_conversion(image, width, height, color_step, step):
    values = []
    for x in range(0, width, step):
        for y in range(0, height, step):
            r, g, b = image[x, y] // color_step
            if r + g + b:
                values.append(((r, g, b), (x, y)))
    return values


class ArtConverter:

    def __init__(self, file_name, pixel_size, color_lvl, is_sound):

        pg.init()
        self.path = os.path.join(video_folder, file_name)
        if is_sound and (file_name != "VebCamera"):
            self.player = MediaPlayer(self.path)
        elif file_name == "VebCamera":
            self.path = 0
        self.capture = cv2.VideoCapture(self.path)
        self.image = self.get_image()
        self.screen_size = self.screen_width, self.screen_height = self.image.shape[0], self.image.shape[1]
        self.surface = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()

        self.color_lvl = color_lvl
        self.pixel_size = pixel_size
        self.palette, self.color_step = self.create_palette()

        self.rec_fps = 25
        self.record = False
        self.recorder = cv2.VideoWriter(os.path.join(save_folder, 'video_pixel_rgb.mp4'),
                                        cv2.VideoWriter_fourcc(*'mp4v'), self.rec_fps, self.screen_size)

    def get_frame(self):
        frame = pg.surfarray.array3d(self.surface)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
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
        self.image = self.get_image()
        values = accelerated_conversion(self.image, self.screen_width,
                                        self.screen_height, self.color_step, self.pixel_size)
        for color_key, (x, y) in values:
            color = self.palette[color_key]
            pygame.gfxdraw.box(self.surface, (x, y, self.pixel_size, self.pixel_size), color)

    def save_image(self):
        pygame_image = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(save_folder, 'pixel_image_rgb.jpg'), cv2_img)

    def get_image(self):
        ret, self.cv2_image = self.capture.read()
        if not ret:
            exit()
        transposed_image = cv2.transpose(self.cv2_image)
        image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2RGB)
        return image

    def create_palette(self):
        colors, color_step = np.linspace(0, 255, num=self.color_lvl, dtype=int, retstep=True)
        color_palette = [np.array([r, g, b]) for r in colors for g in colors for b in colors]
        palette = {}
        color_step = int(color_step)
        for color in color_palette:
            color_key = tuple(color // color_step)
            palette[color_key] = color

        return palette, color_step

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


app = ArtConverter(file_name="girl.mp4", pixel_size=7, color_lvl=8, is_sound=True)
app.run()
