from paramiko import SFTPClient, SSHClient, AutoAddPolicy
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_HOSTNAME: str | None = None
_USERNAME: str | None = None
_PASSWORD: str | None = None
_PORT: int = 22


def set_sftp_credentials(
    hostname: str, username: str, password: str, port: int = 22
) -> None:
    global _HOSTNAME, _USERNAME, _PASSWORD, _PORT
    _HOSTNAME = hostname
    _USERNAME = username
    _PASSWORD = password
    _PORT = port


def check_credentials() -> bool:
    return _HOSTNAME is None or _USERNAME is None or _PASSWORD is None


def open_ssh_connection() -> SSHClient:
    if check_credentials():
        logger.warning("Credentials not provided for SFTP connection.")
        raise RuntimeError(
            "Credentials not provided. Please run set_sftp_credentials() and provide hostname, username, password, and port"
        )
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(
        hostname=_HOSTNAME, username=_USERNAME, password=_PASSWORD, port=_PORT
    )
    return client


def open_sftp_connection(ssh_client) -> SFTPClient:
    logger.debug("SFTP CONNECTED")
    return ssh_client.open_sftp()


def send_files(files_to_send: dict) -> None:
    ssh_client = open_ssh_connection()
    sftp_conn = open_sftp_connection(ssh_client)
    for local_file, remote_file in files_to_send.items():
        if Path(local_file).exists():
            sftp_conn.put(local_file, remote_file)
        else:
            logger.warning(f"File {local_file} does not exist")
    close_connections(ssh_client, sftp_conn)


def close_connections(ssh_client: SSHClient, sftp_client: SFTPClient) -> None:
    sftp_client.close()
    ssh_client.close()
    logger.debug("SFTP CLOSED")
