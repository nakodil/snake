import tkinter
import random

WINDOW_COLOR = 'black'
CANVAS_COLOR = 'pink'
TEXT_COLOR = 'black'
LINE_COLOR = 'white'
SNAKE_COLOR = 'green'
FOOD_COLOR = 'red'
TILE_SIZE = 30
FPS = 5


class Game:
    def __init__(self) -> None:
        self.window = tkinter.Tk()
        self.window.attributes('-fullscreen', True)
        self.window['bg'] = WINDOW_COLOR
        self.window.bind('<Key>', self.on_key)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # играем в квадрате
        min_side = min((screen_width, screen_height))
        screen_width = min_side
        screen_height = min_side

        self.font_size = min_side // 25
        self.tile_size = TILE_SIZE
        self.width = screen_width // self.tile_size
        self.height = screen_height // self.tile_size
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.canvas = tkinter.Canvas(
            self.window,
            bg=CANVAS_COLOR,
            highlightthickness=0,
            height=self.height * self.tile_size,
            width=self.height * self.tile_size
        )
        self.canvas.pack(expand=True)
        self.food = None
        self.snake = None
        self.is_running = False
        self.score = None
        self.lines = False
        self.start()
        self.window.mainloop()

    def start(self):
        self.food = None
        self.snake = Snake(
            self.center_x,
            self.center_y,
            self.tile_size,
            SNAKE_COLOR,
            self.canvas,
            'snake',
            'Up',
            'Down',
            'Left',
            'Right',
            self.width,
            self.height
        )
        self.score = 0
        self.is_running = True
        self.canvas.delete('snake', 'food', 'message', 'score')
        self.update()

    def on_key(self, event: tkinter.Event) -> None:
        if event.keysym == 'Escape':
            self.window.destroy()
        elif event.keysym == 'Return':
            if not self.is_running:
                self.start()
        elif event.keysym == '1':
            if not self.lines:
                self.draw_lines()
                self.lines = True
            else:
                self.canvas.delete('line')
                self.lines = False
        else:
            self.snake.on_key(event)  # FIXME: слишком быстро, нужен FPS

    def draw_lines(self):
        # Горизонтальные
        for i in range(0, int(self.height) + 1):
            y = i * self.tile_size
            self.canvas.create_line(
                0,
                y,
                self.width * self.tile_size,
                y,
                fill=LINE_COLOR,
                tags='line'
            )

        # Вертикальные
        for i in range(0, int(self.width) + 1):
            x = i * self.tile_size
            self.canvas.create_line(
                x,
                0,
                x,
                self.height * self.tile_size,
                fill=LINE_COLOR,
                tags='line'
            )

    def update(self):
        '''Один кадр игры'''
        self.canvas.delete('snake', 'food', 'score')
        self.snake.draw()
        self.snake.update()
        if not self.snake.is_alive:
            return self.game_over()
        if not self.food:
            self.spawn_food()
        self.food.draw(self.food.x, self.food.y)
        if self.snake.x == self.food.x:
            if self.snake.y == self.food.y:
                self.score += 1
                self.snake.body.append((self.food.x, self.food.y))
                self.food = None
        self.draw_score()
        if self.is_running:
            self.canvas.after(1000 // FPS, self.update)

    def spawn_food(self):
        '''
        Спаунит еду в случайной клетке
        FIXME: не спаунить на змею
        '''
        x = random.randint(1, int(self.width) - 1)
        y = random.randint(1, int(self.height) - 1)
        self.food = Food(x, y, self.tile_size, FOOD_COLOR, self.canvas, 'food')

    def game_over(self):
        '''Завершает игру и показывает меню'''
        self.is_running = False
        self.canvas.create_text(
            self.center_x * self.tile_size,
            self.center_y * self.tile_size,
            text=f'Счет: {self.score}\nENTER - заново\nESC - выход',
            font=('Arial', self.font_size),
            fill=TEXT_COLOR,
            tags='message'
        )

    def draw_score(self):
        self.canvas.create_text(
            0 + self.font_size,
            0 + self.font_size,
            text=f'{self.score}',
            font=('Arial', self.font_size),
            fill=TEXT_COLOR,
            tags='score'
        )


class GameObject:
    def __init__(
            self,
            x: int,
            y: int,
            size: int,
            color: str,
            canvas: tkinter.Canvas,
            tag: str
    ) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.canvas = canvas
        self.tag = tag

    def draw(self, x: int, y: int):
        x0 = x * self.size
        y0 = y * self.size
        self.canvas.create_rectangle(
            x0,
            y0,
            x0 + self.size,
            y0 + self.size,
            fill=self.color,
            tags=self.tag
        )


class Food(GameObject):
    def __init__(
            self,
            x: int,
            y: int,
            size: int,
            color: str,
            canvas: tkinter.Canvas,
            tag: str
    ) -> None:
        super().__init__(x, y, size, color, canvas, tag)


class Snake(GameObject):
    def __init__(
            self,
            x: int,
            y: int,
            size: int,
            color: str,
            canvas: tkinter.Canvas,
            tag: str,
            key_up: str,
            key_down: str,
            key_left: str,
            key_right: str,
            x_max,
            y_max
    ) -> None:
        super().__init__(x, y, size, color, canvas, tag)
        self.key_up = key_up
        self.key_down = key_down
        self.key_left = key_left
        self.key_right = key_right
        self.x_max = x_max
        self.y_max = y_max
        self.speed_x = 1
        self.speed_y = 0
        self.body = []
        self.is_alive = True

    def on_key(self, event: tkinter.Event) -> None:
        if event.keysym == self.key_up:
            if self.speed_y != 1:
                self.speed_x = 0
                self.speed_y = -1
        elif event.keysym == self.key_down:
            if self.speed_y != -1:
                self.speed_x = 0
                self.speed_y = 1
        elif event.keysym == self.key_left:
            if self.speed_x != 1:
                self.speed_x = -1
                self.speed_y = 0
        elif event.keysym == self.key_right:
            if self.speed_x != -1:
                self.speed_x = 1
                self.speed_y = 0

    def update(self):
        self.move()
        self.collide_body()
        self.collide_canvas_borders()

    def draw(self):
        super().draw(self.x, self.y)
        for section in self.body:
            super().draw(section[0], section[1])

    def move(self) -> None:
        '''Двигает каждый сегмент тела, а потом голову'''
        if not self.is_alive:
            return
        if self.body:
            for i in range(len(self.body) - 1, 0, -1):
                self.body[i] = self.body[i - 1]
            self.body[0] = (self.x, self.y)

        self.x += self.speed_x
        self.y += self.speed_y

    def collide_canvas_borders(self) -> None:
        '''Столкновение головы c границами холста'''
        if self.x >= self.x_max:  # справа
            self.is_alive = False
        if self.x < 0:  # слева
            self.is_alive = False
        if self.y >= self.y_max:  # снизу
            self.is_alive = False
        if self.y < 0:  # сверху
            self.is_alive = False

    def collide_body(self) -> None:
        '''Столкновение головы с телом'''
        for segment in self.body:
            if self.x == segment[0] and self.y == segment[1]:
                self.is_alive = False


if __name__ == '__main__':
    Game()
