WIDTH, HEIGHT = 960, 544
TILE_SIZE = 32
RING_POSITION = (128, 424)

MAP = (
    ['#' * 30, '###' + '.' * 24 + '###', '##' + '.' * 26 + '##']
    + ['#' + '.' * 28 + '#'] * 4
    + ['#' + '.' * 28 + 'E'] * 2
    + ['#' + '.' * 28 + '#'] * 4
    + ['##' + '.' * 26 + '##', '###' + '.' * 24 + '###']
    + ['#' * 30] * 2
)
GOBLIN_SPAWNS = [(944, 248), (944, 264), (944, 280)]


def can_stand(x, y, doors_open=False):
    for ox, oy in ((-7, -4), (7, -4), (-7, 4), (7, 4)):
        column = int((x + ox) // TILE_SIZE)
        row = int((y + oy) // TILE_SIZE)
        if not (0 <= row < len(MAP) and 0 <= column < len(MAP[row])):
            return False
        if MAP[row][column] == '#' or (
                MAP[row][column] == 'E' and not doors_open):
            return False
    return True


def draw_map(screen, doors_open):
    screen.fill((17, 19, 27))
    for row, line in enumerate(MAP):
        for column, symbol in enumerate(line):
            detail = column * 73856093 ^ row * 19349663 ^ 17
            detail = (detail ^ (detail >> 13)) % 100
            tile = (49, 50, 51)[detail % 3] if detail < 16 else 48
            if symbol == '#' or (symbol == 'E' and not doors_open):
                tile = 24
            position = (column * TILE_SIZE, row * TILE_SIZE)
            screen.blit(f'tiles_2x/tile_{tile:04d}', position)
    if doors_open:
        color = (245, 255, 190)
        screen.draw.text('SAÍDA', (831, 238), fontsize=23, color=color)
        for start in ((891, 247), (905, 241), (905, 253)):
            screen.draw.line(start, (912, 247), color)
