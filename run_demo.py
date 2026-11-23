"""Run this file in Air to start the local demo."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import webbrowser

if __name__ == "__main__":
    handler = partial(SimpleHTTPRequestHandler, directory=str(Path(__file__).resolve().parent))
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        url = f"http://127.0.0.1:{server.server_port}/"
        print(f"Flappy Rivals: {url}", flush=True)
        webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
