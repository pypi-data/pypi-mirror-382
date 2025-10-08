import ctypes
import json
from typing import List, Dict, Optional, Tuple, Any, Union
from ipfs_tk_generics.tunnels import SenderTunnel, ListenerTunnel, TunnelsList, BaseTunnels
from libkubo import libkubo, c_str, from_c_str, ffi, c_bool





class NodeTunnels(BaseTunnels):
    """
    Provides P2P stream mounting functionality for IPFS nodes.

    Stream mounting allows you to expose local TCP services to the libp2p network
    and connect to remote TCP services exposed by other nodes.
    """

    def __init__(self, node):
        self._node = node
        self._repo_path = self._node._repo_path
        BaseTunnels.__init__(self)


    def _enable_p2p(self) -> bool:
        """Enable p2p functionality in the IPFS configuration."""

        repo_path = c_str(self._repo_path.encode('utf-8'))
        result = libkubo.P2PEnable(repo_path)

        if result <= 0:
            print(f"Warning: Could not enable p2p functionality ({result})")
            return False
        return True

    def open_sender(self, name: str, listen_addr: int | str, target_peer_id: str):
        """
        Forward local connections to a remote peer.

        This creates a new listener that forwards connections to the specified
        peer over the libp2p network.

        Args:
            name: The protocol name to use for the forwarding.
            listen_addr: The local address to listen on (e.g. "127.0.0.1:8080").
            target_peer_id: The peer ID to forward connections to.

        Returns:
            bool: True if the forwarding was set up successfully, False otherwise.
        """
        # if not target_peer_id.startswith("/p2p/"):
        #     target_peer_id = f"/p2p/{target_peer_id}"
        result = libkubo.P2PForward(
            c_str(self._repo_path.encode('utf-8')),
            c_str(name.encode('utf-8')),
            c_str(self._port_to_addr(listen_addr).encode('utf-8')),
            c_str(target_peer_id.encode('utf-8'))
        )
        if result > 0:
            return
        if result == -2:
            print(f"Can't create sender {name} {listen_addr} {target_peer_id}")
            raise Exception("IpfsNode.tunnels.open_sender: failed to open sender: bind: address already in use")
            
        
        raise Exception("IpfsNode.tunnels.open_sender: failed to open sender")

    def open_listener(self, name: str, target_addr: int | str):
        """
        Listen for libp2p connections and forward them to a local TCP service.

        This exposes a local TCP service to the libp2p network.

        Args:
            name: The protocol name to use for the listener.
            target_addr: The local address to forward connections to (e.g. "127.0.0.1:8080").

        Returns:
            bool: True if the listener was set up successfully, False otherwise.
        """
        result = libkubo.P2PListen(
            c_str(self._repo_path.encode('utf-8')),
            c_str(name.encode('utf-8')),
            c_str(self._port_to_addr(target_addr)))
        if result > 0:
            return
        if result == -2:
            print(f"Can't open listener {name} {target_addr}")
            raise Exception("IpfsNode.tunnels.open_sender: failed to open listener")
            
        
        raise Exception("IpfsNode.tunnels.open_sender: failed to open listener")

    def close_sender(self, name: str = None, port: int = None, peer_id: str = None) -> int:
        """
        Close a specific TCP forwarding connection, optionally filtered by protocol, port, or peer ID.

        Args:
            name: Optional protocol filter
            port: Optional port filter
            peer_id: Optional peer ID filter

        Returns:
            int: Number of forwarding connections closed
        """
        if peer_id and not peer_id.startswith("/p2p/"):
            peer_id = f"/p2p/{peer_id}"
        return self.close_tcp_connections(name, port, peer_id, senders=True, listeners=False)

    def close_listener(self, name: str = None, port: int = None) -> int:
        """
        Close a specific TCP listening connection, optionally filtered by protocol name or port.

        Args:
            name: Optional protocol name filter
            port: Optional port filter

        Returns:
            int: Number of listening connections closed
        """
        return self.close_tcp_connections(name, target_addr=port, listeners=True, senders=False)

    def close_streams(self, name: str, port: int | None = None, target_peer_id: str = "") -> bool:
        """
        Close a P2P listener or stream.

        Args:
            name: The protocol name of the listener or stream to close.
            listen_addr: For streams, the local address that the stream listens on.
            target_peer_id: For streams, the peer ID that the stream connects to.

        Returns:
            bool: True if the listener or stream was closed successfully, False otherwise.
        """
        result = libkubo.P2PClose(
            c_str(self._repo_path.encode('utf-8')),
            c_str(name.encode('utf-8')),
            c_str(self._port_to_addr(port)) if port else c_str(""),
            c_str(target_peer_id.encode('utf-8'))
        )
        return result > 0

    def close_tcp_connections(
        self,
        name: str = "", listen_addr: str | int | None = None, target_addr: str | int | None = None, all: bool = False,
        listeners: bool = True, senders: bool = True
    ) -> int:
        """
        Close specific TCP p2p connections, optionally filtered by protocol name, port, or peer ID.

        Args:
            name: Optional protocol name filter
            port: Optional port filter
            peer_id: Optional peer ID filter

        Returns:
            int: Number of connections closed
        """

        repo_path = c_str(self._repo_path.encode('utf-8'))

        result = libkubo.P2PClose(
            repo_path, c_str(name),
            c_str(self._port_to_addr(listen_addr)),
            c_str(self._port_to_addr(target_addr)),
            c_bool(all), c_bool(listeners), c_bool(senders)
        )
        return result

    def close_all_senders(self) -> int:
        """
        Close all TCP forwarding connections.

        Returns:
            int: Number of forwarding connections closed
        """
        return self.close_tcp_connections(all=True, listeners=False, senders=True)

    def close_all_listeners(self) -> int:
        """
        Close all TCP listening connections.

        Returns:
            int: Number of listening connections closed
        """
        return self.close_tcp_connections(all=True, listeners=True, senders=False)
    def close_all(self) -> int:
        """
        Close all TCP connections.

        Returns:
            int: Number of listening connections closed
        """
        return self.close_tcp_connections(all=True, listeners=True, senders=True)

    def get_tunnels(self) ->TunnelsList:
        """
        List all active P2P tunnels.
        """
        result_ptr = libkubo.P2PListListeners(
            c_str(self._repo_path.encode('utf-8'))
        )

        if not result_ptr:
            return [], []

        # Convert the C string to a Python string and release memory
        result_str = from_c_str(result_ptr)
        # libkubo.free(result_ptr)

        if not result_str:
            return [], []

        # Parse the JSON
        try:
            result = json.loads(result_str)
        except json.JSONDecodeError:
            return [], []

        # Add local listeners
        listeners = []
        for item in result.get('Listens', []):
            listener = ListenerTunnel(
                name=item.get('Protocol', ''),
                # listen_address=item.get('ListenAddress', ''),
                target_address=item.get('TargetAddress', '')
            )
            listeners.append(listener)

        # Add remote listeners
        forwarders = []
        for item in result.get('Forwards', []):
            listener = SenderTunnel(
                name=item.get('Protocol', ''),
                listen_address=item.get('ListenAddress', ''),
                target_address=item.get('TargetAddress', '')
            )
            forwarders.append(listener)

        # # Extract active streams
        # streams = []
        # for item in result.get('Streams', []):
        #     stream = P2PStream(
        #         name=item.get('Protocol', ''),
        #         origin_address=item.get('LocalAddr', ''),
        #         target_address=item.get('RemoteAddr', '')
        #     )
        #     streams.append(stream)

        return TunnelsList(senders=forwarders, listeners=listeners)


    def _port_to_addr(self, addr: int | str | None) -> str:
        if not addr:
            return ""
        if isinstance(addr, int):
            return f"/ip4/{self._node._ipfs_host_ip()}/tcp/{addr}"
        else:
            return addr
    def terminate(self):
        pass
    def __del__(self):
        self.terminate()