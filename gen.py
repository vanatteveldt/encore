from collections import defaultdict
from itertools import count
import random
import sys
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
env = Environment(
    loader=FileSystemLoader(searchpath="./"),
)
def shuffle(x):
    x = list(x)
    random.shuffle(x)
    return x

nrows = 7
ncols = 15
rowgifts = ["🎁", "💣", "❤️",  "💣", "🎁", "❤️","💣"]*2
colpoints = [5, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 5]
colpoint2 = [3, 2, 2, 2, 1, 1, 1, 0, 1, 1, 1, 2, 2, 2, 3]
colnames = [chr(65+i) for i in range(ncols)]
rownames = [chr(65+ncols+i) for i in range(nrows)]
colors = ["green", "orange", "red", "blue", "yellow"]
moves = [(1,0), (-1,0), (0,1), (0,-1)]
adjacency = [ (1,-1), (1,0),  (1,1),
              (0,-1),         (0,1),
             (-1,-1), (-1,0), (-1,1)]
scores = ["Bonus", "Rows", "Cols", "❤️", "! (1)", "🎁 (2)", "☆ (-2)", "Total"]

def getsums(coords):
    colsums, rowsums = defaultdict(int), defaultdict(int)
    for (px,py) in coords:
        colsums[px] += 1
        rowsums[py] += 1
    return colsums, rowsums



def check_path(grid, path):
    # Check that path does not contain too many adjacent tiles
    colsums, rowsums = getsums(path)
    if any(v >= 3 for v in colsums.values()):
        return False
    if any(v >= 4 for v in rowsums.values()):
        return False
    if len(path) == 6:
        if sum(1 for x in rowsums.values() if x == 3) == 2:
            return False
    if len(path) == 4:
        if sum(1 for x in rowsums.values() if x == 2) == 2:
            return False
    return True


def find_path(grid, x,y, n, value, path=None):
    """   print(path)
    Recursively find n empty contiguous tiles starting from x,y
    returns a set of coordinates or None if not path could be found
    """
    if path is None:
        path = set()
    # Check that the current spot is empty
    if (x,y) in grid or (x,y) in path:
        return None
    # Check that the current spot is inside the grid
    if x > ncols or x <= 0 or y <= 0 or y > nrows:
        return None
    # Check that the current spot is not adjacent to the same color
    for (dx, dy) in adjacency:
        if grid.get((x+dx, y+dy)) == value:
            return None
    path = path | {(x,y)}
    if n == 1:
        return path
    for (dx, dy) in shuffle(moves):
        new_path = find_path(grid, x+dx, y+dy, n-1, value, path)
        if new_path:
            return new_path

def place(grid, x, y, n, value):
    """Try to place n contiguous values in the grid starting from x,y"""
    path = find_path(grid, x,y,n, value)
    if not path:
        return
    if not check_path(grid, path):
        return
    if path:
        for x,y in path:
            grid[x,y] = value
    return path

def get_empty(grid, tiles):
    for tile in tiles:
        if tile not in grid:
            return tile


def find_random_empty(grid):
    for x in shuffle(range(1, ncols+1)):
        for y in shuffle(range(1, nrows+1)):
            if (x,y) not in grid:
                yield (x,y)

def ordered_empty(grid):
    colsums, rowsums = getsums(grid)
    scores = {}
    for x in shuffle(range(1, ncols+1)):
        for y in shuffle(range(1, nrows+1)):
            if (x,y) not in grid:
                scores[x,y] = colsums[x] + rowsums[y] + random.random()
    return sorted(scores.keys(), key=lambda coord: scores[coord])

def gen():
    print("---")
    grid, symbols = {}, {}
    placed = set()
    stars = set()
    for color in colors:
        stars |= {(color, i) for i in shuffle(range(1,7))[:3]}
    # h-column

    for i, col in enumerate(shuffle(colors)):
        value = colors.index(col)
        n = 5 if i == 0 else random.randint(2,5)
        start = get_empty(grid, shuffle((8, i) for i in range(1,8)))
        if not start:
            return None, None
        if path := place(grid, start[0], start[1], n, value):
            if (col, n) in stars:
                symbols[shuffle(path)[-1]] = "☆"
        else:
            return None, None
        placed.add((value, n))
    # 6 tiles
    for ntiles in [6,5,4,3,2,1]:
        for col in shuffle(colors):
            value = colors.index(col)
            if (value, ntiles) in placed:
                continue

            for (x,y) in ordered_empty(grid):
                if path := place(grid, x,y, ntiles, colors.index(col)):
                    if ntiles == 6:
                        add_symbol(path, symbols, "🎁")
                    if (col, ntiles) in stars:
                        add_symbol(path, symbols, "☆")
                    break
            else:
                return None, None

    return grid, symbols


def add_symbol(path, symbols, symbol):
    loc = symbol_loc(path, symbols, symbol)
    if not loc:
        loc = symbol_loc(path, symbols)
    symbols[loc] = symbol


def symbol_loc(path, symbols, check_symbol=None):
    for x,y in shuffle(path):
        if (x, y) in symbols:
            continue
        if any(symbols.get((x+dx, y+dy)) == check_symbol
               for (dx, dy) in moves):
            continue
        return x, y

def get_board(seed):
    if seed:
        random.seed(seed)
    grid, symbols = None, None
    while not grid:
        grid, symbols = gen()

    template = env.get_template("template.html")
    html = template.render(**globals(), **locals())
    return html
