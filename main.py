import asyncio
import curses
import time
import random


TIC_TIMEOUT = 0.1
STARS = '+*.:'

async def blink(canvas, row, column, symbol='*'):
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

'''
def draw(canvas):
    row, column = (5, 20)
    canvas.border()
    curses.curs_set(False)

    coroutines = [blink(canvas, row, column) for column in range(column, column + 9, 2)]

    while True:
        for coroutine in coroutines:
            coroutine.send(None)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
'''

def draw(canvas):
    canvas.border()
    curses.curs_set(False)

    max_row, max_column = curses.window.getmaxyx(canvas)

    coroutines = []

    for _ in range(random.randint(1, (max_row * max_column)) // 4):
        coroutines.append(
            blink(canvas,
                  random.randint(1, max_row - 2),
                  random.randint(1, max_column - 2),
                  random.choice(STARS)
                  )
        )

    while True:
        for coroutine in coroutines:
            coroutine.send(None)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
