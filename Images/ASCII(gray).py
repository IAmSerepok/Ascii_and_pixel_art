import pygame as pg
import cv2
import os


main_folder = os.path.dirname(__file__)
img_folder = os.path.join(main_folder, "input")
save_folder = os.path.join(main_folder, "output")


class ArtConverter:

    def __init__(self, file_name, font_size):

        pg.init()
        self.path = os.path.join(img_folder, file_name)
        self.image, self.cv2_image = self.get_image()
        self.screen_size = self.screen_width, self.screen_height = self.image.shape[0], self.image.shape[1]
        self.surface = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()

        self.ASCII_chars = ' .",:;!~+-xmo*#W&8@'
        self.ASCII_step = 255 // (len(self.ASCII_chars) - 1)
        self.font = pg.font.SysFont('Сourier', font_size, bold=True)
        self.char_step = int(font_size * 0.6)
        self.rendered_ASCII_chars = [self.font.render(char, False, 'white') for char in self.ASCII_chars]

    def draw_converted_image(self):
        char_indices = self.image // self.ASCII_step
        for x in range(0, self.screen_width, self.char_step):
            for y in range(0, self.screen_height, self.char_step):
                char_index = char_indices[x, y]
                if char_index:
                    self.surface.blit(self.rendered_ASCII_chars[char_index], (x, y))

    def save_image(self):
        pygame_image = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2.imwrite(os.path.join(save_folder, 'ascii_image_gray.jpg'), cv2_img)

    def get_image(self):
        cv2_image = cv2.imread(self.path)
        transposed_image = cv2.transpose(cv2_image)
        gray_image = cv2.cvtColor(transposed_image, cv2.COLOR_RGB2GRAY)

        return gray_image, cv2_image

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


app = ArtConverter(file_name="python.png", font_size=12)
app.run()
