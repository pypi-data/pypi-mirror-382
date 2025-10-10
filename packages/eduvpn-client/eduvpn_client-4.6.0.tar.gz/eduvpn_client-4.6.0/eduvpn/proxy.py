from contextlib import closing
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, socket
from typing import List
from urllib.parse import urlparse

from eduvpn.utils import handle_exception


def find_free_udp_port():
    with closing(socket(AF_INET, SOCK_DGRAM)) as s:
        s.bind(("", 0))
        port = s.getsockname()[1]
        return port


def find_free_tcp_port():
    with closing(socket(AF_INET, SOCK_STREAM)) as s:
        s.bind(("", 0))
        port = s.getsockname()[1]
        return port


class Proxy:
    """The class that represents a proxyguard instance
    :param: common: The common library
    :param: peer: str: The remote peer string
    :param: listen: str: The listen proxy string
    """

    def __init__(
        self,
        common,
        endpoint,
    ):
        self.common = common
        self.endpoint = endpoint
        self.wrapper = None
        self._cached_source_port = None
        self._cached_listen_port = None

    def forward_exception(self, error):
        handle_exception(self.common, error)

    def tunnel(self, wgport):
        self.wrapper.tunnel(wgport)

    def restart(self):
        self.wrapper.restart()

    @property
    def source_port(self) -> int:
        if self._cached_source_port is None:
            self._cached_source_port = find_free_tcp_port()
        return self._cached_source_port

    @property
    def listen_port(self) -> int:
        if self._cached_listen_port is None:
            self._cached_listen_port = find_free_udp_port()
        return self._cached_listen_port

    @property
    def peer_ips(self) -> List[str]:
        return self.wrapper.peer_ips

    @property
    def peer_scheme(self) -> str:
        try:
            parsed = urlparse(self.endpoint)
            return parsed.scheme
        except Exception:
            return ""

    @property
    def peer_port(self):
        if self.peer_scheme == "http":
            return 80
        return 443
