import unittest
from unittest.mock import patch

from cubing_algs.commutator_conjugate import expand_commutators_and_conjugates
from cubing_algs.commutator_conjugate import find_innermost_brackets
from cubing_algs.commutator_conjugate import invert_moves
from cubing_algs.commutator_conjugate import split_on_separator
from cubing_algs.exceptions import InvalidBracketError
from cubing_algs.exceptions import InvalidOperatorError


class TestFindInnermostBrackets(unittest.TestCase):

    def test_no_brackets(self) -> None:
        """Should return None when no brackets are present"""
        self.assertIsNone(find_innermost_brackets("R U R' U'"))

    def test_single_level_brackets(self) -> None:
        """Should find brackets at depth 1"""
        result = find_innermost_brackets("[R U R']")
        self.assertEqual(result, (0, 7))

    def test_nested_brackets(self) -> None:
        """Should find the deepest nested brackets"""
        result = find_innermost_brackets('[[R U], D]')
        self.assertEqual(result, (1, 5))  # Inner brackets [R U]

    def test_multiple_nested_brackets(self) -> None:
        """Should find first occurrence of deepest brackets"""
        result = find_innermost_brackets('[[R U], [D F]]')
        self.assertEqual(result, (1, 5))  # First inner brackets [R U]

    def test_complex_nesting(self) -> None:
        """Should handle complex nested structures"""
        result = find_innermost_brackets('[A [B [C D] E] F]')
        self.assertEqual(result, (6, 10))  # Innermost [C D]

    def test_empty_brackets(self) -> None:
        """Should handle empty brackets"""
        result = find_innermost_brackets('[]')
        self.assertEqual(result, (0, 1))

    def test_malformed_brackets_opening_only(self) -> None:
        """Should return None for malformed brackets (opening only)"""
        self.assertIsNone(find_innermost_brackets('[R U'))

    def test_malformed_brackets_closing_only(self) -> None:
        """Should return None for malformed brackets (closing only)"""
        self.assertIsNone(find_innermost_brackets('R U]'))


class TestSplitOnSeparator(unittest.TestCase):

    def test_no_separator(self) -> None:
        """Should return None when separator is not found"""
        self.assertIsNone(split_on_separator("R U R'", ','))

    def test_top_level_comma(self) -> None:
        """Should split on comma at top level"""
        result = split_on_separator('R U, D F', ',')
        self.assertEqual(result, ('R U', ' D F'))

    def test_top_level_colon(self) -> None:
        """Should split on colon at top level"""
        result = split_on_separator('R U: D F', ':')
        self.assertEqual(result, ('R U', ' D F'))

    def test_separator_inside_brackets(self) -> None:
        """Should not split on separator inside brackets"""
        self.assertIsNone(split_on_separator('R [U, D] F', ','))

    def test_nested_brackets_with_separator(self) -> None:
        """Should handle nested brackets with separator inside"""
        self.assertIsNone(split_on_separator('[[R, U], D]', ','))

    def test_multiple_separators_top_level(self) -> None:
        """Should split on first occurrence at top level"""
        result = split_on_separator('A, B, C', ',')
        self.assertEqual(result, ('A', ' B, C'))

    def test_separator_at_beginning(self) -> None:
        """Should handle separator at beginning"""
        result = split_on_separator(',R U', ',')
        self.assertEqual(result, ('', 'R U'))

    def test_separator_at_end(self) -> None:
        """Should handle separator at end"""
        result = split_on_separator('R U,', ',')
        self.assertEqual(result, ('R U', ''))


class TestInvertMoves(unittest.TestCase):

    def test_invert_moves(self) -> None:
        """
        Should create algorithm, transform with mirror_moves,
        and return string
        """
        result = invert_moves("R U R' U'")
        self.assertEqual(result, "U R U' R'")
        self.assertIsInstance(result, str)


