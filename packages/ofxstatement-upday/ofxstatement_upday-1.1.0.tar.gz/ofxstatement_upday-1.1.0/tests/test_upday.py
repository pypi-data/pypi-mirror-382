import unittest
from unittest.mock import patch, MagicMock
from ofxstatement_upday.upday import UpDayPlugin, UpDayParser, _get_start_date_from_user


class TestUpDayPlugin(unittest.TestCase):
    def test_plugin_creation(self):
        """Test che il plugin si crei correttamente"""
        plugin = UpDayPlugin(None, {})
        self.assertIsInstance(plugin, UpDayPlugin)

    def test_get_parser(self):
        """Test che il plugin restituisca il parser corretto"""
        plugin = UpDayPlugin(None, {})
        parser = plugin.get_parser("dummy_filename")
        self.assertIsInstance(parser, UpDayParser)


class TestUpDayParser(unittest.TestCase):
    def setUp(self):
        self.parser = UpDayParser("dummy_filename")

    def test_parser_initialization(self):
        """Test inizializzazione del parser"""
        self.assertEqual(self.parser.filename, "dummy_filename")
        self.assertEqual(self.parser.transactions_data, [])

    @patch('builtins.input', return_value='01/01/2024')
    def test_get_start_date_from_user(self, mock_input):
        """Test parsing della data utente"""
        date = _get_start_date_from_user()
        self.assertEqual(date, "01/01/2024")

    @patch('builtins.input', side_effect=['invalid_date', '1/1/24'])
    @patch('builtins.print')
    def test_get_start_date_invalid_then_valid(self, mock_print, mock_input):
        """Test gestione data invalida seguita da data valida"""
        date = _get_start_date_from_user()
        self.assertEqual(date, "01/01/2024")
        mock_print.assert_called()

    def test_get_scraped_data(self):
        """Test che get_scraped_data restituisca i dati corretti"""
        test_data = [{'page': 1, 'html': '<table>test</table>'}]
        self.parser.transactions_data = test_data
        result = self.parser.get_scraped_data()
        self.assertEqual(result, test_data)


if __name__ == '__main__':
    unittest.main()
