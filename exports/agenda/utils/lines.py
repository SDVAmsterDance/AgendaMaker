import aggdraw
import random


def squiggle(im, x, start_y, end_y, diff=20, steps=5):
    canvas = aggdraw.Draw(im)
    pen = aggdraw.Pen("black")
    path = aggdraw.Path()
    path.moveto(x, start_y)
    start = [x, start_y]
    lenght = end_y - start_y
    alternator = random.choice([-1, 1])
    for i in range(steps):
        new_start = [start[0], start_y + i * (lenght / steps)]
        start = new_start
        end = [start[0], start_y + (i + 1) * (lenght / steps)]
        middle = [x + alternator * random.randint(int(diff / 5), diff), (start[1] + end[1]) / 2]
        path.curveto(*start, *middle, *end)
        path.moveto(*end)
        alternator *= -1

    canvas.path(path, path, pen)
    canvas.flush()