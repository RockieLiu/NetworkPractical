# server.py
from __future__ import annotations
import argparse
import socket
import sys
from typing import Optional
from protocol import recv_object
from serialization import Format


def serve(host: str, port: int, once: bool = False) -> None:
    """Start a TCP server. If once=True, handle a single client and exit."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        # reuse address for quick restarts
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(5)
        actual_host, actual_port = srv.getsockname()
        print(f"[server] listening on {actual_host}:{actual_port}", flush=True)

        def handle_client(conn: socket.socket, addr: tuple) -> None:
            try:
                fmt, obj = recv_object(conn)
                print(f"[server] received format={Format(fmt).name} from {addr}")
                print(f"[server] payload: {obj}")
            except Exception as exc:  # noqa: BLE001
                print(f"[server] error: {exc}", file=sys.stderr)
            finally:
                try:
                    conn.close()
                except Exception:  # noqa: BLE001
                    pass

        try:
            while True:
                conn, addr = srv.accept()
                handle_client(conn, addr)
                if once:
                    break
        except KeyboardInterrupt:
            print("\n[server] shutting down...")


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Simple dict echo server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--once", action="store_true", help="Handle a single client then exit.")
    args = parser.parse_args(argv)
    serve(args.host, args.port, once=args.once)


if __name__ == "__main__":
    main()

