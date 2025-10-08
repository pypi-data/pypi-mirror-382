from dkany.data_hosts.sftp import SftpClient

def test_akamai_sftp_client():
    _ = SftpClient(
        host = "example.com",
        username = "sshacs",
    )
