import shlex
import subprocess  # nosec
from dataclasses import dataclass

TIMEOUT_EXIT_CODE = 255


@dataclass
class ShellResult:
    """Result of shell command execution.

    Args:
        stdout: Standard output from the command
        stderr: Standard error from the command
        code: Exit code of the command
    """

    stdout: str
    stderr: str
    code: int

    @property
    def combined_output(self) -> str:
        """Combined stdout and stderr output."""
        result = ""
        if self.stdout:
            result += self.stdout
        if self.stderr:
            if result:
                result += "\n"
            result += self.stderr
        return result


def shell(cmd: str, timeout: int | None = 60, capture_output: bool = True, echo_command: bool = False) -> ShellResult:
    """Execute a shell command.

    Args:
        cmd: Command to execute
        timeout: Timeout in seconds, None for no timeout
        capture_output: Whether to capture stdout/stderr
        echo_command: Whether to print the command before execution

    Returns:
        ShellResult with stdout, stderr and exit code
    """
    if echo_command:
        print(cmd)  # noqa: T201
    try:
        process = subprocess.run(cmd, timeout=timeout, capture_output=capture_output, shell=True, check=False)  # noqa: S602 # nosec
        stdout = process.stdout.decode("utf-8", errors="replace") if capture_output else ""
        stderr = process.stderr.decode("utf-8", errors="replace") if capture_output else ""
        return ShellResult(stdout=stdout, stderr=stderr, code=process.returncode)
    except subprocess.TimeoutExpired:
        return ShellResult(stdout="", stderr="timeout", code=TIMEOUT_EXIT_CODE)


def ssh_shell(host: str, cmd: str, ssh_key_path: str | None = None, timeout: int = 60, echo_command: bool = False) -> ShellResult:
    """Execute a command on remote host via SSH.

    Args:
        host: Remote host to connect to
        cmd: Command to execute on remote host
        ssh_key_path: Path to SSH private key file
        timeout: Timeout in seconds
        echo_command: Whether to print the command before execution

    Returns:
        ShellResult with stdout, stderr and exit code
    """
    ssh_cmd = "ssh -o 'StrictHostKeyChecking=no' -o 'LogLevel=ERROR'"
    if ssh_key_path:
        ssh_cmd += f" -i {shlex.quote(ssh_key_path)}"
    ssh_cmd += f" {shlex.quote(host)} {shlex.quote(cmd)}"
    return shell(ssh_cmd, timeout=timeout, echo_command=echo_command)
