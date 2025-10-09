import subprocess
import sys
from subprocess import Popen


class CredentialProvider:
    def get_credentials(self, url: str) -> tuple[str, str]:
        proc = Popen(
            ["qerent", "login", "--expose-token"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if not proc.stderr:
            raise RuntimeError("proc.stderr not available for some reason")

        if not proc.stdout:
            raise RuntimeError("proc.stdout not available for some reason")

        for stderr_line in iter(proc.stderr.readline, b""):
            line = stderr_line.decode(errors="ignore")
            sys.stdout.write(line)
            sys.stdout.flush()

        proc.wait()

        if proc.returncode != 0:
            stderr = proc.stderr.read().decode("utf-8", "ignore")

            error_msg = "Failed to get credentials: process with PID {pid} exited with code {code}".format(
                pid=proc.pid, code=proc.returncode
            )
            if stderr.strip():
                error_msg += f"; additional error message: {stderr}"

            raise RuntimeError(error_msg)

        try:
            # stdout is expected to be UTF-8 encoded text, so decoding errors are not ignored here.
            payload = proc.stdout.read().decode("utf-8").strip()
        except ValueError:
            raise RuntimeError(
                "Failed to get credentials: the Qerent CLI's output could not be decoded using UTF-8."
            )

        username = "jwt"
        password = payload

        return username, password
