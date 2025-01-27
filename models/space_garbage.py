from tools.curses_tools import draw_frame, get_frame_size
import asyncio
from models.obstacles import Obstacle
from variables import obstacles, obstacles_in_last_collisions


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    garbage_frame_rows, garbage_frame_columns = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, garbage_frame_rows, garbage_frame_columns)
    obstacles.append(obstacle)

    try:
        while row < rows_number:

            if obstacle in obstacles_in_last_collisions:
                obstacles_in_last_collisions.remove(obstacle)
                return

            #draw_frame(canvas, *obstacle.dump_bounding_box())
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            #draw_frame(canvas, *obstacle.dump_bounding_box(), negative=True)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row = row

    finally:
        obstacles.remove(obstacle)
