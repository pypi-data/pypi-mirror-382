import requests


def download_file(
    url_string: str,
    destination_file: str,
    connection_timeout: int = 5000,
    read_timeout: int = 30000,
) -> None:
    """
    从给定的URL下载文件到本地文件系统

    Args:
        url_string: 要下载的文件的URL字符串
        destination_file: 下载后的本地文件路径
        connection_timeout: 连接超时时间(毫秒)
        read_timeout: 读取超时时间(毫秒)

    Raises:
        IOError: 如果发生IO错误
    """
    try:
        response = requests.get(
            url_string,
            stream=True,
            timeout=(connection_timeout / 1000, read_timeout / 1000),
        )
        response.raise_for_status()

        with open(destination_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    except requests.exceptions.RequestException as e:
        raise IOError("SnailJob download script failed") from e
