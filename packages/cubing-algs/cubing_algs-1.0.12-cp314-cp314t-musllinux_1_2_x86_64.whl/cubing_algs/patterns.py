"""
Collection of cool patterns on 3x3x3

https://ruwix.com/the-rubiks-cube/rubiks-cube-patterns-algorithms/more-rubiks-patterns/
"""
from cubing_algs.algorithm import Algorithm
from cubing_algs.parsing import parse_moves

PATTERNS = {
    '3T': "B U2 L2 F2 R2 F D2 F2 R2 F' R2 U2",
    '4Crosses': 'F2 B2 R F2 B2 R F2 B2 R F2 B2 R F2 B2 R F2 B2 R',
    '4Plus2Dots': "F U2 D2 R L U' D F B R U2 R2 U2 F2 L2 U2 F2 L2 B2",
    'Anaconda': "L U B' U' R L' B R' F B' D R D' F'",
    'AreYouHigh': "L R' U2 D2 L' R U2 D2 R2 L2",
    'BlackMamba': "R D L F' R L' D R' U D' B U' R' D'",
    'CUAround': "U' B2 U L2 D L2 R2 D' B' R D' L R' B2 U2 F' L' U'",
    'Cage': "L U F2 R L' U2 B' U D B2 L F B' R' L F' R",
    'CheckerZigzag': 'R2 L2 F2 B2 U F2 B2 U2 F2 B2 U',
    'CornerPyramid': "U' D B R' F R B' L' F' B L F R' B' R F' U' D",
    'Cross': "R2 L' D F2 R' D' R' L U' D R D B2 R' U D2",
    'CrossingSnake': "R L U2 R L' U2 F2 R2 D2 B2 D2 B2 L2 D2 R2",
    'CubeInACubeInACube': "U' L' U' F' R2 B' R F U B2 U B' L U' F U R F'",
    'CubeInTheCube': "F L F U' R U F2 L2 U' L' B D' B' L2 U",
    'DontCrossLine': 'F2 L2 R2 B2 U2 D2',
    'Doubler': "R L U2 R L' D2 R2 F2 U2 F2 U2 L2 F2 U2 L2",
    'EasyCheckerboard': 'U2 D2 R2 L2 F2 B2',
    'EdgeTriangle': "U B2 U' F' U' D L' D2 L U D' F D' L2 B2 D'",
    'ExchangedChickenFeet': "F L' D' B' L F U F' D' F L2 B' R' U L2 D' F",
    'ExchangedDuckFeet': "U F R2 F' D' R U B2 U2 F' R2 F D B2 R B'",
    'ExchangedPeaks': "F U2 L F L' B L U B' R' L' U R' D' F' B R2",
    'ExchangedRings': "B' U' B' L' D B U D2 B U L D' L' U' L2 D",
    'FacingCheckerboards': 'U2 F2 U2 F2 B2 U2 F2 D2',
    'FourSpots': "F2 B2 U D' R2 L2 U D'",
    'GreenMamba': "R D R F R' F' B D R' U' B' U D2",
    'Headlights': 'U2 F2 U2 D2 B2 D2',
    'HenrysSnake': "R2 F2 U' D' B2 L2 F2 L2 U D R2 F2",
    'Hi': 'R2 L2 D2 R2 L2 U2',
    'HiAllAround': 'U2 R2 F2 U2 D2 F2 L2 U2',
    'Kilt': "U' R2 L2 F2 B2 U' R L F B' U F2 D2 R2 L2 F2 U2 F2 U' F2",
    'LooseStrap': 'F2 U2 B2 U2 F2 U2',
    'MatchingPictures': "R' D2 R L D2 L'",
    'Mirror': "U D F2 B2 U' D' R2 L2 B2",
    'OppositeCheckerboards': "U D R2 L2 U D' R2 L2 D2",
    'OppositeCorners': 'R L U2 F2 D2 F2 R L F2 D2 B2 D2',
    'OrderInChaos': "B L2 B' U2 B F2 U L U B U' R U' B F U' R D R B' U'",
    'PercentSign': "R L U2 R L' U2 F2 L2 U2 F2 U2 F2 R2 U2 R2",
    'Picnic': 'D2 R2 L2 F2 B2',
    'Pillars': 'L2 R2 B2 F2',
    'PlusMinus': 'U2 R2 L2 U2 R2 L2',
    'PlusMinusCheck': 'U D R2 L2 U D R2 L2',
    'Pyraminx': "D L' U R' B' R B U2 D B D' B' L U D'",
    'Python': "F2 R' B' U R' L F' L F' B D' R B L2",
    'QuickMaths': "R L F2 U2 R' L' F2 U2 R2 F2 U R2 L2 F2 B2 D'",
    'Quote': 'U2 F2 D2 B2 R2 U2 B2 R2 U2 R2',
    'Rockets': "U R2 F2 R2 U' D F2 R2 F2 D",
    'RonsCubeInACube': "F D' F' R D F' R' D R D L' F L D R' F D'",
    'SixSpots': "U D' R L' F B' U D'",
    'SixTwoOne': "U B2 D2 L B' L' U' L' B D2 B2",
    'Slash': 'R L F B R L F B R L F B',
    'Solved': '',
    'SpeedsolvingLogo': "R' L' U2 F2 D2 F2 R L B2 U2 B2 U2",
    'Spiral': "L' B' D U R U' R' D2 R2 D L D' L' R' F U",
    'StripeDotSolved': "D U B2 F2 D' U'",
    'Superflip': "U R2 F B R B2 R U2 L B2 R U' D' R2 F R' L B2 U2 F2",
    'Tablecloth': "R L U2 F' U2 D2 R2 L2 F' D2 F2 D R2 L2 F2 B2 D B2 L2",
    'Tetris': "L R F B U' D' L' R'",
    'TwistedChickenFeet': "F L' D F' U' B U F U' F R' F2 L U' R' D2",
    'TwistedCorners': "F U D R2 F2 U' B U B U R2 B' U L2 U B2 U2 F2 L2 U'",
    'TwistedDuckFeet': "F R' B R U F' L' F' U2 L' U' D2 B D' F B' U2",
    'TwistedPeaks': "F B' U F U F U L B L2 B' U F' L U L' B",
    'TwistedRings': "F D F' D2 L' B' U L D R U L' F' U L U2",
    'Twister': "F R' U L F' L' F U' R U L' U' L F'",
    'UnionJack': "U F B' L2 U2 L2 F' B U2 L2 U",
    'VerticalStripes': "F U F R L2 B D' R D2 L D' B R2 L F U F",
    'Wire': 'R L F B R L F B R L F B R2 B2 L2 R2 B2 L2',
    'YanYing': "L R F B U' D' L' R'",
    'YinYang': "R L B F R L U' D' F' B' U D",
    'ZZLine': "R L U2 R L' U2 F2 R2 U2 F2 D2 B2 L2 U2 L2",
}


def get_pattern(pattern_name: str) -> Algorithm:
    """
    Get an algorithm for a specific cube pattern by name.
    """
    return parse_moves(PATTERNS.get(pattern_name, ''))
