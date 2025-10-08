from jsoncfg.functions import ConfigWithWrapper


class FileConfigTcpListenTunnel:
    def __init__(self, cfg: ConfigWithWrapper, node):
        self._cfg = cfg
        self._node = node

    @property
    def tunnelName(self) -> str:
        return self._node["tunnelName"]

    @property
    def listenPort(self) -> int:
        with self._cfg:
            return self._node["listenPort"]

    @property
    def listenBindAddress(self) -> str:
        with self._cfg:
            return self._node["listenBindAddress"]
