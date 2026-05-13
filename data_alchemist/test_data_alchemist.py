import unittest
import os
import pandas as pd
from unittest.mock import patch
from data_alchemist import generate_sample_data, get_schema, query_ollama, extract_python_code

class TestDataAlchemist(unittest.TestCase):

    def setUp(self):
        self.test_file = "test_sample_data.csv"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_generate_sample_data(self):
        file_path = generate_sample_data(self.test_file)
        self.assertTrue(os.path.exists(file_path))

        df = pd.read_csv(file_path)
        self.assertEqual(len(df), 100)
        self.assertIn('order_id', df.columns)

    def test_get_schema(self):
        generate_sample_data(self.test_file)
        df = pd.read_csv(self.test_file)
        schema = get_schema(df)
        self.assertIn("Column 'order_id'", schema)
        self.assertIn("Column 'product_category'", schema)

    @patch('data_alchemist.requests.post')
    def test_query_ollama_mock_fallback(self, mock_post):
        # Simulate connection error
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        response = query_ollama("Please propose a question")
        self.assertIn("1. What is the total revenue by product category?", response)

    def test_extract_python_code(self):
        markdown_text = "Here is the code:\n```python\nprint('hello')\n```\nEnjoy!"
        code = extract_python_code(markdown_text)
        self.assertEqual(code, "print('hello')")

if __name__ == '__main__':
    unittest.main()
