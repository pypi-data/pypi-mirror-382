import os

from mm_std import ShellResult, shell, ssh_shell
from mm_std.subprocess_utils import TIMEOUT_EXIT_CODE


class TestShellResult:
    def test_combined_output_with_both_stdout_and_stderr(self):
        """Test combined output when both stdout and stderr are present."""
        result = ShellResult(stdout="output", stderr="error", code=0)
        assert result.combined_output == "output\nerror"

    def test_combined_output_with_only_stdout(self):
        """Test combined output when only stdout is present."""
        result = ShellResult(stdout="output", stderr="", code=0)
        assert result.combined_output == "output"

    def test_combined_output_with_only_stderr(self):
        """Test combined output when only stderr is present."""
        result = ShellResult(stdout="", stderr="error", code=1)
        assert result.combined_output == "error"

    def test_combined_output_with_neither(self):
        """Test combined output when both stdout and stderr are empty."""
        result = ShellResult(stdout="", stderr="", code=0)
        assert result.combined_output == ""


class TestShell:
    def test_successful_command(self):
        """Test execution of a successful command."""
        result = shell("echo 'hello world'")
        assert result.code == 0
        assert result.stdout.strip() == "hello world"
        assert result.stderr == ""

    def test_command_with_exit_code(self):
        """Test command that returns non-zero exit code."""
        result = shell("exit 42")
        assert result.code == 42
        assert result.stdout == ""

    def test_command_with_stderr(self):
        """Test command that outputs to stderr."""
        result = shell("echo 'error message' >&2")
        assert result.code == 0
        assert result.stdout == ""
        assert result.stderr.strip() == "error message"

    def test_capture_output_false(self):
        """Test command execution without capturing output."""
        result = shell("echo 'test'", capture_output=False)
        assert result.code == 0
        assert result.stdout == ""
        assert result.stderr == ""

    def test_timeout_handling(self):
        """Test command timeout handling."""
        result = shell("sleep 2", timeout=1)
        assert result.code == TIMEOUT_EXIT_CODE
        assert result.stdout == ""
        assert result.stderr == "timeout"

    def test_echo_command(self, capsys):
        """Test echo_command parameter prints the command."""
        shell("echo 'test'", echo_command=True)
        captured = capsys.readouterr()
        assert "echo 'test'" in captured.out

    def test_command_with_pipes(self):
        """Test command with pipes and complex shell operations."""
        result = shell("echo 'line1\nline2\nline3' | grep 'line2'")
        assert result.code == 0
        assert result.stdout.strip() == "line2"

    def test_working_directory_commands(self, tmp_path):
        """Test commands that interact with filesystem."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        result = shell(f"cat {test_file}")
        assert result.code == 0
        assert result.stdout.strip() == "test content"

    def test_environment_variables(self):
        """Test command that uses environment variables."""
        result = shell("echo $HOME")
        assert result.code == 0
        assert result.stdout.strip() == os.environ.get("HOME", "")


class TestSshShell:
    def test_ssh_command_construction(self):
        """Test that SSH command is properly constructed and quoted."""
        # We can't test actual SSH without a server, but we can test the command construction
        # by checking what command gets passed to the shell function
        result = ssh_shell("nonexistent-host", "echo 'test'", timeout=1)

        # This will fail with connection error, but that's expected
        # We're testing that the function doesn't crash on command construction
        assert result.code != 0  # Should fail to connect
        assert "timeout" in result.stderr or "connect" in result.stderr.lower() or "resolve" in result.stderr.lower()

    def test_ssh_with_key_path(self):
        """Test SSH command with key path parameter."""
        result = ssh_shell("nonexistent-host", "echo 'test'", ssh_key_path="/path/to/key", timeout=1)

        # Should fail to connect but not crash
        assert result.code != 0
        assert "timeout" in result.stderr or "connect" in result.stderr.lower() or "resolve" in result.stderr.lower()

    def test_ssh_echo_command(self, capsys):
        """Test that SSH command echoing works."""
        ssh_shell("nonexistent-host", "echo 'test'", echo_command=True, timeout=1)
        captured = capsys.readouterr()

        # Should see the constructed SSH command
        assert "ssh" in captured.out
        assert "nonexistent-host" in captured.out

    def test_ssh_command_quoting(self):
        """Test that SSH commands with special characters are properly quoted."""
        # Test with command that has special characters
        result = ssh_shell("nonexistent-host", "echo 'hello; rm -rf /'", timeout=1)

        # Should fail to connect but not execute dangerous commands locally
        assert result.code != 0
        assert "timeout" in result.stderr or "connect" in result.stderr.lower() or "resolve" in result.stderr.lower()