class TestExpandCommutatorsAndConjugates(unittest.TestCase):

    def test_simple_commutator(self) -> None:
        """Should expand simple commutator [A, B] to A B A' B'"""
        result = expand_commutators_and_conjugates('[R U, D F]')
        expected = "R U D F U' R' F' D'"
        self.assertEqual(result.strip(), expected)

    def test_simple_conjugate(self) -> None:
        """Should expand simple conjugate [A: B] to A B A'"""
        result = expand_commutators_and_conjugates('[R: U]')
        expected = "R U R'"
        self.assertEqual(result.strip(), expected)

    def test_nested_commutator(self) -> None:
        """Should handle nested commutators"""
        result = expand_commutators_and_conjugates('[[R, U], D]')
        # Inner commutator [R, U] expands to "R U R' U'"
        # Then outer commutator with D
        self.assertEqual("R U R' U' D U R U' R' D'", result)

    def test_no_brackets(self) -> None:
        """Should return unchanged string when no brackets"""
        result = expand_commutators_and_conjugates("R U R' U'")
        self.assertEqual(result, "R U R' U'")

    def test_malformed_bracket_raises_error(self) -> None:
        """Should raise InvalidBracketError for malformed brackets"""
        with self.assertRaises(InvalidBracketError) as context:
            expand_commutators_and_conjugates("[R U R'")
        self.assertIn('Malformed bracket', str(context.exception))

    def test_invalid_operator_raises_error(self) -> None:
        """Should raise InvalidOperatorError for invalid operators"""
        with self.assertRaises(InvalidOperatorError) as context:
            expand_commutators_and_conjugates('[R U | D F]')
        self.assertIn('Invalid operator', str(context.exception))

    def test_empty_bracket_parts(self) -> None:
        """Should handle empty bracket parts"""
        result = expand_commutators_and_conjugates('[, D]')
        expected = "D  D'"
        self.assertEqual(result.strip(), expected)

    def test_multiple_brackets_same_level(self) -> None:
        """Should handle multiple brackets at same level"""
        result = expand_commutators_and_conjugates('[R, U] [D, F]')
        # Should expand both commutators
        self.assertIn("R U R' U'", result)
        self.assertIn("D F D' F'", result)

    def test_mixed_operators(self) -> None:
        """Should handle mix of commutators and conjugates"""
        result = expand_commutators_and_conjugates('[R: U] [D, F]')
        # Should have conjugate (R U R') and commutator (D F D' F')
        self.assertIn("R U R'", result)
        self.assertIn("D F D' F'", result)

    def test_recursive_expansion(self) -> None:
        """Should recursively expand nested structures"""
        # Test that recursive calls are made
        with patch(
                'cubing_algs.commutator_conjugate.expand_commutators_and_conjugates',
                wraps=expand_commutators_and_conjugates,
        ) as mock_expand:
            expand_commutators_and_conjugates('[[R, U]: D]')
            # Should make multiple recursive calls
            self.assertGreater(mock_expand.call_count, 1)


class TestEdgeCases(unittest.TestCase):

    def test_empty_string(self) -> None:
        """Should handle empty strings gracefully"""
        self.assertIsNone(find_innermost_brackets(''))
        self.assertIsNone(split_on_separator('', ','))
        self.assertEqual(expand_commutators_and_conjugates(''), '')

    def test_whitespace_handling(self) -> None:
        """Should handle whitespace in brackets"""
        result_find = find_innermost_brackets('[ R U ]')
        self.assertEqual(result_find, (0, 6))

        result_split = split_on_separator(' R U , D F ', ',')
        self.assertEqual(result_split, (' R U ', ' D F '))

    def test_single_character_moves(self) -> None:
        """Should handle single character moves"""
        result = expand_commutators_and_conjugates('[R, U]')
        expected = " R U R' U' "
        self.assertEqual(result.strip(), expected.strip())

    def test_deeply_nested_brackets(self) -> None:
        """Should handle deeply nested bracket structures"""
        nested = '[[[[[A]]]]]'
        result = find_innermost_brackets(nested)
        self.assertEqual(result, (4, 6))  # Innermost [A]
