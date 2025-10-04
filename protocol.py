# protocol.py
from __future__ import annotations
import socket
import struct
from typing import Tuple, Any
from serialization import Format, serialize, deserialize


_HEADER_STRUCT = struct.Struct("!BI")  # 1 byte fmt + 4 bytes payload length (big-endian)


def send_object(sock: socket.socket, obj: Any, fmt: Format) -> None:
    payload = serialize(obj, fmt)
    header = _HEADER_STRUCT.pack(int(fmt), len(payload))
    sock.sendall(header + payload)


def recv_object(sock: socket.socket) -> Tuple[Format, Any]:
    header = _recv_exact(sock, _HEADER_STRUCT.size)
    if not header:
        raise ConnectionError("No header received")
    fmt_val, length = _HEADER_STRUCT.unpack(header)
    payload = _recv_exact(sock, length)
    if payload is None:
        raise ConnectionError("Incomplete payload")
    fmt = Format(fmt_val)
    obj = deserialize(payload, fmt)
    return fmt, obj


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    chunks = []
    remaining = n
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            return b"".join(chunks) if chunks else None
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)

