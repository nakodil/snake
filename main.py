from typing import Tuple
import tkinter

CANVAS_BG = 'black'
PLAYER_SIZE = 100
PLAYER_IMAGE = 'snake.png'
PLAYER_SPEED = 100
LINE_COLOR = 'black'
TILE_SIZE = 32
SNAKE_COLOR = 'green'
SNAKE_SPEED = 10
FPS = 3


class Game:
    def __init__(self) -> None:
        self.window = tkinter.Tk()
        self.window.attributes('-fullscreen', True)
        self.window.bind('<Key>', self.on_key)
        self.width = self.window.winfo_screenwidth()
        self.height = self.window.winfo_screenheight()
        self.tile_size = TILE_SIZE
        self.cols = self.width // self.tile_size
        self.rows = self.height // self.tile_size
        self.canvas = tkinter.Canvas(
            self.window,
            bg=CANVAS_BG,
            width=self.width,
            height=self.height,
            highlightthickness=0
        )
        self.canvas.pack()
        self.snake = Snake(
            self,
            self.cols // 2 * self.tile_size,
            self.rows // 2 * self.tile_size,
            SNAKE_COLOR,
            'w',
            's',
            'a',
            'd'
        )
        self.update()
        self.window.mainloop()

    def on_key(self, event) -> None:
        if event.keysym == 'Escape':
            print('Пока!')
            self.window.destroy()
        else:
            self.snake.on_key(event)

    def update(self):
        self.canvas.delete('all')
        self.snake.draw()
        self.snake.move()
        self.canvas.after(1000 // FPS, self.update)


class Snake:
    def __init__(
            self,
            game: Game,
            x: int,
            y: int,
            fill_color: str,
            key_up: str,
            key_down: str,
            key_left: str,
            key_right: str
    ) -> None:
        self.game = game
        self.x = x
        self.y = y
        self.fill_color = fill_color
        self.key_up = key_up
        self.key_down = key_down
        self.key_left = key_left
        self.key_right = key_right
        self.canvas = self.game.canvas
        self.speed_x = 1
        self.speed_y = 0
        self.body = [(1, 1), (2, 2)]

    def on_key(self, event) -> None:
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

    def draw(self):
        self.canvas.create_rectangle(
            self.x,
            self.y,
            self.x + self.game.tile_size,
            self.y + self.game.tile_size,
            fill=self.fill_color
        )

    def move(self) -> None:
        self.x += self.speed_x * self.game.tile_size
        self.y += self.speed_y * self.game.tile_size


if __name__ == '__main__':
    Game()
