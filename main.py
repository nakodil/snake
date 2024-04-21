import tkinter
import random
import config


class App:
    '''
    Приложение:
    создает полноэкранное окно;
    создает холст шириной и высотой, кратными размеру плитки в центре окна;
    создает экземпляр игры;
    запускает mainloop окна.
    '''
    def __init__(self) -> None:
        self.window = tkinter.Tk()
        self.window.title = config.WINDOW_TITLE
        self.window.attributes('-fullscreen', True)
        self.window['bg'] = config.WINDOW_BG

        self.width = self.window.winfo_screenwidth()
        self.height = self.window.winfo_screenheight()

        self.canvas = tkinter.Canvas(
            self.window,
            width=self.width // config.TILE_SIZE * config.TILE_SIZE,
            height=self.height // config.TILE_SIZE * config.TILE_SIZE,
            bg=config.CANVAS_BG,
            highlightthickness=0
        )
        self.canvas.pack(expand=True)
        self.game = Game(self.canvas)
        self.window.mainloop()


class Game:
    '''Игра'''
    def __init__(self, canvas: tkinter.Canvas, is_grid=True) -> None:
        self.canvas = canvas
        self.canvas.focus_set()
        self.canvas.update()  # До апдейта размер виджетов будет 1 1
        self.canvas.bind('<Key>', self.on_key)
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        self.font_size = int(min((self.width, self.height)) * 0.05)
        self.is_grid = is_grid
        self.cols = self.width // config.TILE_SIZE
        self.rows = self.height // config.TILE_SIZE
        self.snake = None
        self.food = None
        self.is_running = False
        self.menu_heading_text = config.WINDOW_TITLE
        self.menu_heading_color = config.MENU_HEADING_COLOR
        if self.is_grid:
            self.draw_lines()
        self.show_menu()

    def show_menu(self) -> None:
        '''Рисует меню выбора действий на холсте'''
        self.canvas.create_text(
            self.width // 2,
            self.height * 0.3,
            text=self.menu_heading_text,
            fill=self.menu_heading_color,
            font=(config.MENU_FONT_NAME, int(self.font_size * 2)),
            tags='menu',
            justify='center',

        )

        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=config.MENU_TEXT,
            fill=config.MENU_TEXT_COLOR,
            font=(config.MENU_FONT_NAME, self.font_size),
            tags='menu',
            justify='center'
        )

    def run(self) -> None:
        '''Запускает новую игру'''
        self.canvas.delete('snake', 'food', 'menu')
        self.snake = Snake(
            self.canvas,
            self.cols // 2,
            self.rows // 2,
            config.SNAKE_HEAD_COLOR,
            config.SNAKE_BODY_COLOR,
            config.KEY_LEFT,
            config.KEY_RIGHT,
            config.KEY_UP,
            config.KEY_DOWN
        )
        self.food = None
        self.is_running = True
        self.update()

    def on_key(self, event: tkinter.Event) -> None:
        '''Диспетчер клавиш'''
        if event.keysym == config.KEY_QUIT:
            window = self.canvas.winfo_toplevel()
            window.destroy()
        elif event.keysym == config.KEY_NEW_GAME:
            if not self.is_running:
                self.run()
        else:
            self.snake.on_key(event)

    def draw_lines(self) -> None:
        '''Размечает холст на клетки вертикальными и горизонтальными линиями'''
        for i in range(1, self.rows):
            self.canvas.create_line(
                0,
                i * config.TILE_SIZE,
                self.width,
                i * config.TILE_SIZE,
                fill=config.LINE_COLOR
            )
        for i in range(1, self.cols):
            self.canvas.create_line(
                i * config.TILE_SIZE,
                0,
                i * config.TILE_SIZE,
                self.height,
                fill=config.LINE_COLOR
            )

    def update(self) -> None:
        '''Обновляет всю игру FPS раз в секунду'''
        if not self.food:
            self.food = Food(self, self.canvas, config.FOOD_COLOR)
        if self.food:
            self.food.draw()
        self.snake.change_direction()
        self.snake.move()
        self.snake.collide_borders(self)
        self.snake.collide_body(self)
        if not self.is_running:
            return self.show_menu()
        self.snake.eat_food(self)
        self.snake.draw()
        self.check_victory()
        if self.is_running:
            self.canvas.after(1000 // config.FPS, self.update)
        else:
            return self.show_menu()

    def check_victory(self) -> None:
        '''Завершает игру победой, если змея заняла все игровое поле'''
        if len(self.snake.body) == self.cols * self.rows:
            self.is_running = False
            self.menu_heading_text = 'Победа!'
            self.menu_heading_color = config.VICTORY_COLOR


class Snake:
    '''Змейка'''
    def __init__(
            self,
            canvas: tkinter.Canvas,
            col: int,
            row: int,
            head_color: str,
            body_color: str,
            key_left: str,
            key_right: str,
            key_up: str,
            key_down: str
    ) -> None:
        self.canvas = canvas
        self.col = col
        self.row = row

        self.max_col = self.canvas.winfo_width() // config.TILE_SIZE - 1
        self.max_row = self.canvas.winfo_height() // config.TILE_SIZE - 1

        self.head_color = head_color
        self.body_color = body_color
        self.tag = 'snake'

        self.key_up = key_up
        self.key_down = key_down
        self.key_left = key_left
        self.key_right = key_right
        self.key_pressed = None

        self.body = []
        self.direction = (1, 0)

    def on_key(self, event: tkinter.Event) -> None:
        '''Запоминает нажатую клавишу'''
        self.key_pressed = event.keysym

    def change_direction(self) -> None:
        '''
        Поворачивает змею в зависимости от запомненой клавиши,
        поворт на 180 гадусов запрещен
        '''
        new_direction = self.direction

        if self.key_pressed == self.key_up:
            new_direction = (0, -1)
        elif self.key_pressed == self.key_down:
            new_direction = (0, 1)
        elif self.key_pressed == self.key_right:
            new_direction = (1, 0)
        elif self.key_pressed == self.key_left:
            new_direction = (-1, 0)

        # запрещает поворот на 180 градусов
        if self.direction[0] == -new_direction[0]:
            return
        if self.direction[1] == -new_direction[1]:
            return
        self.direction = new_direction

    def draw(self) -> None:
        '''Рисует тело и голову змеи на холсте'''
        self.canvas.delete(self.tag)

        # рисуем все секции тела
        for section in self.body:
            self.canvas.create_rectangle(
                section[0] * config.TILE_SIZE,
                section[1] * config.TILE_SIZE,
                section[0] * config.TILE_SIZE + config.TILE_SIZE,
                section[1] * config.TILE_SIZE + config.TILE_SIZE,
                fill=self.body_color,
                tags=self.tag
            )

        # рисуем голову
        self.canvas.create_rectangle(
            self.col * config.TILE_SIZE,
            self.row * config.TILE_SIZE,
            self.col * config.TILE_SIZE + config.TILE_SIZE,
            self.row * config.TILE_SIZE + config.TILE_SIZE,
            fill=self.head_color,
            tags=self.tag
        )

    def move(self) -> None:
        '''Двигает каждую секцию тела змейки и ее голову'''
        self.key_pressed = None

        # движение тела
        if self.body:
            self.body = [(self.col, self.row)] + self.body[:-1]

        # движение головы
        self.col += self.direction[0]
        self.row += self.direction[1]

    def collide_borders(self, game: Game) -> None:
        '''Столкновения с границами экрана'''
        if self.col < 0:  # слева
            game.is_running = False
        if self.row < 0:  # сверху
            game.is_running = False
        if self.col > self.max_col:  # справа
            game.is_running = False
        if self.row > self.max_row:  # снизу
            game.is_running = False

        if not game.is_running:
            game.menu_heading_text = 'врезался в край'
            game.menu_heading_color = config.GAMEOVER_COLOR

    def collide_body(self, game: Game) -> None:
        '''Столкновение головы с секциями тела'''
        if (self.col, self.row) in self.body:
            game.is_running = False
            game.menu_heading_text = 'врезался в тело'
            game.menu_heading_color = config.GAMEOVER_COLOR

    def eat_food(self, game: Game) -> None:
        '''Поглощение еды'''
        if self.col == game.food.col and self.row == game.food.row:
            self.body.append((game.food.col, game.food.row))
            self.canvas.delete(game.food.tag)
            game.food = None


class Food:
    '''Еда, которой питается змея'''
    def __init__(
            self, game: Game, canvas: tkinter.Canvas, color: str
    ) -> None:
        self.game = game
        self.canvas = canvas
        self.col = None
        self.row = None
        self.color = color
        self.tag = 'food'
        self.spawn()

    def spawn(self) -> None:
        '''
        Выбирает еде колонну и ряд, которые не находятся
        на голове или теле змеи
        '''
        free_positions = []
        snake_head_position = (self.game.snake.col, self.game.snake.row)
        occupied_positions = self.game.snake.body + [snake_head_position]
        for col in range(self.game.cols):
            for row in range(self.game.rows):
                if (col, row) not in occupied_positions:
                    free_positions.append((col, row))
        if free_positions:
            self.col, self.row = random.choice(free_positions)
        else:
            self.game.food = None

    def draw(self) -> None:
        '''Рисует еду на холсте'''
        self.canvas.create_rectangle(
            self.col * config.TILE_SIZE,
            self.row * config.TILE_SIZE,
            self.col * config.TILE_SIZE + config.TILE_SIZE,
            self.row * config.TILE_SIZE + config.TILE_SIZE,
            fill=self.color,
            tags=self.tag
        )


if __name__ == '__main__':
    App()
