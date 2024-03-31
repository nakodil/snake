import tkinter
import random

WINDOW_COLOR = 'black'
CANVAS_COLOR = 'pink'
TEXT_COLOR = 'black'
LINE_COLOR = 'white'
SNAKE_COLOR = 'green'
FOOD_COLOR = 'red'
TILE_SIZE = 30
FPS = 10


class Screen:
    '''
    Окно во всю ширину экрана с квадратным игровым полем посередине,
    поле разделено на квадратные клетки
    '''
    def __init__(self, is_squared=True) -> None:
        self.window = tkinter.Tk()
        self.window.attributes('-fullscreen', True)
        self.window['bg'] = WINDOW_COLOR
        self.width = self.window.winfo_screenwidth()
        self.height = self.window.winfo_screenheight()
        if is_squared:
            self.width = min((self.width, self.height))
            self.height = min((self.width, self.height))
        self.tile_size = TILE_SIZE
        self.font_size = TILE_SIZE
        self.tiles_width = self.width // self.tile_size
        self.tiles_height = self.height // self.tile_size
        self.canvas = tkinter.Canvas(
            self.window,
            bg=CANVAS_COLOR,
            highlightthickness=0,
            width=self.height,
            height=self.width,
        )
        self.canvas.pack(expand=True)
        self.draw_lines()

    def quit(self, event):
        '''Выход из программы'''
        self.window.destroy()

    def draw_lines(self):
        '''Размечает клетки поля горизонтальными и вертикальными линиями'''
        for i in range(0, self.tiles_width + 1):
            y = i * self.tile_size
            self.canvas.create_line(
                0,
                y,
                self.width,
                y,
                fill=LINE_COLOR,
                tags='line'
            )

        for i in range(0, int(self.tiles_width) + 1):
            x = i * self.tile_size
            self.canvas.create_line(
                x,
                0,
                x,
                self.height,
                fill=LINE_COLOR,
                tags='line'
            )

    def draw_gameover(self, score: int):
        '''Рисует счет и меню в центре поля в конце игры'''
        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=f'Счет: {score}\nENTER - заново\nESC - выход',
            font=('Arial', self.font_size),
            fill=TEXT_COLOR,
            tags='message'
        )

    def draw_score(self, score: int):
        '''Рисует счет в левом верхнем углу поля'''
        self.canvas.create_text(
            self.font_size,
            self.font_size,
            text=f'{score}',
            font=('Arial', self.font_size),
            fill=TEXT_COLOR,
            tags='score'
        )


class Game:
    def __init__(self) -> None:
        self.screen = Screen()
        self.screen.window.bind('<Key>', self.on_key)
        self.food = None
        self.snake = None
        self.is_running = False
        self.score = 0
        self.start()
        self.screen.window.mainloop()

    def on_key(self, event: tkinter.Event) -> None:
        '''Диспетчер всех клавиш'''
        if event.keysym == 'Escape':
            self.screen.window.destroy()
        elif event.keysym == 'Return' and not self.is_running:
            self.start()
        else:
            self.snake.on_key(event)

    def start(self):
        '''Начинает игру заново'''
        self.food = None
        self.snake = Snake(
            self.screen.tiles_width // 2,
            self.screen.tiles_height // 2,
            self.screen.tile_size,
            SNAKE_COLOR,
            self.screen.canvas,
            'snake',
            'Up',
            'Down',
            'Left',
            'Right',
            self,
            self.screen
        )
        self.score = 0
        self.is_running = True
        self.update()

    def update(self):
        '''Один кадр игры'''
        self.screen.canvas.delete('snake', 'food', 'message', 'score')
        self.spawn_food()
        self.food.draw(self.food.x, self.food.y)
        self.screen.draw_score(self.score)
        self.snake.update()
        self.snake.draw()
        if not self.is_running:
            return self.screen.draw_gameover(self.score)
        self.screen.canvas.after(1000 // FPS, self.update)

    def spawn_food(self):
        '''
        Спаунит еду в случайной клетке игрового поля, если на нем нет еды
        FIXME: не спаунить на змею
        '''
        if self.food:
            return
        x = random.randint(1, self.screen.tiles_width - 1)
        y = random.randint(1, self.screen.tiles_height - 1)
        self.food = Food(
            x, y, self.screen.tile_size, FOOD_COLOR, self.screen.canvas, 'food'
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
            game: Game,
            screen: Screen,
    ) -> None:
        super().__init__(x, y, size, color, canvas, tag)
        self.key_up = key_up
        self.key_down = key_down
        self.key_left = key_left
        self.key_right = key_right
        self.speed_x = 1
        self.speed_y = 0
        self.body = []
        self.game = game
        self.screen = screen
        self.key_pressed = None

    def on_key(self, event: tkinter.Event) -> None:
        '''Запомниает последнюю нажатую клавишу'''
        self.key_pressed = event.keysym

    def update(self) -> None:
        '''Все действия змеи за один кадр'''
        self.collide_body()
        self.collide_canvas_borders()
        self.eat_food()
        self.change_speed()
        self.move()
        self.key_pressed = None

    def draw(self) -> None:
        super().draw(self.x, self.y)
        for section in self.body:
            super().draw(section[0], section[1])

    def change_speed(self) -> None:
        '''
        Поворот змеи в одну из 4 сторон,
        змея не может сразу повернуться на 180 градусов
        '''
        if self.key_pressed == self.key_up:
            speed_x_new = 0
            speed_y_new = -1
        elif self.key_pressed == self.key_down:
            speed_x_new = 0
            speed_y_new = 1
        elif self.key_pressed == self.key_left:
            speed_x_new = -1
            speed_y_new = 0
        elif self.key_pressed == self.key_right:
            speed_x_new = 1
            speed_y_new = 0
        else:
            speed_x_new = 0
            speed_y_new = 0

        if speed_x_new == self.speed_x * -1:
            return
        if speed_y_new == self.speed_y * -1:
            return

        self.speed_x = speed_x_new
        self.speed_y = speed_y_new

    def move(self) -> None:
        '''Двигает каждый сегмент тела, а потом голову'''
        if self.body:
            for i in range(len(self.body) - 1, 0, -1):
                self.body[i] = self.body[i - 1]
            self.body[0] = (self.x, self.y)

        self.x += self.speed_x
        self.y += self.speed_y

    def collide_canvas_borders(self) -> None:
        '''Столкновение головы c границами холста'''
        if self.x > self.screen.tiles_width - 1:  # справа
            self.game.is_running = False
        if self.x < 0:  # слева
            self.game.is_running = False
        if self.y > self.screen.tiles_height - 1:  # снизу
            self.game.is_running = False
        if self.y < 0:  # сверху
            self.game.is_running = False

    def collide_body(self) -> None:
        '''Столкновение головы с телом'''
        for segment in self.body:
            if self.x == segment[0] and self.y == segment[1]:
                self.is_running = False

    def eat_food(self) -> None:
        '''
        Змея съедает еду и увеличивает свое тело на один сегмент.
        Съеденная еда удаляется с поля.
        TODO: отрезанный хвост: переносим голову на еду,
        удаляем последний сегмент тела
        '''
        if not self.game.food:
            return
        if self.x == self.game.food.x:
            if self.y == self.game.food.y:
                self.game.score += 1
                self.body.append((self.game.food.x, self.game.food.y))
                self.game.food = None


if __name__ == '__main__':
    Game()
