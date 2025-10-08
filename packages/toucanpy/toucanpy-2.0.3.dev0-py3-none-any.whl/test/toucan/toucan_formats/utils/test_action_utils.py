import unittest
from unittest.mock import patch

from toucan.utils.action_utils import retry_action


class TestRetryAction(unittest.TestCase):
    @patch("time.sleep", return_value=None)  # Patch sleep to avoid actual delay
    def test_success_on_first_attempt(self, mock_sleep):
        result = retry_action(lambda: "Success")
        self.assertEqual(result, "Success")
        mock_sleep.assert_not_called()  # No sleep if it succeeds on the first attempt

    @patch("time.sleep", return_value=None)
    def test_success_on_retry(self, mock_sleep):
        attempts = 0

        def flaky_action():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise ValueError("Temporary error")
            return "Recovered"

        result = retry_action(flaky_action, retry_times=3, delay=0.1)
        self.assertEqual(result, "Recovered")
        self.assertEqual(attempts, 2)  # Should succeed on the 2nd attempt
        self.assertEqual(mock_sleep.call_count, 1)  # One retry, so one sleep call

    @patch("time.sleep", return_value=None)
    def test_failure_after_all_retries(self, mock_sleep):
        attempts = 0

        def always_failing_action():
            nonlocal attempts
            attempts += 1
            raise ValueError("Persistent error")

        with self.assertRaises(Exception) as context:
            retry_action(always_failing_action, retry_times=3, delay=0.1)

        self.assertIn("Persistent error", str(context.exception))
        self.assertEqual(mock_sleep.call_count, 2)  # Retries 3 times, so sleep called 2 times
        self.assertEqual(attempts, 3)

    @patch("time.sleep", return_value=None)
    def test_custom_retry_and_delay(self, mock_sleep):
        attempts = 0

        def action_with_retries():
            nonlocal attempts
            attempts += 1
            if attempts < 4:
                raise RuntimeError("Error")
            return "Done"

        result = retry_action(action_with_retries, retry_times=4, delay=777)
        mock_sleep.assert_called_with(777)
        self.assertEqual(result, "Done")
        self.assertEqual(attempts, 4)  # Should succeed on the 4th attempt
        self.assertEqual(mock_sleep.call_count, 3)  # Three delays for 4 attempts

    @patch("time.sleep", return_value=None)
    def test_method_with_args(self, mock_sleep):
        def flaky_action(test_arg, another_test="test"):
            return f"{test_arg} {another_test}"

        result = retry_action(flaky_action, "test2", retry_times=3, delay=0.1, another_test="test3")
        self.assertEqual(result, "test2 test3")


if __name__ == "__main__":
    unittest.main()
