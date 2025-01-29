import asyncio
import curses
import time
import random
from tools.file_manager import get_frame
from tools.curses_tools import draw_frame, read_controls, get_frame_size
from itertools import cycle
from models.space_garbage import fly_garbage
from tools.physics import update_speed
from variables import obstacles, coroutines, obstacles_in_last_collisions
from models.explosion import explode
from game_scenario import get_garbage_delay_tics,PHRASES


year = 1957
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
TICS_PER_YEAR = 15
GARBAGE_APPEARANCE_YEAR = 1961
LASER_GUN_APPEARANCE_YEAR = 2020


async def change_year():
    """Display game duration"""
    global year
    await sleep(TICS_PER_YEAR)
    year += 1


async def show_year(canvas):
    """Display years counter and text description of the year"""
    max_row, max_column = curses.window.getmaxyx(canvas)
    row = max_row - MARGINS_FROM_FRAME
    column = max_column - max_column // 8

    global year

    while True:

        if year in PHRASES:
            canvas.derwin(row, max_column // 2)
            canvas.addstr(row, max_column // 2, PHRASES[year], curses.A_REVERSE)

        text = f'Year: {year}'
        canvas.addstr(row, column, text, curses.A_BOLD)
        await change_year()


async def show_gameover(canvas):
    """Display game over frame"""
    frame = get_frame('frames/game_over.txt')
    max_row, max_column = curses.window.getmaxyx(canvas)
    frame_rows, frame_columns = get_frame_size(frame)
    row = max_row // 2 - frame_rows // 2
    column = max_column // 2 - frame_columns // 2

    while True:
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)


async def sleep(tics=1):
    """Make a pause during number of tics"""
    for _ in range(tics):
        await asyncio.sleep(0)


async def fill_orbit_with_garbage(canvas, max_column):
    """Continuously fill the orbit with garbage"""
    garbage_frames = [get_frame(frame) for frame in GARBAGE_FRAMES]

    global year
    while year < GARBAGE_APPEARANCE_YEAR:
        await asyncio.sleep(0)

    while True:
        for _ in range(random.randint(1, MAX_GARBAGE_ON_SCREEN)):
            coroutines.append(
                fly_garbage(canvas,
                            random.randint(MARGINS_FROM_FRAME, max_column - MARGINS_FROM_FRAME),
                            random.choice(garbage_frames)
                      )
            )
        await sleep(get_garbage_delay_tics(year))


async def animate_spaceship(canvas, frames, start_row, start_column):
    """Display animation of spaceship with flight control capability."""

    canvas.nodelay(True)
    row, column = start_row, start_column
    row_speed = column_speed = 0

    for item in cycle(frames):
        frame_rows, frame_columns = get_frame_size(item)
        max_row, max_column = curses.window.getmaxyx(canvas)

        delta_row, delta_col, shooting = read_controls(canvas)

        # Ограничение на вылет за границы поля
        row = min(max(row, delta_row), max_row - frame_rows + delta_row)
        column = min(max(column, delta_col), max_column - frame_columns + delta_col)

        row_speed, column_speed = update_speed(row_speed, column_speed, delta_row, delta_col)

        row += row_speed
        column += column_speed
        draw_frame(canvas, row, column, item)

        if shooting:
            coroutines.append(fire(canvas, row, column + frame_columns // 2))

        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                draw_frame(canvas, row, column, item, negative=True)
                await show_gameover(canvas)
                return

        await asyncio.sleep(0)
        draw_frame(canvas, row, column, item, negative=True)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    while year < LASER_GUN_APPEARANCE_YEAR:
        await asyncio.sleep(0)

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

        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                await explode(canvas, row, column)
                return

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

    coroutines.append(show_year(canvas))

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
