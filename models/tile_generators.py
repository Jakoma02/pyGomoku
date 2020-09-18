from .constants import Direction


def horizontal_generator(board):
    def row_generator(r):
        for c in range(board.size):
            yield board[r][c]

    for row in range(board.size):
        yield row_generator(row)


def vertical_generator(board):
    def col_generator(c):
        for r in range(board.size):
            yield board[r][c]

    for col in range(board.size):
        yield col_generator(col)


def diagonal_a_generator(board):
    def diag_generator(i):
        if i < board.size:  # Left triangle
            _range = range(i + 1)
        else:  # Right triangle
            _range = range(i - board.size + 1, board.size)

        for r, c in zip(_range, reversed(_range)):
            yield board[r][c]

    for i in range(2 * board.size - 1):
        yield diag_generator(i)


def diagonal_b_generator(board):
    def diag_generator(i):
        if i < board.size:  # Left triangle
            row_range = range(i + 1)
            col_range = range((board.size - 1) - i, board.size)
        else:  # Right triangle
            i -= board.size - 1
            row_range = range(i, board.size)
            col_range = range(board.size - i)

        for r, c in zip(row_range, col_range):
            yield board[r][c]

    for i in range(2 * board.size - 1):
        yield diag_generator(i)


def all_empty_tiles(board):
    """
    Generates all empty tiles, row by row
    :param board:
    :return:
    """
    for x in range(board.size):
        for y in range(board.size):
            tile = board[x][y]
            if tile.empty():
                yield board[x][y]


def all_generators(board):
    """
    Generates tiles in all directions and return them with the directions
    :param board:
    :return: tuple of generator 'line' and Direction 'direction'
    """
    generators = [
        (Direction.HORIZONTAL, horizontal_generator(board)),
        (Direction.VERTICAL, vertical_generator(board)),
        (Direction.DIAGONAL_A, diagonal_a_generator(board)),
        (Direction.DIAGONAL_B, diagonal_b_generator(board))
    ]

    for direction, generator in generators:
        for line in generator:
            yield line, direction


def neighbors(board, x, y):
    """
    Generator of all neighbors of given position that are within bounds.
    :param size: size of the board
    :param x: x coordinate
    :param y: y coordinate
    """
    for i in range(x - 1, x + 2):
        if i < 0:
            continue
        if i >= board.size:
            continue

        for j in range(y - 1, y + 1):
            if j < 0:
                continue
            if j >= board.size:
                continue

            if (i, j) == (x, y):
                # This is me
                continue

            yield (i, j)


def is_valid(board, x, y):
    return \
        0 <= x < board.size and \
        0 <= y < board.size


def direction_neighbors(board, direction, x, y):
    """
    Returns the two neighboring tiles' coordinates
    in the given direction, if they are valid
    """
    if direction == Direction.HORIZONTAL:
        dir_neighbors = [(x - 1, y), (x + 1, y)]
    elif direction == Direction.VERTICAL:
        dir_neighbors = [(x, y - 1), (x, y + 1)]
    elif direction == Direction.DIAGONAL_A:
        dir_neighbors = [(x - 1, y - 1), (x + 1, y + 1)]
    elif direction == Direction.DIAGONAL_B:
        dir_neighbors = [(x - 1, y + 1), (x + 1, y - 1)]

    result = list(filter(dir_neighbors,
                         lambda pos: is_valid(board, pos[0], pos[1])))
    return result
