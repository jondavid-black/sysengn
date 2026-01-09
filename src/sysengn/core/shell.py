import os
import pty
import select
import subprocess
import threading
from typing import Callable


class ShellManager:
    """Manages a persistent shell session using a pseudo-terminal (pty).

    Allows sending commands to a running shell process and receiving output
    asynchronously via a callback. Main state (like current directory) is
    preserved between commands because the same shell process is used.
    """

    def __init__(
        self, on_output: Callable[[str], None], shell_cmd: list[str] | None = None
    ) -> None:
        """Initializes the shell manager.

        Args:
            on_output: Callback function to handle stdout/stderr output.
            shell_cmd: Command to start the shell. Defaults to ["/bin/bash"].
        """
        self.on_output = on_output
        self.shell_cmd = shell_cmd or ["/bin/bash"]
        self.running = False
        self._thread: threading.Thread | None = None
        self.master_fd: int | None = None
        self.process: subprocess.Popen | None = None

        self._start_process()

    def _start_process(self) -> None:
        """Starts the shell process with a pty."""
        # Create a new pseudo-terminal pair
        self.master_fd, slave_fd = pty.openpty()

        try:
            # Start the shell process
            # stdin, stdout, and stderr are all connected to the slave end of the pty
            self.process = subprocess.Popen(
                self.shell_cmd,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                preexec_fn=os.setsid,  # Start in a new session
                close_fds=True,
                text=False,  # operate on bytes
                bufsize=0,  # unbuffered
            )
            self.running = True

            # Start the reading thread
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()

        finally:
            # The parent process doesn't need the slave fd
            os.close(slave_fd)

    def write(self, command: str) -> None:
        """Sends a command to the shell.

        Args:
            command: The command string to execute.
        """
        if not self.running or self.master_fd is None:
            return

        try:
            os.write(self.master_fd, command.encode("utf-8"))
        except OSError as e:
            # Handle case where writing fails (e.g. process died)
            self.on_output(f"\nError writing to shell: {e}\n")
            self.close()

    def _read_loop(self) -> None:
        """Background loop to read output from the master fd."""
        if self.master_fd is None:
            return

        while self.running and self.master_fd is not None:
            try:
                # Wait for data to be available to read (timeout 0.1s to allow checking self.running)
                r, _, _ = select.select([self.master_fd], [], [], 0.1)

                if self.master_fd in r:
                    # Read data from the master fd
                    data = os.read(self.master_fd, 10240)
                    if not data:
                        break  # EOF

                    # Decode and send to callback
                    # Using errors='replace' to handle partial multibyte characters gracefully if needed
                    # (though a robust solution might need a streaming decoder)
                    text = data.decode("utf-8", errors="replace")
                    self.on_output(text)

            except OSError:
                # EIO is raised on Linux when the slave side closes (shell exits)
                break
            except Exception as e:
                self.on_output(f"\nShell read error: {e}\n")
                break

        self.running = False

    def close(self) -> None:
        """Terminates the shell session and cleans up resources."""
        self.running = False

        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None

        if self._thread and self._thread.is_alive():
            # Thread should exit on its own since running is False and master_fd is closed
            self._thread.join(timeout=0.5)
