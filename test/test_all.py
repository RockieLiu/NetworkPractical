# tests/test_all.py
from __future__ import annotations
import threading
import time
import socket
from typing import Any, Dict
import pytest
from serialization import serialize, deserialize, Format
from server import serve
from client import build_sample_dict, send_dict


@pytest.mark.parametrize("fmt", [Format.PICKLE, Format.JSON, Format.XML])
def test_serialize_roundtrip(fmt: Format) -> None:
    obj: Dict[str, Any] = build_sample_dict()
    data = serialize(obj, fmt)
    back = deserialize(data, fmt)
    assert back == obj


def _pick_free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.mark.parametrize("fmt", [Format.PICKLE, Format.JSON, Format.XML])
def test_client_server_once(fmt: Format, capsys: Any) -> None:
    port = _pick_free_port()

    # start server in background (handle one client then exit)
    th = threading.Thread(target=serve, args=("127.0.0.1", port, True), daemon=True)
    th.start()
    time.sleep(0.2)  # give server time to bind

    send_dict("127.0.0.1", port, fmt)
    th.join(timeout=5)

    out = capsys.readouterr().out
    assert "received format" in out

