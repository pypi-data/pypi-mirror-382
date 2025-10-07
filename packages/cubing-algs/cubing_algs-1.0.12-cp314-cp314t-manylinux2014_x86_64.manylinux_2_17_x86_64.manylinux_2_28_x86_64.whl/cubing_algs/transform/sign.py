from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move


def sign_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert an algorithm from standard notation to SiGN notation.
    """
    moves: list[Move] = []

    for move in old_moves:
        moves.append(move.to_sign)

    return Algorithm(moves)


def unsign_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert an algorithm from SiGN notation to standard notation.
    """
    moves: list[Move] = []

    for move in old_moves:
        moves.append(move.to_standard)

    return Algorithm(moves)
