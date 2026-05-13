import os
import unittest
from unittest.mock import patch, MagicMock
from detective import DataDetective

class TestDataDetective(unittest.TestCase):

    def setUp(self):
        # Clean up possible generated files before tests
        self.output_dir = "data_detective/test_output"
        self.report_path = "data_detective/test_report.md"
        self.detective = DataDetective(output_dir=self.output_dir)

    def tearDown(self):
        # Cleanup
        if os.path.exists(self.report_path):
            os.remove(self.report_path)
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                os.remove(os.path.join(self.output_dir, file))
            os.rmdir(self.output_dir)
        if os.path.exists("data_detective/generated_script.py"):
            os.remove("data_detective/generated_script.py")

    @patch('detective.requests.post')
    def test_call_ollama_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "test response"}
        mock_post.return_value = mock_response

        response = self.detective._call_ollama("test prompt")
        self.assertEqual(response, "test response")

    def test_mock_response_fallback(self):
        # When Ollama is offline, it should use the mock
        self.detective.ollama_url = "http://invalid-url-that-will-fail.test"

        # Test analyze mock
        response = self.detective._call_ollama("analyze the following dataset")
        self.assertIn("```python", response)

        # Test report mock
        response = self.detective._call_ollama("compile a final report")
        self.assertIn("# Data Detective Final Report", response)

    def test_extract_python_code(self):
        response = "Here is the code:\n```python\nprint('hello')\n```\nEnjoy!"
        code = self.detective._extract_python_code(response)
        self.assertEqual(code, "print('hello')")

    def test_analyze_and_report_flow_with_mock(self):
        # Ensure it uses the mock by pointing to invalid url
        self.detective.ollama_url = "http://invalid-url-that-will-fail.test"
        csv_file = "sample_data.csv"

        # 1. Test analyze
        insights = self.detective.analyze(csv_file)
        self.assertIsNotNone(insights)
        self.assertIn("Mock Analysis Insights", insights)

        # 2. Verify plot generation
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'sales_trend.png')))

        # 3. Test report generation
        report_path = self.detective.generate_report(insights, report_path=self.report_path)
        self.assertTrue(os.path.exists(report_path))
        with open(report_path, "r") as f:
            content = f.read()
            self.assertIn("# Data Detective Final Report", content)
            self.assertIn("![Sales Trend]", content)

if __name__ == '__main__':
    unittest.main()
