import json
import socket
import threading
import queue


class TCPLogSender:
    def __init__(self, host="127.0.0.1", port=6000):
        self.host = host
        self.port = port
        self.q = queue.Queue()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def send(self, data: dict):
        print(f"Network data: {data}")
        """Queue the data for async sending."""
        self.q.put(data)

    def _worker(self):
        """Background thread that sends queued log entries."""
        sock = None
        while True:
            data = self.q.get()
            if data is None:
                break
            try:
                if sock is None:
                    sock = socket.create_connection((self.host, self.port))
                message = json.dumps(data) + "\n"
                sock.sendall(message.encode("utf-8"))
            except Exception as e:
                sock = None
