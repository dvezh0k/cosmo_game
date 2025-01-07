import asyncio
import curses
import time
import random


from file_manager import get_frame
from curses_tools import draw_frame, read_controls
from itertools import cycle


TIC_TIMEOUT = 0.1
STARS = '+*.:'


async def animate_spaceship(canvas, frames, start_row, start_column):
    """Display animation of spaceship with flight control capability."""

    canvas.nodelay(True)
    row, column = start_row, start_column

    for item in cycle(frames):
        delta_row, delta_col, _ = read_controls(canvas)
        row += delta_row
        column += delta_col
        draw_frame(canvas, row, column, item)
        canvas.refresh()
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, item, negative=True)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    """Display stars with blinks."""
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(random.randint(20, 50)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    """Game engine"""

    curses.curs_set(False)

    max_row, max_column = curses.window.getmaxyx(canvas)

    first_frame = get_frame('frames/rocket_frame_1.txt')
    second_frame = get_frame('frames/rocket_frame_2.txt')
    frames = [first_frame, second_frame]

    coroutines = [fire(canvas, max_row // 2, max_column //2)]

    for _ in range(random.randint(1, (max_row * max_column)) // 4):
        coroutines.append(
            blink(canvas,
                  random.randint(1, max_row - 2),
                  random.randint(1, max_column - 2),
                  random.choice(STARS)
                  )
        )

    coroutines.append(animate_spaceship(canvas, frames, max_row // 2, max_column // 2))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
