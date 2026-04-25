import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from ollama_cli_agent.client import OllamaClient
from ollama_cli_agent.executor import CommandExecutor
from ollama_cli_agent.agent import ReActAgent

class TestCommandExecutor(unittest.TestCase):
    def test_basic_command(self):
        executor = CommandExecutor()
        output = executor.execute("echo 'hello world'")
        self.assertIn("hello world", output)

    def test_cd_command(self):
        executor = CommandExecutor()
        output = executor.execute("cd /tmp")
        self.assertIn("Changed directory to /tmp", output)
        self.assertEqual(executor.cwd, "/tmp")


class TestReActAgent(unittest.TestCase):

    @patch('ollama_cli_agent.agent.OllamaClient.chat')
    @patch('ollama_cli_agent.agent.console')
    def test_execute_turn(self, mock_console, mock_chat):
        # Mock the API response to return a thinking and execute block
        mock_chat.return_value = """
        <THINK>I need to check the files.</THINK>
        <EXECUTE>ls -la</EXECUTE>
        """

        agent = ReActAgent()
        agent.add_user_message("What files are here?")

        # Run one turn
        should_continue = agent.run_turn()

        # It should continue because it executed a command, not an answer
        self.assertTrue(should_continue)

        # Verify it added the command output to the messages
        last_message = agent.messages[-1]
        self.assertEqual(last_message["role"], "user")
        self.assertIn("Command Output", last_message["content"])

    @patch('ollama_cli_agent.agent.OllamaClient.chat')
    @patch('ollama_cli_agent.agent.console')
    def test_answer_turn(self, mock_console, mock_chat):
        # Mock the API response to return a final answer
        mock_chat.return_value = """
        <THINK>I have the answer now.</THINK>
        <ANSWER>There are 5 files.</ANSWER>
        """

        agent = ReActAgent()
        agent.add_user_message("How many files?")

        # Run one turn
        should_continue = agent.run_turn()

        # It should stop because it gave an answer
        self.assertFalse(should_continue)

    @patch('ollama_cli_agent.agent.OllamaClient.chat')
    @patch('ollama_cli_agent.agent.console')
    def test_malformed_turn(self, mock_console, mock_chat):
        # Mock the API response to return bad formatting
        mock_chat.return_value = "Just regular text with no tags."

        agent = ReActAgent()
        agent.add_user_message("Do something.")

        should_continue = agent.run_turn()

        # Should continue to give the agent a chance to fix it
        self.assertTrue(should_continue)

        # Verify the warning message was appended
        last_message = agent.messages[-1]
        self.assertEqual(last_message["role"], "user")
        self.assertIn("Your previous response was malformed", last_message["content"])

if __name__ == '__main__':
    unittest.main()
