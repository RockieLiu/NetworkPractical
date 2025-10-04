# client.py
from __future__ import annotations
import argparse
import socket
from typing import Optional, Dict, Any
from protocol import send_object
from serialization import Format


def build_sample_dict() -> Dict[str, Any]:
    return {
        "user": "alice",
        "score": 98,
        "skills": ["Python", "Networking", "JSON/XML"],
        "active": True,
    }


def send_dict(host: str, port: int, fmt: Format) -> None:
    data = build_sample_dict()
    with socket.create_connection((host, port), timeout=10) as sock:
        send_object(sock, data, fmt)
    print(f"[client] sent dict using {fmt.name} to {host}:{port}")


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Simple dict client.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--format", choices=["pickle", "json", "xml"], default="json")
    args = parser.parse_args(argv)

    fmt_map = {"pickle": Format.PICKLE, "json": Format.JSON, "xml": Format.XML}
    send_dict(args.host, args.port, fmt_map[args.format])


if __name__ == "__main__":
    main()

