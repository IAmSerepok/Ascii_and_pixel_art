import pygame as pg
from numba import njit
from ffpyplayer.player import MediaPlayer
import cv2
import os


main_folder = os.path.dirname(__file__)
video_folder = os.path.join(main_folder, "input")
save_folder = os.path.join(main_folder, "output")


@njit(fastmath=True)
def accelerated_conversion(image, width, height, ascii_step, step):
    values = []
    for x in range(0, width, step):
        for y in range(0, height, step):
            index = image[x, y] // ascii_step
            if index:
                values.append((index, (x, y)))

    return values


class ArtConverter:

    def __init__(self, file_name, font_size, is_sound):

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

        self.ASCII_chars = ' .",:;!~+-xmo*#W&8@'
        self.ASCII_step = 255 // (len(self.ASCII_chars) - 1)
        self.font = pg.font.SysFont('Сourier', font_size, bold=True)
        self.char_step = int(font_size * 0.6)
        self.rendered_ASCII_chars = [self.font.render(char, False, 'white') for char in self.ASCII_chars]

        self.rec_fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.record = False
        self.recorder = cv2.VideoWriter(os.path.join(save_folder, 'video_ascii_gray.mp4'),
                                        cv2.VideoWriter_fourcc(*'mp4v'), self.rec_fps, self.screen_size)

    def get_frame(self):
        frame = pg.surfarray.array3d(self.surface)
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
        values = accelerated_conversion(self.image, self.screen_width, self.screen_height,
                                        self.ASCII_step, self.char_step)
        for char_index, (x, y) in values:
            self.surface.blit(self.rendered_ASCII_chars[char_index], (x, y))

    def save_image(self):
        pygame_image = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2.imwrite(os.path.join(save_folder, 'ascii_image_gray.jpg'), cv2_img)

    def get_image(self):
        ret, self.cv2_image = self.capture.read()
        if not ret:
            exit()
        transposed_image = cv2.transpose(self.cv2_image)
        image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2GRAY)
        return image

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


app = ArtConverter(file_name="girl.mp4", font_size=12, is_sound=True)
app.run()
