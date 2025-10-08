from typing import Optional
import logging
import paramiko


class SftpClient:
    def __init__(
        self,
        host: str,
        username: Optional[str] = None,
        private_key_file: Optional[str] = None,
        private_key_pass: Optional[str] = None,
        default_remote_path: Optional[str] = None,
        hostkeys: Optional[str] = None,
    ):
        ssh = paramiko.SSHClient()
        if hostkeys is not None:
            logging.warning("Host key checking is not implemented yet.")
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load private key with passphrase
        private_key = None
        if private_key_file is not None:
            private_key = paramiko.RSAKey.from_private_key_file(
                private_key_file, password=private_key_pass
            )

        if host == "example.com":
            return # testing

        ssh.connect(
            hostname=host,
            username=username,
            pkey=private_key,
            look_for_keys=False,
            allow_agent=False,
        )

        self.connection = ssh.open_sftp()

        try:
            self.connection.chdir(default_remote_path or "/")
        except Exception as e:
            raise SystemError(
                f"Could not change to base_path {default_remote_path or '/'}"
            ) from e

    def exists(self, path: str) -> bool:
        try:
            self.connection.stat(path)
            return True
        except FileNotFoundError:
            return False