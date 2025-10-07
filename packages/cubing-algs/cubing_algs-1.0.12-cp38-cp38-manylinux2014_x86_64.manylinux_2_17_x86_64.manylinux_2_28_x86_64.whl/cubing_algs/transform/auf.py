from collections.abc import Iterable
from itertools import takewhile

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import AUF_CHAR
from cubing_algs.move import Move
from cubing_algs.transform.offset import offset_y2_moves
from cubing_algs.transform.offset import offset_y_moves
from cubing_algs.transform.offset import offset_yprime_moves
from cubing_algs.transform.trim import trim_moves

OFFSET_MAP = {
    1: offset_y_moves,
    2: offset_y2_moves,
    3: offset_yprime_moves,
}


def get_move_score(move: Move) -> int:
    """
    Calculate the numeric score for a move for AUF calculations.
    """
    if move.is_double:
        return 2
    if move.is_counter_clockwise:
        return -1
    if move.is_clockwise:
        return 1
    return 0


def is_auf_or_pause(move: Move) -> bool:
    """
    Check if a move is an AUF move or pause.
    """
    return move.base_move == AUF_CHAR or move.is_pause


def calculate_auf_score(moves: Iterable[Move]) -> int:
    """
    Calculate the total AUF score for a sequence of moves.
    """
    return sum(
        get_move_score(move)
        for move in takewhile(is_auf_or_pause, moves)
    )


def remove_auf_moves(old_moves: Algorithm) -> Algorithm:
    """
    Remove AUF (Adjust Upper Face) moves from an algorithm.
    """
    if not old_moves:
        return old_moves

    score = (
        calculate_auf_score(old_moves) +
        calculate_auf_score(list(reversed(old_moves)))
    ) % 4

    transforms = [trim_moves(AUF_CHAR)]
    if score:
        transforms.insert(0, OFFSET_MAP[score])

    return old_moves.transform(*transforms)
