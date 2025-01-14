import asyncio
import curses
import time
import random
from file_manager import get_frame
from curses_tools import draw_frame, read_controls, get_frame_size
from itertools import cycle
from space_garbage import fly_garbage


TIC_TIMEOUT = 0.1
STARS = '+*.:'
MARGINS_FROM_FRAME = 2
GARBAGE_FRAMES = [
    'frames/garbage/duck.txt',
    'frames/garbage/hubble.txt',
    'frames/garbage/lamp.txt',
    'frames/garbage/trash_large.txt',
    'frames/garbage/trash_small.txt',
    'frames/garbage/trash_xl.txt'
]
MAX_GARBAGE_ON_SCREEN = 5
coroutines = []


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def fill_orbit_with_garbage(canvas, max_column):
    garbage_frames = [get_frame(frame) for frame in GARBAGE_FRAMES]

    while True:
        for _ in range(random.randint(1, MAX_GARBAGE_ON_SCREEN)):
            coroutines.append(
                fly_garbage(canvas,
                            random.randint(MARGINS_FROM_FRAME, max_column - MARGINS_FROM_FRAME),
                            random.choice(garbage_frames)
                      )
            )
        await sleep(random.randint(20, 40))




async def animate_spaceship(canvas, frames, start_row, start_column):
    """Display animation of spaceship with flight control capability."""

    canvas.nodelay(True)
    row, column = start_row, start_column

    for item in cycle(frames):
        delta_row, delta_col, _ = read_controls(canvas)

        frame_rows, frame_columns = get_frame_size(item)
        max_row, max_column = curses.window.getmaxyx(canvas)

        row = min(max(row, delta_row), max_row - frame_rows + delta_row)
        column = min(max(column, delta_col), max_column - frame_columns + delta_col)

        row += delta_row
        column += delta_col
        draw_frame(canvas, row, column, item)
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


async def blink(canvas, row, column, offset_tics, symbol='*'):
    """Display stars with blinks."""
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(offset_tics)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


def draw(canvas):
    """Game engine"""
    curses.curs_set(False)
    # canvas.border()

    max_row, max_column = curses.window.getmaxyx(canvas)

    #coroutines.append(fire(canvas, max_row // 2, max_column // 2))

    for _ in range(random.randrange((max_row * max_column)) // 8):
        coroutines.append(
            blink(canvas,
                  random.randint(MARGINS_FROM_FRAME, max_row - MARGINS_FROM_FRAME),
                  random.randint(MARGINS_FROM_FRAME, max_column - MARGINS_FROM_FRAME),
                  random.randint(20, 50),
                  random.choice(STARS)
                  )
        )

    coroutines.append(fill_orbit_with_garbage(canvas, max_column))

    first_frame = get_frame('frames/rocket_frame_1.txt')
    second_frame = get_frame('frames/rocket_frame_2.txt')
    spaceship_frames = [first_frame, first_frame, second_frame, second_frame]

    coroutines.append(animate_spaceship(canvas, spaceship_frames, max_row // 2, max_column // 2))

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
