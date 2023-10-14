import pygame as pg
import pygame.gfxdraw
import cv2
import os


main_folder = os.path.dirname(__file__)
img_folder = os.path.join(main_folder, "input")
save_folder = os.path.join(main_folder, "output")


class ArtConverter:

    def __init__(self, file_name, pixel_size):

        pg.init()
        self.path = os.path.join(img_folder, file_name)
        self.image, self.cv2_image = self.get_image()
        self.screen_size = self.screen_width, self.screen_height = self.image.shape[0], self.image.shape[1]
        self.surface = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()
        self.pixel_size = pixel_size

    def draw_converted_image(self):
        color_indices = self.image
        for x in range(0, self.screen_width, self.pixel_size):
            for y in range(0, self.screen_height, self.pixel_size):
                col = color_indices[x, y]
                pygame.gfxdraw.box(self.surface, (x, y, self.pixel_size, self.pixel_size), (col, col, col))

    def save_image(self):
        pygame_image = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2.imwrite(os.path.join(save_folder, 'pixel_image_gray_.jpg'), cv2_img)

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


app = ArtConverter(file_name="fefu.jpg", pixel_size=10)
app.run()
