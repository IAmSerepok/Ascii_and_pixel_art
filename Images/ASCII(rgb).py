import pygame as pg
import numpy as np
import cv2
import os


main_folder = os.path.dirname(__file__)
img_folder = os.path.join(main_folder, "input")
save_folder = os.path.join(main_folder, "output")


class ArtConverter:

    def __init__(self, file_name, font_size, color_lvl):

        pg.init()
        self.path = os.path.join(img_folder, file_name)
        self.image, self.gray_image, self.cv2_image = self.get_image()
        self.screen_size = self.screen_width, self.screen_height = self.image.shape[0], self.image.shape[1]
        self.surface = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()

        self.color_lvl = color_lvl
        self.ASCII_chars = ' ixzao*#MW&8%B@$'
        self.ASCII_step = 255 // (len(self.ASCII_chars) - 1)
        self.font = pg.font.SysFont('Сourier', font_size, bold=True)
        self.char_step = int(font_size * 0.6)
        self.palette, self.color_step = self.create_palette()

    def draw_converted_image(self):
        char_indices = self.gray_image // self.ASCII_step
        color_indices = self.image // self.color_step
        for x in range(0, self.screen_width, self.char_step):
            for y in range(0, self.screen_height, self.char_step):
                char_index = char_indices[x, y]
                if char_index:
                    char = self.ASCII_chars[char_index]
                    color = tuple(color_indices[x, y])
                    self.surface.blit(self.palette[char][color], (x, y))

    def save_image(self):
        pygame_image = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(save_folder, 'ascii_image_rgb.jpg'), cv2_img)

    def get_image(self):
        cv2_image = cv2.imread(self.path)
        transposed_image = cv2.transpose(cv2_image)
        image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2RGB)
        gray_image = cv2.cvtColor(transposed_image, cv2.COLOR_RGB2GRAY)

        return image, gray_image, cv2_image

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


app = ArtConverter(file_name="python.png", font_size=12, color_lvl=8)
app.run()
