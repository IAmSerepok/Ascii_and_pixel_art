import pygame as pg
import numpy as np
import pygame.gfxdraw
import cv2
import os


main_folder = os.path.dirname(__file__)
img_folder = os.path.join(main_folder, "input")
save_folder = os.path.join(main_folder, "output")


class ArtConverter:

    def __init__(self, file_name, pixel_size, color_lvl):

        pg.init()
        self.path = os.path.join(img_folder, file_name)
        self.image, self.cv2_image = self.get_image()
        self.screen_size = self.screen_width, self.screen_height = self.image.shape[0], self.image.shape[1]
        self.surface = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()

        self.color_lvl = color_lvl
        self.pixel_size = pixel_size
        self.palette, self.color_step = self.create_palette()

    def draw_converted_image(self):
        color_indices = self.image // self.color_step
        for x in range(0, self.screen_width, self.pixel_size):
            for y in range(0, self.screen_height, self.pixel_size):
                color_key = tuple(color_indices[x, y])
                if sum(color_key):
                    color = self.palette[color_key]
                    pygame.gfxdraw.box(self.surface, (x, y, self.pixel_size, self.pixel_size), color)

    def save_image(self):
        pygame_image = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(save_folder, 'pixel_image_rgb.jpg'), cv2_img)

    def get_image(self):
        cv2_image = cv2.imread(self.path)
        transposed_image = cv2.transpose(cv2_image)
        image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2RGB)
        return image, cv2_image

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

            self.draw()
            pg.display.set_caption(str(round(self.clock.get_fps())))
            pg.display.flip()
            self.clock.tick()


app = ArtConverter(file_name="python.png", pixel_size=8, color_lvl=16)
app.run()
