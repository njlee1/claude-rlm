"""
IPC Server for sub_query() communication.

The RLM subprocess sandbox needs to call back into the parent process
to make LLM API calls (sub_query). This module provides a TCP-based
IPC server that:

1. Parent starts a ThreadingTCPServer on localhost (random port)
2. Subprocess connects via socket, sends JSON request with 4-byte length prefix
3. Parent handles request (calls the sub_query callback), sends JSON response
4. Subprocess receives response and continues execution

This pattern is adapted from the original RLM repo's ThreadingLMServer.
"""

import json
import socketserver
import struct
import threading
from typing import Callable, Optional


class IPCServer:
    """TCP-based IPC server for sub_query communication.

    Takes a callback function instead of a reference to ClaudeRLM,
    enabling dependency inversion and testability.

    Usage:
        def my_sub_query(prompt, context_slice=None):
            return "response from LLM"

        with IPCServer(my_sub_query) as server:
            port = server.port
            # ... launch subprocess that connects to port ...

    Args:
        sub_query_fn: Callable that takes (prompt, context_slice) and returns str.
    """

    def __init__(self, sub_query_fn: Callable[[str, Optional[str]], str]):
        self._sub_query_fn = sub_query_fn
        self._server: Optional[socketserver.ThreadingTCPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._port: int = 0

    @property
    def port(self) -> int:
        """The port the server is listening on. 0 if not started."""
        return self._port

    def start(self) -> int:
        """Start the IPC server. Returns the port number."""
        sub_query_fn = self._sub_query_fn  # Capture for handler closure

        class SubQueryHandler(socketserver.StreamRequestHandler):
            def handle(self):
                try:
                    # Read 4-byte length prefix
                    length_bytes = self.rfile.read(4)
                    if len(length_bytes) < 4:
                        return
                    msg_len = struct.unpack("!I", length_bytes)[0]

                    # Read the JSON request
                    data = self.rfile.read(msg_len)
                    request = json.loads(data.decode("utf-8"))

                    prompt = request.get("prompt", "")
                    context_slice = request.get("context_slice")

                    # Call the sub_query function
                    response_text = sub_query_fn(prompt, context_slice)

                    # Send response back with 4-byte length prefix
                    resp_bytes = json.dumps({"result": response_text}).encode("utf-8")
                    self.wfile.write(struct.pack("!I", len(resp_bytes)))
                    self.wfile.write(resp_bytes)
                    self.wfile.flush()
                except Exception as e:
                    try:
                        err = json.dumps({"error": str(e)}).encode("utf-8")
                        self.wfile.write(struct.pack("!I", len(err)))
                        self.wfile.write(err)
                        self.wfile.flush()
                    except Exception:
                        pass

        self._server = socketserver.ThreadingTCPServer(
            ("127.0.0.1", 0), SubQueryHandler
        )
        self._port = self._server.server_address[1]

        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True
        )
        self._thread.start()

        return self._port

    def stop(self) -> None:
        """Stop the IPC server."""
        if self._server is not None:
            self._server.shutdown()
            self._server = None
            self._thread = None
            self._port = 0

    def __enter__(self) -> "IPCServer":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop()
