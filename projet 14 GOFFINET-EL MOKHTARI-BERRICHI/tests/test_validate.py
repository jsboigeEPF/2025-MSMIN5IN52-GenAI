import unittest
from unittest.mock import patch, mock_open
import json
import sys
import os
from jsonschema import ValidationError
from pathlib import Path

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.utils.validate import load_schema, validate_data

class TestValidationFunctions(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='{"schema": "content"}')
    def test_load_schema(self, mock_file):
        result = load_schema('cv')
        self.assertEqual(result, {"schema": "content"})

        # Convert to Path pour matcher l'appel réel
        expected_path = Path(__file__).parent.parent / 'src' / 'schemas' / 'cv.schema.json'
        mock_file.assert_called_once_with(expected_path, 'r')

    @patch('src.utils.validate.validate')
    def test_validate_data_success(self, mock_validate):
        mock_validate.return_value = None  # No exception means success
        result = validate_data({"key": "value"}, "cv")
        self.assertTrue(result)

    @patch('src.utils.validate.validate', side_effect=ValidationError("Invalid"))
    def test_validate_data_failure(self, mock_validate):
        result = validate_data({"key": "value"}, "cv")
        self.assertFalse(result)

    @patch('src.utils.validate.load_schema', side_effect=FileNotFoundError("Schema not found"))
    def test_validate_data_schema_not_found(self, mock_load_schema):
        result = validate_data({"key": "value"}, "nonexistent")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()

def test_validate_cv_with_sample():
    """Test CV validation with sample data"""
    with open('samples/cv.json') as f:
        data = json.load(f)
    result = validate_data(data, 'cv')
    assert result is True

def test_validate_invoice_with_sample():
    """Test invoice validation with sample data"""
    with open('samples/invoice.json') as f:
        data = json.load(f)
    result = validate_data(data, 'invoice')
    assert result is True

def test_validate_report_with_sample():
    """Test report validation with sample data"""
    with open('samples/report.json') as f:
        data = json.load(f)
    result = validate_data(data, 'report')
    assert result is True