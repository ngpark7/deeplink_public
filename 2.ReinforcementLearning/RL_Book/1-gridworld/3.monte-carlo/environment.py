import time
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image

np.random.seed(1)
PhotoImage = ImageTk.PhotoImage
UNIT = 100  # pixels
HEIGHT = 5  # grid height
WIDTH = 5  # grid width


class Env(tk.Tk):
    def __init__(self):
        super(Env, self).__init__()
        self.action_space = ['u', 'd', 'l', 'r']
        self.n_actions = len(self.action_space)
        self.title('monte carlo')
        self.geometry('{0}x{1}'.format(HEIGHT * UNIT, HEIGHT * UNIT))
        self.shapes = self.load_images()
        self.canvas = self._build_canvas()
        self.texts = []
        self.width = WIDTH
        self.height = HEIGHT
        self.all_states = []

        for x in range(WIDTH):
            for y in range(HEIGHT):
                state = [x, y]
                self.all_states.append(state)

    def _build_canvas(self):
        canvas = tk.Canvas(self, bg='white', height=HEIGHT * UNIT, width=WIDTH * UNIT)

        # create grids
        for c in range(0, WIDTH * UNIT, UNIT):  # 0~400 by 80
            x0, y0, x1, y1 = c, 0, c, HEIGHT * UNIT
            canvas.create_line(x0, y0, x1, y1)

        for r in range(0, HEIGHT * UNIT, UNIT):  # 0~400 by 80
            x0, y0, x1, y1 = 0, r, HEIGHT * UNIT, r
            canvas.create_line(x0, y0, x1, y1)

        # add img to canvas
        self.rectangle = canvas.create_image(50, 50, image=self.shapes[0])
        self.triangle1 = canvas.create_image(250, 150, image=self.shapes[1])
        self.triangle2 = canvas.create_image(150, 250, image=self.shapes[1])
        self.circle = canvas.create_image(250, 250, image=self.shapes[2])

        # pack all
        canvas.pack()

        return canvas

    def load_images(self):
        rectangle = PhotoImage(Image.open("../img/rectangle.png").resize((65, 65)))
        triangle = PhotoImage(Image.open("../img/triangle.png").resize((65, 65)))
        circle = PhotoImage(Image.open("../img/circle.png").resize((65, 65)))

        return rectangle, triangle, circle

    def text_value(self, row, col, contents, font='Helvetica', size=15, style='normal', color='black', anchor="nw"):
        origin_x, origin_y = 37, 39
        x, y = origin_y + (UNIT * col), origin_x + (UNIT * row)
        font = (font, str(size), style)
        text = self.canvas.create_text(x, y, fill=color, text=contents, font=font, anchor=anchor)
        return self.texts.append(text)

    def print_value_table(self, value_table, samples_visited):
        for i in self.texts:
            self.canvas.delete(i)

        for i in range(WIDTH):
            for j in range(HEIGHT):
                isVisited = False
                for sample_ in samples_visited:
                    if i == sample_[0][0] and j == sample_[0][1]:
                        isVisited = True
                if i == 0 and j == 0:
                    isVisited = True
                if isVisited:
                    self.text_value(j, i, round(value_table[str([i, j])], 2), color='red')
                else:
                    self.text_value(j, i, round(value_table[str([i, j])], 2), color='black')

    @staticmethod
    def coords_to_state(coords):
        x = int((coords[0] - 50) / 100)
        y = int((coords[1] - 50) / 100)
        return [x, y]

    def reset(self):
        self.update()
        x, y = self.canvas.coords(self.rectangle)
        self.canvas.move(self.rectangle, UNIT / 2 - x, UNIT / 2 - y)
        # return observation
        time.sleep(2)
        return self.coords_to_state(self.canvas.coords(self.rectangle))

    def step(self, action):
        state = self.canvas.coords(self.rectangle)
        base_action = np.array([0, 0])
        self.render()

        if action == 0:  # 상
            if state[1] > UNIT:
                base_action[1] -= UNIT
        elif action == 1:  # 하
            if state[1] < (HEIGHT - 1) * UNIT:
                base_action[1] += UNIT
        elif action == 2:  # 좌
            if state[0] > UNIT:
                base_action[0] -= UNIT
        elif action == 3:  # 우
            if state[0] < (WIDTH - 1) * UNIT:
                base_action[0] += UNIT

        # 에이전트 이동
        self.canvas.move(self.rectangle, base_action[0], base_action[1])

        # 에이전트(빨간 네모)를 가장 상위로 배치
        self.canvas.tag_raise(self.rectangle)

        next_state = self.canvas.coords(self.rectangle)

        # 보상 함수
        if next_state == self.canvas.coords(self.circle):
            reward = 100
            done = True
        elif next_state in [self.canvas.coords(self.triangle1),
                            self.canvas.coords(self.triangle2)]:
            reward = -100
            done = True
        else:
            reward = 0
            done = False

        next_state = self.coords_to_state(next_state)

        return next_state, reward, done

    def render(self):
        time.sleep(0.03)
        self.update()
