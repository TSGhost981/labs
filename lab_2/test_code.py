import unittest
from unittest.mock import patch, Mock
from code import is_valid_card_number, user_input_mode, file_input_mode, web_input_mode


class TestCode(unittest.TestCase):
    def test_is_valid_card_number(self):
        result, message = is_valid_card_number('4111111111111111')
        self.assertTrue(result)

    def test_is_invalid_card_number(self):
        result, message = is_valid_card_number('412345')
        self.assertFalse(result)

    def test_user_input_mode(self):
        mock_input = Mock()
        mock_input.side_effect = ['4111111111111111', 'quit']
        with patch('builtins.input', mock_input):
            result = user_input_mode()
        self.assertEqual(result[0], '4111 1111 1111 1111')

    def test_file_input_mode(self):
        mock_input = Mock()
        mock_input.return_value = 'checker.txt'
        with patch('builtins.input', mock_input):
            result = file_input_mode()
        self.assertEqual(result, ['4111 1111 1111 1111',
                                  '5555 5555 5555 4444',
                                  '5111 1111 1111 1118'])

    def test_web_input_mode(self):
        mock_input = Mock()
        mock_input.return_value = 'https://www.freeformatter.com/credit-card-number-generator-validator.html'
        with patch('builtins.input', mock_input):
            result = web_input_mode()
        self.assertEqual(result, ['2485 7080 3024 1382',
                                  '2485 7080 3024 1382'])
